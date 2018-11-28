from base.constants import UNSET_INTEGER, UNSET_DOUBLE
from classes.soft_dollar_tier import SoftDollarTier

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
        self.permId   = 0

        # main order fields
        self.action = ""
        self.totalQuantity = 0
        self.orderType = ""
        self.lmtPrice      = UNSET_DOUBLE
        self.auxPrice      = UNSET_DOUBLE

        # extended order fields
        self.tif = ""                 # "Time in Force" - DAY, GTC, etc.
        self.active_start_time = ""   # for Good Till Cancelled (GTC) orders
        self.active_stop_time = ""    # for Good Till Cancelled (GTC) orders
        self.ocaGroup = ""            # One cancels all group name
        self.ocaType        = 0       # 1 = CANCEL_WITH_BLOCK, 2 = REDUCE_WITH_BLOCK, 3 = REDUCE_NON_BLOCK
        self.orderRef       = ""
        self.transmit       = True  # if false, order will be created but not transmited
        self.parentId       = 0     # Parent order Id, to associate Auto STP or TRAIL orders with the original order.
        self.blockOrder     = False
        self.sweepToFill    = False
        self.displaySize    = 0
        self.triggerMethod  = 0     # 0=Default, 1=Double_Bid_Ask, 2=Last, 3=Double_Last, 4=Bid_Ask, 7=Last_or_Bid_Ask, 8=Mid-point
        self.outsideRth     = False
        self.hidden         = False
        self.goodAfterTime       = ""   # Format: 20060505 08:00:00 {time zone}
        self.goodTillDate        = ""   # Format: 20060505 08:00:00 {time zone}
        self.rule80A             = ""   # Individual = 'I', Agency = 'A', AgentOtherMember = 'W', IndividualPTIA = 'J', AgencyPTIA = 'U', AgentOtherMemberPTIA = 'M', IndividualPT = 'K', AgencyPT = 'Y', AgentOtherMemberPT = 'N'
        self.allOrNone      = False
        self.minQty         = UNSET_INTEGER  #type: int
        self.percentOffset  = UNSET_DOUBLE  # type: float; REL orders only
        self.overridePercentageConstraints = False
        self.trailStopPrice = UNSET_DOUBLE  # type: float
        self.trailingPercent = UNSET_DOUBLE # type: float; TRAILLIMIT orders only

        # financial advisors only
        self.faGroup              = ""
        self.faProfile            = ""
        self.faMethod             = ""
        self.faPercentage         = ""

        # institutional (ie non-cleared) only
        self.designatedLocation = "" #used only when shortSaleSlot=2
        self.openClose     = "O"    # O=Open, C=Close
        self.origin        = CUSTOMER  # 0=Customer, 1=Firm
        self.shortSaleSlot = 0    # type: int; 1 if you hold the shares, 2 if they will be delivered from elsewhere.  Only for Action=SSHORT
        self.exemptCode    = -1

        # SMART routing only
        self.discretionaryAmt = 0
        self.eTradeOnly       = True
        self.firmQuoteOnly    = True
        self.nbboPriceCap     = UNSET_DOUBLE  # type: float
        self.optOutSmartRouting = False

        # BOX exchange orders only
        self.auctionStrategy = AUCTION_UNSET # type: int; AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
        self.startingPrice   = UNSET_DOUBLE   # type: float
        self.stockRefPrice   = UNSET_DOUBLE   # type: float
        self.delta           = UNSET_DOUBLE   # type: float

        # pegged to stock and VOL orders only
        self.stockRangeLower = UNSET_DOUBLE   # type: float
        self.stockRangeUpper = UNSET_DOUBLE   # type: float

        self.randomizePrice = False
        self.randomizeSize = False

        # VOLATILITY ORDERS ONLY
        self.volatility            = UNSET_DOUBLE  # type: float
        self.volatilityType        = UNSET_INTEGER  # type: int   # 1=daily, 2=annual
        self.deltaNeutralOrderType = ""
        self.deltaNeutralAuxPrice  = UNSET_DOUBLE  # type: float
        self.deltaNeutralConId     = 0
        self.deltaNeutralSettlingFirm = ""
        self.deltaNeutralClearingAccount = ""
        self.deltaNeutralClearingIntent = ""
        self.deltaNeutralOpenClose = ""
        self.deltaNeutralShortSale = False
        self.deltaNeutralShortSaleSlot = 0
        self.deltaNeutralDesignatedLocation = ""
        self.continuousUpdate      = False
        self.referencePriceType    = UNSET_INTEGER  # type: int; 1=Average, 2 = BidOrAsk

        # COMBO ORDERS ONLY
        self.basisPoints     = UNSET_DOUBLE  # type: float; EFP orders only
        self.basisPointsType = UNSET_INTEGER  # type: int;  EFP orders only

        # SCALE ORDERS ONLY
        self.scaleInitLevelSize  = UNSET_INTEGER  # type: int
        self.scaleSubsLevelSize  = UNSET_INTEGER  # type: int
        self.scalePriceIncrement = UNSET_DOUBLE  # type: float
        self.scalePriceAdjustValue = UNSET_DOUBLE  # type: float
        self.scalePriceAdjustInterval = UNSET_INTEGER  # type: int
        self.scaleProfitOffset = UNSET_DOUBLE  # type: float
        self.scaleAutoReset = False
        self.scaleInitPosition = UNSET_INTEGER   # type: int
        self.scaleInitFillQty = UNSET_INTEGER    # type: int
        self.scaleRandomPercent = False
        self.scaleTable = ""

        # HEDGE ORDERS
        self.hedgeType             = "" # 'D' - delta, 'B' - beta, 'F' - FX, 'P' - pair
        self.hedgeParam            = "" # 'beta=X' value for beta hedge, 'ratio=Y' for pair hedge

        # Clearing info
        self.account               = "" # IB account
        self.settlingFirm          = ""
        self.clearingAccount       = ""   #True beneficiary of the order
        self.clearingIntent        = "" # "" (Default), "IB", "Away", "PTA" (PostTrade)

        # ALGO ORDERS ONLY
        self.algoStrategy          = ""

        self.algo_params            = None    #TagValueList
        self.smartComboRoutingParams = None  #TagValueList

        self.algoId = ""

        # What-if
        self.whatIf = False

        # Not Held
        self.notHeld = False
        self.solicited = False

        # models
        self.modelCode = ""

        # order combo legs

        self.orderComboLegs = None  # OrderComboLegListSPtr

        self.orderMiscOptions = None  # TagValueList

        # VER PEG2BENCH fields:
        self.referenceContractId = 0
        self.peggedChangeAmount = 0.
        self.isPeggedChangeAmountDecrease = False
        self.referenceChangeAmount = 0.
        self.referenceExchangeId = ""
        self.adjustedOrderType = ""

        self.triggerPrice = UNSET_DOUBLE
        self.adjusted_stop_price = UNSET_DOUBLE
        self.adjusted_stop_limit_price = UNSET_DOUBLE
        self.adjusted_trailing_amount = UNSET_DOUBLE
        self.adjusted_trailing_unit = 0
        self.lmtPriceOffset = UNSET_DOUBLE

        self.conditions = []  # std::vector<std::shared_ptr<OrderCondition>>
        self.conditionsCancelOrder = False
        self.conditionsIgnoreRth = False

        # ext operator
        self.extOperator = ""

        # native cash quantity
        self.cashQty = UNSET_DOUBLE

        self.mifid2DecisionMaker = ""
        self.mifid2DecisionAlgo = ""
        self.mifid2ExecutionTrader = ""
        self.mifid2ExecutionAlgo = ""

        self.dontUseAutoPriceForHedge = False

        self.isOmsContainer = False

    def __str__(self):
        s = "%s,%d,%s:" % (self.order_id, self.client_id, self.permId)

        s += " %s %s %d@%f" % (
            self.orderType,
            self.action,
            self.totalQuantity,
            self.lmtPrice)

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