from ibkr_api.classes.orders.order import Order

class AuctionOrder(Order):
    def __init__(self, contract, action, total_quantity, limit_price, **kwargs):
        super().__init__(kwargs)
        self.action         =   action
        self.total_quantity =   total_quantity
        self.limit_price    =   limit_price
        self.order_type     =   "LMT"
        self.time_in_force  =   "AUC"

        """
           1         order = Order()
    2         order.action = action
    3         order.tif = "AUC"
    4         order.orderType = "MTL"
    5         order.totalQuantity = quantity
    6         order.lmtPrice = price
        """