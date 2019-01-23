"""
	SAME_POS    = open/close leg value is same as combo
	OPEN_POS    = open
	CLOSE_POS   = close
	UNKNOWN_POS = unknown
"""


(SAME_POS, OPEN_POS, CLOSE_POS, UNKNOWN_POS) = range(4)


class Contract(object):
    def __init__(self, symbol="", security_type="", currency="USD", exchange="ISLAND", contract_id=0, strike=0.0,
                 last_trade_date_or_contract_month="", right="", multiplier="", primary_exchange="", local_symbol="",
                 trading_class="", include_expired=False, security_id_type="", security_id="", **kwargs):


        # Common Attributes
        self.currency                           = currency
        self.exchange                           = exchange
        self.security_type                      = security_type
        self.symbol                             = symbol
        self.id                                 = contract_id
        self.last_trade_date_or_contract_month  = last_trade_date_or_contract_month
        self.strike                             = strike # A float is expected
        self.right                              = right
        self.multiplier                         = multiplier
        # Primary exchange should be an actual (ie non-aggregate) exchange that the contract trades on.
        # DO NOT SET TO SMART.
        self.primary_exchange                   = primary_exchange
        self.local_symbol                       = local_symbol
        self.trading_class                      = trading_class
        self.include_expired                    = include_expired
        self.regular_trading_hours              = {}
        self.security_id_type                   = security_id_type	  # CUSIP;SEDOL;ISIN;RIC
        self.security_id                        = security_id

        self.derivative_security_types = []
        #combos
        self.combo_legs_description       = ""        # type: str; received in open order 14 and up for all combos
        self.combo_legs              = None      # type: list<ComboLeg>
        self.delta_neutral_contract = None

        for attribute in vars(self):
            if attribute in kwargs:
                value = kwargs[attribute]
                setattr(self,attribute, value)


    def __str__(self, title="Contract"):
        """
        Produces a human readable representation of a Contract
        :return:
        """
        desc =  "\n{0}\n".format(title)
        desc +=  "--------\n"
        desc += "Contract ID: {0}\n".format(self.id)
        desc += "Symbol: {0}\n".format(self.symbol)
        desc += "Security Type: {0}\n".format(self.security_type)
        desc += "Strike: {0}\n".format(self.strike)
        desc += "Right: {0}\n".format(self.right)
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

        """
        if self.combo_legs:
            for leg in self.combo_legs:
                s += ";" + str(leg)

        if self.delta_neutral_contract:
            s += ";" + str(self.delta_neutral_contract)
        """
        return desc