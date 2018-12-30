class Execution(object):
    """
    A specific execution for an order
    """

    def __init__(self):
        self.id                 = ""

        self.account_number     = ""
        self.datetime           = ""
        self.exchange           = ""
        self.price              = 0.
        self.side               = ""
        self.shares             = 0.
        self.perm_id            = 0
        self.client_id          = 0
        self.order_id           = 0
        self.liquidation        = 0
        self.quantity           = 0.
        self.average_price      = 0.
        self.order_reference    =  ""
        self.ev_rule            = ""
        self.ev_multiplier      = 0.
        self.model_code          =  ""
        self.last_liquidity      = 0
        
        self.contract       = None


    def to_csv(self):
        fields = [self.id, self.contract.id]
        return ",".join(fields)
        
    def __str__(self):
        desc  = "Execution Information\n"
        desc += "---------------------\n"
        desc += "ID: {0}\n".format(self.id)
        desc += "Datetime: {0}\n".format(self.datetime)
        desc += "Order ID: {0}\n".format(self.order_id)
        desc += "Order Ref: {0}\n".format(self.order_reference)
        desc += "Last Liquidity: {0}\n".format(self.last_liquidity)
        desc += "Liquidation: {0}\n".format(self.liquidation)
        desc += "Price: {0}\n".format(self.price)
        desc += "Average Price: {0}\n".format(self.average_price)
        desc += "Side: {0}\n".format(self.side)
        
        if self.contract:
            desc += "\n{0}".format(str(self.contract))
        return desc
