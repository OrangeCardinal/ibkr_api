from ibkr_api.classes.contracts.contract import Contract
from ibkr_api.classes.enum.security_type import SecurityType

class Option(Contract):
    def __init__(self, symbol, right, strike, expiration, exchange="SMART"):
        super().__init__()
        self.security_type                      = SecurityType.OPTIONS.value
        self.last_trade_date_or_contract_month  = expiration
        self.symbol                             = symbol
        self.right                              = right
        self.strike                             = strike
        self.exchange                           = exchange