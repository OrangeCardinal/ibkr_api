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
        self.currency = currency
        self.exchange = exchange
        self.security_type = security_type
        self.symbol = symbol
        self.id = contract_id
        self.last_trade_date_or_contract_month = last_trade_date_or_contract_month
        self.strike = strike # A float is expected
        self.right = right
        self.multiplier = multiplier
        self.primary_exchange = primary_exchange # pick an actual (ie non-aggregate) exchange that the contract trades on.  DO NOT SET TO SMART.
        self.local_symbol = local_symbol
        self.trading_class = trading_class
        self.include_expired = include_expired
        self.security_id_type = security_id_type	  # CUSIP;SEDOL;ISIN;RIC
        self.security_id = security_id

        self.derivative_security_types = []
        #combos
        self.comboLegsDescrip = ""  # type: str; received in open order 14 and up for all combos
        self.comboLegs = None     # type: list<ComboLeg>
        self.deltaNeutralContract = None

        for attribute in vars(self):
            if attribute in kwargs:
                value = kwargs[attribute]
                setattr(self,attribute, value)


    def __str__(self):
        """
        Produces a human readable representation of this object
        :return:
        """
        desc =  "\nContract\n"
        desc +=  "--------\n"
        desc += "ID: {0}\nSymbol: {1}\nSecurity Type: {2}".format(self.id, self.symbol, self.security_type)
        desc += "Exchange: {0}\n".format(self.exchange)
        """
        if self.comboLegs:
            for leg in self.comboLegs:
                s += ";" + str(leg)

        if self.deltaNeutralContract:
            s += ";" + str(self.deltaNeutralContract)
        """
        return desc



class ContractDetails(object):
    def __init__(self):
        self.contract = Contract()
        self.marketName = ""
        self.minTick = 0.
        self.orderTypes = ""
        self.valid_exchanges = ""
        self.price_magnifier = 0
        self.underConId = 0
        self.longName = ""
        self.contractMonth = ""
        self.industry = ""
        self.category = ""
        self.subcategory = ""
        self.timeZoneId = ""
        self.tradingHours = ""
        self.liquidHours = ""
        self.evRule = ""
        self.evMultiplier = 0
        self.mdSizeMultiplier = 0
        self.aggGroup = 0
        self.underSymbol = ""
        self.underSecType = ""
        self.marketRuleIds = ""
        self.security_id_list = None
        self.realExpirationDate = ""
        self.lastTradeTime = ""
        # BOND values
        self.cusip = ""
        self.ratings = ""
        self.descAppend = ""
        self.bondType = ""
        self.couponType = ""
        self.callable = False
        self.putable = False
        self.coupon = 0
        self.convertible = False
        self.maturity = ""
        self.issueDate = ""
        self.next_option_date = ""
        self.next_option_type = ""
        self.next_option_partial = False
        self.notes = ""

    def __str__(self):
        s = ",".join((
            str(self.contract),
            str(self.marketName),
            str(self.minTick),
            str(self.orderTypes),
            str(self.valid_exchanges),
            str(self.price_magnifier),
            str(self.underConId),
            str(self.longName),
            str(self.contractMonth),
            str(self.industry),
            str(self.category),
            str(self.subcategory),
            str(self.timeZoneId),
            str(self.tradingHours),
            str(self.liquidHours),
            str(self.evRule),
            str(self.evMultiplier),
            str(self.mdSizeMultiplier),
            str(self.underSymbol),
            str(self.underSecType),
            str(self.marketRuleIds),
            str(self.aggGroup),
            str(self.security_id_list),
            str(self.realExpirationDate),
            str(self.cusip),
            str(self.ratings),
            str(self.descAppend),
            str(self.bondType),
            str(self.couponType),
            str(self.callable),
            str(self.putable),
            str(self.coupon),
            str(self.convertible),
            str(self.maturity),
            str(self.issueDate),
            str(self.next_option_date),
            str(self.next_option_type),
            str(self.next_option_partial),
            str(self.notes)))
        return s



class ContractDescription(object):
    def __init__(self):
        self.contract = Contract()
        self.derivativeSecTypes = None   # type: list of strings