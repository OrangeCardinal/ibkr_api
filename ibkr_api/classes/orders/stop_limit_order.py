from ibkr_api.classes.orders.order import Order

class StopLimitOrder(Order):
    def __init__(self, action, contract, amount, stop_price, limit_price, **kwargs):
        super().__init__(**kwargs)
        # Order Attributes
        self.action         =   action
        self.contract       =   contract
        self.order_type     =   'STP LMT'
        self.total_quantity =   amount
        self.limit_price    =   limit_price

        # StopLimitOrder Attributes
        self.aux_price      = stop_price