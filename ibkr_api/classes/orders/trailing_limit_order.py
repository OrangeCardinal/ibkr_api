from ibkr_api.classes.orders.order import Order

class TrailingLimitOrder(Order):
    def __init__(self, contract, total_quantity, limit_price, trail_stop_price, trailing_percent, **kwargs):
        super().__init__(**kwargs)
        self.contract       =   contract
        self.order_type     =   "LMT" #TRAILLIMIT?
        self.total_quantity =   total_quantity
        self.limit_price    =   limit_price
        self.trail_stop_price = trail_stop_price
        self.trailing_percent = trailing_percent            # type: float