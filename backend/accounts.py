import json
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
from backend.database import write_account, read_account, write_log
from backend.market import get_share_price

load_dotenv(override=True)

INITIAL_BALANCE = 10_000.0
SPREAD = 0.002

class Transection(BaseModel):
    symbol: str
    quantity: int
    price: float
    timestamp: str
    rationale: str

    def total(self) -> float:
        return self.quantity * self.price
    
    def __repr__(self):
        return f"{abs(self.quantity)} shares of {self.symbol} at {self.price} each."

class Account(BaseModel):
    name: str
    balance: float = INITIAL_BALANCE
    strategy: str
    holdings: dict = {str: int}
    transections: list = [Transection]
    portfolio_value_time_series: list[tuple[str, float]]

    @classmethod
    def get(cls, name: str):
        fields = read_account(name)
        if fields is None:
            fields = {
                "name": name.lower(),
                "balance": INITIAL_BALANCE,
                "strategy": "",
                "holdings": {},
                "transections": [],
                "portfolio_value_time_series": [],
            }
            write_account(name, fields)
        return cls(**fields)

    def save(self):
        write_account(self.name.lower(), self.model_dump())

    def reset(self, strategy: str = ""):
        self.balance = INITIAL_BALANCE
        self.strategy = strategy
        self.holdings = {}
        self.transections = []
        self.portfolio_value_time_series = []
        self.save()

    def deposit(self, amount: float):
        """Deposit funds into the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        print(f"Deposited ${amount}. New balance: ${self.balance}")
        self.save()

    def withdraw(self, amount: float):
        """Withdraw funds from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal.")
        self.balance -= amount
        print(f"Withdrew ${amount}. New balance: ${self.balance}")
        self.save()


    def buy_shares(self, symbol: str, quantity: int, rationale: str = ""):
        """Buy shares of a stock."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        price = get_share_price(symbol)
        total_cost = price * quantity * (1 + SPREAD)
        if total_cost > self.balance:
            raise ValueError("Insufficient funds to buy shares.")
        self.balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        transection = Transection(
            symbol=symbol,
            quantity=quantity,
            price=price,
            timestamp=datetime.now().isoformat(),
            rationale=rationale,
        )
        self.transections.append(transection)
        print(f"Bought {quantity} shares of {symbol} at ${price} each. Total cost: ${total_cost}. New balance: ${self.balance}")
        self.save()
        write_log(self.name, "account", f"Bought {quantity} of {symbol}")
        return "Completed. Latest details:\n" + self.report()

    def sell_shares(self, symbol: str, quantity: int, rationale: str = ""):
        """Sell shares of a stock."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            raise ValueError("Insufficient shares to sell.")
        price = get_share_price(symbol)
        total_revenue = price * quantity * (1 - SPREAD)
        self.balance += total_revenue
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        transection = Transection(
            symbol=symbol,
            quantity=-quantity,
            price=price,
            timestamp=datetime.now().isoformat(),
            rationale=rationale,
        )
        self.transections.append(transection)
        print(f"Sold {quantity} shares of {symbol} at ${price} each. Total revenue: ${total_revenue}. New balance: ${self.balance}")
        self.save()
        write_log(self.name, "account", f"Sold {quantity} of {symbol}")
        return "Completed. Latest details:\n" + self.report()

    def calculate_portfolio_value(self) -> float:
        """Calculate the total value of the portfolio (cash + holdings)."""
        total_value = self.balance
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
        return total_value

    def calculate_profit_loss(self, portfolio_value: float):
        """ Calculate profit or loss from the initial spend. """
        initial_spend = sum(transaction.total() for transaction in self.transactions)
        return portfolio_value - initial_spend - self.balance

    def get_holdings(self):
        """ Report the current holdings of the user. """
        return self.holdings

    def get_profit_loss(self):
        """ Report the user's profit or loss at any point in time. """
        return self.calculate_profit_loss()

    def list_transactions(self):
        """ List all transactions made by the user. """
        return [transaction.model_dump() for transaction in self.transactions]

    def report(self) -> str:
        """ Return a json string representing the account.  """
        portfolio_value = self.calculate_portfolio_value()
        self.portfolio_value_time_series.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), portfolio_value))
        self.save()
        pnl = self.calculate_profit_loss(portfolio_value)
        data = self.model_dump()
        data["total_portfolio_value"] = portfolio_value
        data["total_profit_loss"] = pnl
        write_log(self.name, "account", "Retrieved account details")
        return json.dumps(data)
    
    def get_strategy(self) -> str:
        """ Return the strategy of the account """
        write_log(self.name, "account", "Retrieved strategy")
        return self.strategy
    
    def change_strategy(self, strategy: str) -> str:
        """ At your discretion, if you choose to, call this to change your investment strategy for the future """
        self.strategy = strategy
        self.save()
        write_log(self.name, "account", "Changed strategy")
        return "Changed strategy"