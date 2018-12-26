class Execution(object):
    """
    A specific execution for an order
    """

    def __init__(self):
        self.id = ""
        self.time =  ""
        self.account_number = ""
        self.exchange =  ""
        self.side = ""
        self.shares = 0.
        self.price = 0.
        self.perm_id = 0
        self.clientId = 0
        self.orderId = 0
        self.liquidation = 0
        self.cumQty = 0.
        self.avgPrice = 0.
        self.orderRef =  ""
        self.evRule =  ""
        self.evMultiplier = 0.
        self.modelCode =  ""
        self.lastLiquidity = 0

    def __str__(self):
        return "ID: %s, Time: %s, Account: %s, Exchange: %s, Side: %s, Shares: %f, Price: %f, PermId: %d, " \
                "ClientId: %d, OrderId: %d, Liquidation: %d, CumQty: %f, AvgPrice: %f, OrderRef: %s, EvRule: %s, " \
                "EvMultiplier: %f, ModelCode: %s, LastLiquidity: %d" % (self.id, self.time, self.account_number,
                                                                        self.exchange, self.side, self.shares, self.price, self.perm_id, self.clientId, self.orderId, self.liquidation,
                                                                        self.cumQty, self.avgPrice, self.orderRef, self.evRule, self.evMultiplier, self.modelCode, self.lastLiquidity)