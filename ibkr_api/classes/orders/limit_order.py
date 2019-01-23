from ibkr_api.classes.orders.order import Order

class LimitOrder(Order):
    def __init__(self, contract, total_quantity, limit_price, **kwargs):
        super().__init__(kwargs)
        self.order_type = "LMT"

