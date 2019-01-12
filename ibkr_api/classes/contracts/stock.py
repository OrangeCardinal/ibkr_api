from ibkr_api.classes.contracts.contract import Contract

class Stock(Contract):
    def __init__(self, symbol=None):
        super().__init__()
        
        # Set the Stock Specific Attributes
        self.symbol        = symbol
        self.security_type = 'STK'
        
        # Remove Contract Attributes Not Applicable to a Stock
        del self.last_trade_date_or_contract_month
        del self.strike
        del self.right
        del self.multiplier   # Technically is 1, not sure if that is "logically" more correct than removing it
        
