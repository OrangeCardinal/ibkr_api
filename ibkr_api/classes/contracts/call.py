from ibkr_api.classes.contracts.option import Option

class Call(Option):
    """
    US Call Option Contract
    """
    def __init__(self, symbol, strike, expiration, exchange='SMART'):
        super().__init__(symbol, 'C', strike, expiration, exchange)