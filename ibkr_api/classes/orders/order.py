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
    def __init__(self,**kwargs):
        self.softDollarTier = SoftDollarTier("", "", "")
        # order identifier
        self.order_id  = 0
        self.client_id = 0
        self.perm_id   = 0

        # main order fields
        self.action                 = ""
        self.total_quantity         = 0
        self.order_type             = ""
        self.limit_price            = UNSET_DOUBLE
        self.aux_price              = UNSET_DOUBLE

        # extended order fields
        self.contract               = None # Contract object (if any) associated with the order (
        self.time_in_force          = ""   # "Time in Force" - DAY, GTC, etc.
        self.active_start_time      = ""   # for Good Till Cancelled (GTC) orders
        self.active_stop_time       = ""   # for Good Till Cancelled (GTC) orders
        self.oca_group              = ""   # One cancels all group name
        self.oca_type               = 0    # 1 = CANCEL_WITH_BLOCK, 2 = REDUCE_WITH_BLOCK, 3 = REDUCE_NON_BLOCK
        self.order_ref              = ""
        self.transmit               = True  # if false, order will be created but not transmited
        self.parent_id              = 0     # Parent order Id, to associate Auto STP or TRAIL orders with the original order.
        self.block_order            = False
        self.sweep_to_fill          = False
        self.display_size           = 0
        self.trigger_method         = 0     # 0=Default, 1=Double_Bid_Ask, 2=Last, 3=Double_Last, 4=Bid_Ask, 7=Last_or_Bid_Ask, 8=Mid-point
        self.outside_rth            = False
        self.hidden                 = False
        self.good_after_time        = ""   # Format: 20060505 08:00:00 {time zone}
        self.good_till_date         = ""   # Format: 20060505 08:00:00 {time zone}
        self.rule80A                = ""   # Individual = 'I', Agency = 'A', AgentOtherMember = 'W', IndividualPTIA = 'J', AgencyPTIA = 'U', AgentOtherMemberPTIA = 'M', IndividualPT = 'K', AgencyPT = 'Y', AgentOtherMemberPT = 'N'
        self.all_or_none            = False
        self.min_qty                = UNSET_INTEGER  #type: int
        self.percent_offset                     = UNSET_DOUBLE  # type: float; REL orders only
        self.override_percentage_constraints    = False
        self.trail_stop_price                   = UNSET_DOUBLE  # type: float
        self.trailing_percent                   = UNSET_DOUBLE # type: float; TRAILLIMIT orders only

        # Only used by financial advisers
        self.financial_advisers_group              = ""
        self.financial_advisers_profile            = ""
        self.financial_advisers_method             = ""
        self.financial_advisers_percentage         = ""

        # institutional (ie non-cleared) only
        self.designated_location            = "" #used only when short_sale_slot=2
        self.open_close                     = "O"    # O=Open, C=Close
        self.origin                         = CUSTOMER  # 0=Customer, 1=Firm
        self.short_sale_slot                = 0    # type: int; 1 if you hold the shares, 2 if they will be delivered from elsewhere.  Only for Action=SSHORT
        self.exempt_code                    = -1

        # SMART routing only
        self.discretionary_amt              = 0
        self.e_trade_only                   = True
        self.firm_quote_only                = True
        self.nbbo_price_cap                 = UNSET_DOUBLE  # type: float
        self.opt_out_smart_routing          = False

        # BOX exchange orders only
        self.auctionStrategy                = AUCTION_UNSET # type: int; AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
        self.starting_price                 = UNSET_DOUBLE   # type: float
        self.stock_ref_price                = UNSET_DOUBLE   # type: float
        self.delta                          = UNSET_DOUBLE   # type: float

        # pegged to stock and VOL orders only
        self.stock_range_lower              = UNSET_DOUBLE   # type: float
        self.stock_range_upper              = UNSET_DOUBLE   # type: float

        self.randomize_price                = False
        self.randomize_size                 = False

        # COMBO ORDERS ONLY
        self.basis_points                   = UNSET_DOUBLE  # type: float; EFP orders only
        self.basis_points_type              = UNSET_INTEGER  # type: int;  EFP orders only

        # SCALE ORDERS ONLY
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

        # HEDGE ORDERS
        self.hedge_type                     = "" # 'D' - delta, 'B' - beta, 'F' - FX, 'P' - pair
        self.hedge_param                    = "" # 'beta=X' value for beta hedge, 'ratio=Y' for pair hedge

        # Clearing info
        self.account                        = "" # IB account
        self.settling_firm                   = ""
        self.clearing_account               = ""   #True beneficiary of the order
        self.clearing_intent                = "" # "" (Default), "IB", "Away", "PTA" (PostTrade)

        # ALGO ORDERS ONLY
        self.algorithmic_strategy           = ""

        self.algorithm_parameters           = None    #TagValueList
        self.smart_combo_routing_params     = None  #TagValueList

        self.algoId = ""

        # What-if
        self.what_if = False

        # Not Held
        self.not_held = False
        self.solicited = False

        # models
        self.modelCode = ""

        # order combo legs

        self.order_combo_legs = None  # OrderComboLegListSPtr

        self.order_misc_options = None  # TagValueList

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
        self.conditions_cancel_order = False
        self.conditions_ignore_rth   = False

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


        # Set any attributes that were supplied via keyword arguments
        for key, val in kwargs.items():
            if hasattr(self,key):
                setattr(self,key,val)

    def __str__(self, display_contract=True):
        """
        Produce a human readable description of the Order
        :return:
        """
        desc  = "Order\n"
        desc += "-----\n"
        desc += "Order ID: {0}\n".format(self.order_id)
        desc += "Client ID: {0}\n".format(self.client_id)
        desc += "Perm ID: {0}\n\n".format(self.perm_id)
        desc += "Order Type: {0}\n".format(self.order_type)
        desc += "Action: {0}\n".format(self.action)
        desc += "Total Quantity: {0}\n".format(self.total_quantity)
        desc += "Limit Price: {0}\n".format(self.limit_price)
        desc += "Time in Force: {0}\n".format(self.time_in_force)

        if display_contract and self.contract != None:
            desc += self.contract.__str__('Order - Contract Info')

        if self.order_combo_legs:
            desc += " CMB("
            for leg in self.order_combo_legs:
                desc += str(leg) + ","
            desc += ")"

        if self.conditions:
            desc += " COND("
            for cond in self.conditions:
                desc += str(cond) + ","
            desc += ")"
        return desc
