from ibkr_api.classes.orders.order import Order

class MarketIfTouchedOrder(Order):
    """
    Convenience class for a 'Market If Touched' Order
    """
    def __init__(self, action, quantity, touch_price, **kwargs):
        """
        
        :param action: Action to take (E.g. BUY, SELL, etc) 
        :param quantity: Purchase/Sale Quantity
        :param touch_price: The 'If Touched' price 
        :param kwargs: Used to set any other attribute of an Order
        """
        super().__init__(**kwargs)
        self.order_type     =   "MIT"
        self.action         = action
        self.total_quantity = quantity
        self.aux_price      = touch_price