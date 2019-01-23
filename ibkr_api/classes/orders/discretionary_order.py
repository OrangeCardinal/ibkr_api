from ibkr_api.classes.orders.order import Order

class DiscretionaryOrder(Order):
    def __init__(self, contract, action, total_quantity, limit_price, discretionary_amt, **kwargs):
        super().__init__(kwargs)
        self.contract       =   contract
        self.action         =   action
        self.total_quantity =   total_quantity
        self.limit_price    =   limit_price
        self.order_type     =   "LMT"
        self.discretionary_amt = discretionary_amt

