from mcp.server.fastmcp import FastMCP
from .accounts import Account

mcp = FastMCP("accounts_server")

@mcp.tool()
async def get_balance(name: str):
    """Get the cash balance of the given account name.

    Args:
        name: The name of the account holder
    """

    account = Account.get(name)
    return account.balance

@mcp.tool()
async def get_holdings(name: str):
    """Get the holdings of the given account name.

    Args:
        name: The name of the account holder
    """

    account = Account.get(name)
    return account.holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str = ""):
    """Buy shares for the given account name.

    Args:
        name: The name of the account holder
        symbol: The stock symbol to buy
        quantity: The number of shares to buy
        rationale: Optional rationale for the purchase
    """

    account = Account.get(name)
    return account.buy_shares(symbol, quantity, rationale)

@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> float:
    """Sell shares of a stock.

    Args:
        name: The name of the account holder
        symbol: The symbol of the stock
        quantity: The quantity of shares to sell
        rationale: The rationale for the sale and fit with the account's strategy
    """
    return Account.get(name).sell_shares(symbol, quantity, rationale)

@mcp.tool()
async def change_strategy(name: str, strategy: str) -> str:
    """At your discretion, if you choose to, call this to change your investment strategy for the future.

    Args:
        name: The name of the account holder
        strategy: The new strategy for the account
    """
    return Account.get(name).change_strategy(strategy)

@mcp.resource("accounts://accounts_server/{name}")
async def read_account_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{name}")
async def read_strategy_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.get_strategy()



if __name__ == "__main__":
    mcp.run(transport='stdio')
    print("Accounts server is running. Use Ctrl+C to stop.")