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


    def __str__(self, title="Stock"):
        """
        Produces a human readable representation of a Contract
        :return:
        """
        desc =  "\n{0}\n".format(title)
        desc +=  "--------\n"
        desc += "Contract ID: {0}\n".format(self.id)
        desc += "Symbol: {0}\n".format(self.symbol)
        desc += "Security Type: {0}\n".format(self.security_type)
        desc += "Exchange: {0}\n".format(self.exchange)
        desc += "Local Symbol: {0}\n".format(self.local_symbol)


        if len(self.regular_trading_hours) > 0:
            desc += "\nRegular Trading Hours\n"
            desc += "---------------------\n"
            for day in self.regular_trading_hours.keys():
                info = self.regular_trading_hours[day]
                if info['market_open']:
                    desc += "{0}:{1} - {2}:{3}\n".format(info['start_date'],info['start_time'],
                                                       info['end_date'],info['end_time'])
                else:
                    desc += "{0}: Closed\n".format(day)

        return desc
        
