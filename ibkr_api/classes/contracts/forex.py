from ibkr_api.classes.contracts.contract import Contract

class Forex(Contract):
    def __init__(self, currency_pair, exchange="IDEALPRO"):
        super().__init__()
        symbol      = currency_pair[0:3]
        currency    = currency_pair[3:6]

        self.security_type  = 'CASH'
        self.symbol         = symbol
        self.currency       = currency
        self.exchange       = exchange