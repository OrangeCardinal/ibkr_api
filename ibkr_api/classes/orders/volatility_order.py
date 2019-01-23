from ibkr_api.classes.orders.order import Order
from ibkr_api.base.constants import UNSET_DOUBLE, UNSET_INTEGER
class VolatilityOrder(Order):
    def __init__(self):
        super().__init__()

        self.volatility                         = UNSET_DOUBLE  # type: float
        self.volatility_type                    = UNSET_INTEGER  # type: int   # 1=daily, 2=annual
        self.delta_neutral_order_type           = ""
        self.delta_neutral_aux_price            = UNSET_DOUBLE  # type: float
        self.delta_neutral_con_id               = 0
        self.delta_neutral_settling_firm        = ""
        self.delta_neutral_clearing_account     = ""
        self.delta_neutral_clearing_intent      = ""
        self.delta_neutral_open_close           = ""
        self.delta_neutral_short_sale           = False
        self.delta_neutral_short_sale_slot      = 0
        self.delta_neutral_designated_location  = ""
        self.continuous_update                  = False
        self.reference_price_type               = UNSET_INTEGER  # type: int; 1=Average, 2 = BidOrAsk