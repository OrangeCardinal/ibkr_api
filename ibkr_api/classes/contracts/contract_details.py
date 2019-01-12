from ibkr_api.classes.contracts.contract import Contract


class ContractDetails(object):
    def __init__(self):
        self.contract = Contract()
        self.marketName = ""
        self.minTick = 0.
        self.orderTypes = ""
        self.validExchanges = ""
        self.priceMagnifier = 0
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
        self.secIdList = None
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
        self.nextOptionDate = ""
        self.nextOptionType = ""
        self.nextOptionPartial = False
        self.notes = ""

    def __str__(self):
        s = ",".join((
            str(self.contract),
            str(self.marketName),
            str(self.minTick),
            str(self.orderTypes),
            str(self.validExchanges),
            str(self.priceMagnifier),
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
            str(self.secIdList),
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
            str(self.nextOptionDate),
            str(self.nextOptionType),
            str(self.nextOptionPartial),
            str(self.notes)))
        return s