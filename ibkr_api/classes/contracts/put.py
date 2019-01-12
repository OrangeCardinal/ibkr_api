from ibkr_api.classes.contracts.option import Option

class Put(Option):
    def __init__(self, symbol, strike, expiry):
        super().__init__(symbol, 'C', strike, expiry)