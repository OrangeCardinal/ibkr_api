from ibkr_api.base.constants import UNSET_INTEGER, UNSET_DOUBLE
from ibkr_api.classes.soft_dollar_tier import SoftDollarTier

# enum Origin
(CUSTOMER, FIRM, UNKNOWN) = range(3)

# enum AuctionStrategy
(AUCTION_UNSET, AUCTION_MATCH,
 AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT) = range(4)


class OrderComboLeg(object):
    def __init__(self):
        self.price = UNSET_DOUBLE  # type: float

    def __str__(self):
        return "%f" % self.price


class Order(object):
    def __init__(self):
        self.softDollarTier = SoftDollarTier("", "", "")
        # order identifier
        self.order_id  = 0
        self.client_id = 0
        self.perm_id   = 0

        # main order fields
        self.action = ""
        self.total_quantity = 0
        self.order_type = ""
        self.limit_price      = UNSET_DOUBLE
        self.aux_price      = UNSET_DOUBLE

        # extended order fields
        self.tif = ""                 # "Time in Force" - DAY, GTC, etc.
        self.active_start_time = ""   # for Good Till Cancelled (GTC) orders
        self.active_stop_time = ""    # for Good Till Cancelled (GTC) orders
        self.oca_group = ""            # One cancels all group name
        self.oca_type        = 0       # 1 = CANCEL_WITH_BLOCK, 2 = REDUCE_WITH_BLOCK, 3 = REDUCE_NON_BLOCK
        self.order_ref       = ""
        self.transmit       = True  # if false, order will be created but not transmited
        self.parent_id       = 0     # Parent order Id, to associate Auto STP or TRAIL orders with the original order.
        self.block_order     = False
        self.sweep_to_fill    = False
        self.display_size    = 0
        self.trigger_method  = 0     # 0=Default, 1=Double_Bid_Ask, 2=Last, 3=Double_Last, 4=Bid_Ask, 7=Last_or_Bid_Ask, 8=Mid-point
        self.outside_rth     = False
        self.hidden            = False
        self.good_after_time   = ""   # Format: 20060505 08:00:00 {time zone}
        self.good_till_date    = ""   # Format: 20060505 08:00:00 {time zone}
        self.rule80A           = ""   # Individual = 'I', Agency = 'A', AgentOtherMember = 'W', IndividualPTIA = 'J', AgencyPTIA = 'U', AgentOtherMemberPTIA = 'M', IndividualPT = 'K', AgencyPT = 'Y', AgentOtherMemberPT = 'N'
        self.allOrNone         = False
        self.min_qty         = UNSET_INTEGER  #type: int
        self.percent_offset  = UNSET_DOUBLE  # type: float; REL orders only
        self.override_percentage_constraints = False
        self.trail_stop_price = UNSET_DOUBLE  # type: float
        self.trailing_percent = UNSET_DOUBLE # type: float; TRAILLIMIT orders only

        # Only used by financial advisers
        self.financial_advisers_group              = ""
        self.financial_advisers_profile            = ""
        self.financial_advisers_method             = ""
        self.financial_advisers_percentage         = ""

        # institutional (ie non-cleared) only
        self.designatedLocation    = "" #used only when shortSaleSlot=2
        self.open_close             = "O"    # O=Open, C=Close
        self.origin                = CUSTOMER  # 0=Customer, 1=Firm
        self.shortSaleSlot         = 0    # type: int; 1 if you hold the shares, 2 if they will be delivered from elsewhere.  Only for Action=SSHORT
        self.exemptCode            = -1

        # SMART routing only
        self.discretionary_amt = 0
        self.e_trade_only       = True
        self.firmQuoteOnly    = True
        self.nbboPriceCap     = UNSET_DOUBLE  # type: float
        self.opt_out_smart_routing = False

        # BOX exchange orders only
        self.auctionStrategy = AUCTION_UNSET # type: int; AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
        self.starting_price   = UNSET_DOUBLE   # type: float
        self.stock_ref_price   = UNSET_DOUBLE   # type: float
        self.delta           = UNSET_DOUBLE   # type: float

        # pegged to stock and VOL orders only
        self.stock_range_lower = UNSET_DOUBLE   # type: float
        self.stock_range_upper = UNSET_DOUBLE   # type: float

        self.randomize_price = False
        self.randomize_size = False

        # VOLATILITY ORDERS ONLY
        self.volatility                     = UNSET_DOUBLE  # type: float
        self.volatility_type                = UNSET_INTEGER  # type: int   # 1=daily, 2=annual
        self.delta_neutral_order_type       = ""
        self.delta_neutral_aux_price        = UNSET_DOUBLE  # type: float
        self.delta_neutral_con_id           = 0
        self.delta_neutral_settling_firm    = ""
        self.delta_neutral_clearing_account = ""
        self.delta_neutral_clearing_intent     = ""
        self.delta_neutral_open_close          = ""
        self.delta_neutral_short_sale          = False
        self.delta_neutral_short_sale_slot      = 0
        self.delta_neutral_designated_location = ""
        self.continuous_update               = False
        self.reference_price_type             = UNSET_INTEGER  # type: int; 1=Average, 2 = BidOrAsk

        # COMBO ORDERS ONLY
        self.basis_points     = UNSET_DOUBLE  # type: float; EFP orders only
        self.basis_points_type = UNSET_INTEGER  # type: int;  EFP orders only

        # SCALE ORDERS ONLY
        self.scale_init_level_size       = UNSET_INTEGER  # type: int
        self.scale_subs_level_size       = UNSET_INTEGER  # type: int
        self.scale_price_increment      = UNSET_DOUBLE  # type: float
        self.scale_price_adjust_value    = UNSET_DOUBLE  # type: float
        self.scale_price_adjust_interval = UNSET_INTEGER  # type: int
        self.scale_profit_offset        = UNSET_DOUBLE  # type: float
        self.scale_auto_reset           = False
        self.scale_init_position        = UNSET_INTEGER   # type: int
        self.scale_init_fill_qty         = UNSET_INTEGER    # type: int
        self.scale_random_percent       = False
        self.scaleTable = ""

        # HEDGE ORDERS
        self.hedge_type             = "" # 'D' - delta, 'B' - beta, 'F' - FX, 'P' - pair
        self.hedge_param            = "" # 'beta=X' value for beta hedge, 'ratio=Y' for pair hedge

        # Clearing info
        self.account               = "" # IB account
        self.settlingFirm          = ""
        self.clearing_account       = ""   #True beneficiary of the order
        self.clearing_intent        = "" # "" (Default), "IB", "Away", "PTA" (PostTrade)

        # ALGO ORDERS ONLY
        self.algorithmic_strategy          = ""

        self.algo_params            = None    #TagValueList
        self.smart_combo_routing_params = None  #TagValueList

        self.algoId = ""

        # What-if
        self.what_if = False

        # Not Held
        self.not_held = False
        self.solicited = False

        # models
        self.modelCode = ""

        # order combo legs

        self.orderComboLegs = None  # OrderComboLegListSPtr

        self.orderMiscOptions = None  # TagValueList

        # VER PEG2BENCH fields:
        self.reference_contract_id            = 0
        self.pegged_change_amount             = 0.
        self.is_pegged_change_amount_decrease = False
        self.reference_change_amount          = 0.
        self.reference_exchange_id            = ""
        self.adjusted_order_type                = ""

        self.trigger_price             = UNSET_DOUBLE
        self.adjusted_stop_price       = UNSET_DOUBLE
        self.adjusted_stop_limit_price = UNSET_DOUBLE
        self.adjusted_trailing_amount  = UNSET_DOUBLE
        self.adjusted_trailing_unit    = 0
        self.limit_price_offset        = UNSET_DOUBLE

        self.conditions            = []  # std::vector<std::shared_ptr<OrderCondition>>
        self.conditionsCancelOrder = False
        self.conditionsIgnoreRth   = False

        # ext operator
        self.extOperator = ""

        # native cash quantity
        self.cash_qty = UNSET_DOUBLE

        self.mifid2DecisionMaker = ""
        self.mifid2DecisionAlgo = ""
        self.mifid2ExecutionTrader = ""
        self.mifid2ExecutionAlgo = ""

        self.dont_use_auto_price_for_hedge = False

        self.is_oms_container = False

    def __str__(self):
        s = "%s,%d,%s:" % (self.order_id, self.client_id, self.perm_id)

        s += " %s %s %d@%f" % (
            self.order_type,
            self.action,
            self.total_quantity,
            self.limit_price)

        s += " %s" % self.tif

        if self.orderComboLegs:
            s += " CMB("
            for leg in self.orderComboLegs:
                s += str(leg) + ","
            s += ")"

        if self.conditions:
            s += " COND("
            for cond in self.conditions:
                s += str(cond) + ","
            s += ")"

        return s
