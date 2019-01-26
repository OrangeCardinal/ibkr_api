from ibkr_api.classes.orders.order import Order
from ibkr_api.base.constants import UNSET_INTEGER,UNSET_DOUBLE

class ScaleOrder(Order):
    def __init__(self):
        self.scale_init_level_size          = UNSET_INTEGER
        self.scale_subs_level_size          = UNSET_INTEGER
        self.scale_price_increment          = UNSET_DOUBLE
        self.scale_price_adjust_value       = UNSET_DOUBLE
        self.scale_price_adjust_interval    = UNSET_INTEGER
        self.scale_profit_offset            = UNSET_DOUBLE
        self.scale_auto_reset               = False
        self.scale_init_position            = UNSET_INTEGER
        self.scale_init_fill_qty            = UNSET_INTEGER
        self.scale_random_percent           = False
        self.scale_table = ""