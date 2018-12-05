"""
Extracts data from messages and returns the appropriate class(es)

"""

from base.messages import Messages
from classes.contracts.contract import Contract
from classes.contracts.contract_details import ContractDetails
from classes.order import Order
from classes.execution import Execution

from classes.bar import Bar
from classes.tick_type import TickType

import logging
import time

logger = logging.getLogger(__name__)


class MessageParser(object):
    def __init__(self):
        self.server_version = 147

    @staticmethod
    def commission_report(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        commission_report = {
            'execute_id':bytearray(fields[2]).decode(),
            'commission':float(fields[3]),
            'currency':bytearray(fields[4]).decode(),
            'realized_pnl':float(fields[5]),
            'yield':float(fields[6]),
            'yield_redemption_date':bytearray(fields[7]).decode()
        }
        return message_id, request_id, commission_report

    @staticmethod
    def contract_data(fields):
        contract = Contract()
        
        version = fields[0]
        request_id = int(fields[1])
        contract.symbol = bytearray(fields[2]).decode() 
        contract.security_type = bytearray(fields[3]).decode()
        #self.readLastTradeDate(fields, contract, False) ???
        contract.strike = float(fields[4])
        contract.right = bytearray(fields[5]).decode()
        contract.exchange = bytearray(fields[6]).decode()
        contract.currency = bytearray(fields[7]).decode()
        contract.local_symbol = bytearray(fields[8]).decode()
        contract.market_name = bytearray(fields[9]).decode()          # New to contract
        contract.trading_class = bytearray(fields[10]).decode()
        contract.id = int(fields[11])
        contract.min_tick = float(fields[12])                     # New to contract
        contract.md_size_multiplier = int(fields[13])
        contract.multiplier  = bytearray(fields[14]).decode()
        contract.order_types = bytearray(fields[15]).decode()
        contract.valid_exchanges = bytearray(fields[16]).decode()
        contract.price_magnifier = int(fields[17])
        contract.under_contract_id = int(fields[18])
        contract.long_name = bytearray(fields[19]).decode()
        contract.primary_exchange = bytearray(fields[20]).decode()
        contract.contract_month = bytearray(fields[21]).decode()
        contract.industry = bytearray(fields[22]).decode()
        contract.category = bytearray(fields[23]).decode()
        contract.sub_category = bytearray(fields[24]).decode()
        contract.time_zone_id = bytearray(fields[25]).decode()
        contract.trading_hours = bytearray(fields[26]).decode()
        contract.liquid_hours =  bytearray(fields[27]).decode()
        contract.ev_rule = bytearray(fields[28]).decode()
        contract.ev_multiplier = int(fields[29])

        """
        Not yet ported
        secIdListCount = int(fields[])
        if secIdListCount > 0:
            contract.secIdList = []
            for _ in range(secIdListCount):
                tagValue = TagValue()
                tagValue.tag :bytearray(fields[]).decode()
                tagValue.value :bytearray(fields[]).decode()
                contract.secIdList.append(tagValue)

        if self.server_version >= MIN_SERVER_VER_AGG_GROUP:
            contract.aggGroup = int(fields[])

        if self.server_version >= MIN_SERVER_VER_UNDERLYING_INFO:
            contract.underSymbol :bytearray(fields[]).decode()
            contract.underSecType :bytearray(fields[]).decode()

        if self.server_version >= MIN_SERVER_VER_MARKET_RULES:
            contract.marketRuleIds :bytearray(fields[]).decode()

        if self.server_version >= MIN_SERVER_VER_REAL_EXPIRATION_DATE:
            contract.realExpirationDate :bytearray(fields[]).decode()
        """

    @staticmethod
    def bond_contract_data(fields):

        contract = Contract()
        message_id = int(fields[0])
        version = int(fields[1])
        request_id = int(fields[2])
        contract.symbol = bytearray(fields[3]).decode()
        contract.security_type = bytearray(fields[4]).decode()
        contract.cusip = bytearray(fields[5]).decode()
        contract.coupon = int(fields[6])
        #self.readLastTradeDate(fields, contract, True)
        contract.issueDate = bytearray(fields[7]).decode()
        contract.ratings = bytearray(fields[8]).decode()
        contract.bondType = bytearray(fields[9]).decode()
        contract.couponType = bytearray(fields[10]).decode()
        contract.convertible = fields[11]
        contract.callable =  fields[12]
        contract.putable = fields[13]
        contract.descAppend = bytearray(fields[14]).decode()
        contract.exchange = bytearray(fields[15]).decode()
        contract.currency = bytearray(fields[16]).decode()
        contract.marketName = bytearray(fields[17]).decode()
        contract.tradingClass = bytearray(fields[18]).decode()
        contract.id = int(fields[19])
        contract.min_tick = float(fields[20])
        contract.mdSizeMultiplier = int(fields[21])
        contract.orderTypes = bytearray(fields[22]).decode()
        contract.validExchanges = bytearray(fields[23]).decode()
        contract.nextOptionDate = bytearray(fields[24]).decode()  # ver 2 field
        contract.nextOptionType = bytearray(fields[25]).decode()  # ver 2 field
        contract.nextOptionPartial = fields[26]  # ver 2 field
        contract.notes = bytearray(fields[27]).decode()  # ver 2 field
        contract.longName = bytearray(fields[28]).decode()
        contract.evRule = bytearray(fields[29]).decode()
        contract.evMultiplier = int(fields[30])
        secIdListCount = int(fields[31])
        if secIdListCount > 0:
            contract.security_id_list = []
            for _ in range(secIdListCount):
                tagValue = {
                    'tag' :bytearray(fields[32]).decode(),
                    'value' :bytearray(fields[33]).decode()
                }
                contract.security_id_list.append(tagValue)

        contract.aggGroup = int(fields[34])
        contract.marketRuleIds = bytearray(fields[35]).decode()


    @staticmethod
    def current_time(fields):
        """
        Parse data from the current_time response message

        Message Fields
        0 - Message ID
        1 - Request ID
        2 - Current Time (seconds since epoch)

        :param message: API Response message
        :returns: (request_id:int, timestamp)
        """
        request_id = int(message['fields'][1])
        timestamp = time.ctime(int(message['fields'][2]))
        return request_id, timestamp

    @staticmethod
    def family_codes(fields):
        fields = message['fields']

        num_family_codes = int(fields[0])
        family_codes = []
        field_index = 1
        for i in range(num_family_codes):
            data = {}
            data['account_id'] = bytearray(fields[field_index]).decode()
            data['family_code'] = bytearray(fields[field_index+1]).decode()
            field_index += 2
            family_codes.append(data)
        return family_codes

    @staticmethod
    def historical_data(fields):
        """

        :param message:
        :return: Message ID, Request ID, Bar Data
        """
        bars = []
        fields = message['fields']
        message_id = int(fields[0])
        request_id = int(fields[1])
        start_date = fields[2]
        end_date   = fields[3]
        bar_count = int(fields[4])
        current_bar = 1
        bar_index = 5

        while current_bar <= bar_count:
            bar = Bar()
            bar.date = str(fields[bar_index]) # TODO: Make a proper date
            bar.open = float(fields[bar_index+1])
            bar.high = float(fields[bar_index+2])
            bar.low = float(fields[bar_index+3])
            bar.close = float(fields[bar_index+4])
            bar.volume = fields[bar_index+5]
            bar.average = fields[bar_index+6]
            bar.bar_count = fields[bar_index+7]
            bar_index += 8
            current_bar += 1
            bars.append(bar)

        return message_id, request_id, bars
    
    @staticmethod
    def info_message(fields):
        """
        Message Fields
        0 - Message ID
        1 - Request ID
        2 - Ticker ID (~Contract ID , -1 No Ticker associated)
        3 - Info Code
        4 - Info
        :param message:
        :return:
        """
        fields = message['fields']
        ticker_id = int(fields[2])
        info_code = int(fields[3])
        text      = bytearray(fields[4]).decode()
        return ticker_id, info_code, text

    def managed_accounts(self, fields):
        accounts = []  # List of Accounts to Return
        print(fields)
        return accounts


    @staticmethod
    def market_data_type(fields):
        fields = message['fields']
        data = {
            'message_id':int(fields[0]),
            'request_id':int(fields[1]),
            'market_data_type':bytearray(fields[2]).decode()
        }
        return data


    @staticmethod
    def market_depth_l2(fields):
        fields = message['fields']
        data = {
            'message_id':int(fields[0]),
            'request_id':int(fields[1]),
            'position':int(fields[2]),
            'market_maker':bytearray(fields[3]).decode(),
            'operation':int(fields[4]),
            'side':int(fields[5]),
            'price':float(fields[6]),
            'size':int(fields[7]),
            'is_smart_depth':bool(fields[8])
            }
        
        return data

    @staticmethod
    def order_bound(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        api_client_id = int(fields[2])
        api_order_id  = int(fields[3])
        return message_id, request_id, api_client_id, api_order_id

    @staticmethod
    def reroute_market_data_request(fields):
        fields = message['fields']
        data = {
            'request_id':int(fields[0]),
            'contract_id':int(fields[1]),
            'exchange':bytearray(fields[2]).decode()
        }
        return data
    
    @staticmethod
    def reroute_market_depth_request(fields):
        fields = message['fields']
        data = {
            'request_id':int(fields[0]),
            'contract_id':int(fields[1]),
            'exchange':bytearray(fields[2]).decode()
        }
        return data

    @staticmethod
    def scanner_data(fields):
        fields = message['fields']

        message_id = int(fields[0])
        request_id = int(fields[1])
        number_of_elements = int(fields[2])
        index = 1
        field_index = 0
        results = []
        while index <= number_of_elements:
            data = {}
            contract = Contract()
            data['rank'] = int(fields[field_index])
            contract.id = int(fields[field_index+1])
            contract.symbol = bytearray(fields[field_index+2]).decode()
            contract.security_type = bytearray(fields[field_index+3]).decode()
            contract.last_trade_date_or_contract_month= bytearray(fields[field_index+4]).decode()
            contract.strike= int(fields[field_index+5])
            contract.right= bytearray(fields[field_index+6]).decode()
            contract.exchange= bytearray(fields[field_index+7]).decode()
            contract.currency= bytearray(fields[field_index+8]).decode()
            contract.local_symbol= bytearray(fields[field_index+9]).decode()
            contract.market_name= bytearray(fields[field_index+10]).decode()
            contract.trading_class= bytearray(fields[field_index+11]).decode()

            data['contract'] = contract
            data['distance'] = fields[field_index+12]
            data['benchmark'] = fields[field_index+13]
            data['projection'] = fields[field_index+14]
            data['legs_str'] = fields[field_index+15]
            field_index += 16
            results.append(data)
            index += 1
        return message_id,request_id,results

    @staticmethod
    def soft_dollar_tiers(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        num_tiers = int(fields[2])
        field_index = 3
        tiers = []
        for i in range(num_tiers):
            tier = {
                'name':bytearray(fields[field_index]).decode(),
                'value':bytearray(fields[field_index+1]).decode(),
                'display_name':bytearray(fields[field_index+2]).decode()
            }
            field_index += 3
            tiers.append(tier)
        return message_id, request_id, tiers

    @staticmethod
    def symbol_samples(fields):
        fields = message['fields']

        request_id = int(fields[1])
        num_samples = int(fields[2])
        field_index = 3
        contracts = []
        for index in range(num_samples):
            contract = Contract()
            contract.id = int(fields[field_index])
            contract.symbol = bytearray(fields[field_index+1]).decode()
            contract.security_type = bytearray(fields[field_index+2]).decode()
            contract.primary_exchange = bytearray(fields[field_index+3]).decode()
            contract.currency = bytearray(fields[field_index+4]).decode()

            num_security_types = int(fields[field_index+5])
            field_index += 6
            for j in range(num_security_types):
                derivative_security_type = str(fields[field_index])
                contract.derivative_security_types.append(derivative_security_type)
                field_index += 1

            contracts.append(contract)

        return request_id, contracts

    @staticmethod
    def tick_price(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_type = int(fields[2])
        price = float(fields[3])
        size = int(fields[4])
        attr_mask = int(fields[5])

        # attrib = TickAttrib()
        attributes ={
            'can_auto_execute' : attr_mask & 1 != 0,
            'past_limit' : attr_mask & 2 != 0 ,
            'pre_open': attr_mask & 4 != 0
        }

        # process ver 2 fields
        size_tick_type = TickType.NOT_SET
        if TickType.BID == tick_type:
            size_tick_type = TickType.BID_SIZE
        elif TickType.ASK == tick_type:
            size_tick_type = TickType.ASK_SIZE
        elif TickType.LAST == tick_type:
            size_tick_type = TickType.LAST_SIZE
        elif TickType.DELAYED_BID == tick_type:
            size_tick_type = TickType.DELAYED_BID_SIZE
        elif TickType.DELAYED_ASK == tick_type:
            size_tick_type = TickType.DELAYED_ASK_SIZE
        elif TickType.DELAYED_LAST == tick_type:
            size_tick_type = TickType.DELAYED_LAST_SIZE

        if size_tick_type != TickType.NOT_SET:
            pass


    @staticmethod
    def order_status(fields):
        info = {
            'message_id': int(fields[0]),
            'order_id' : int(fields[1]),
            'status' : bytearray(fields[2]).decode(),
            'filled' : float(fields[3]),
            'remaining' : float(fields[4]),
            'average_fill_price':float(fields[5]),
            'perm_id':int(fields[6]),
            'parent_id':int(fields[7]),
            'last_fill_price':int(fields[8]),
            'client_id':int(fields[9]),
            'why_held':bytearray(fields[10]).decode(),
            'market_cap_price':float(fields[11]),
        }
        return info


    @staticmethod
    def open_order(fields):

        message_id = int(fields[0])
        message_version = int(fields[1])


        order = Order()

        order.order_id = int(fields[2])

        contract = Contract()
        contract.id                                = int(fields[3])
        contract.symbol                            = bytearray(fields[4]).decode()
        contract.security_type                     = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month = bytearray(fields[6]).decode()
        contract.strike                            = float(fields[7])
        contract.right                             = bytearray(fields[8]).decode()
        contract.multiplier                        = bytearray(fields[9]).decode()
        contract.exchange                          = bytearray(fields[10]).decode()
        contract.currency = bytearray(fields[11]).decode()
        contract.localSymbol = bytearray(fields[12]).decode()  # ver 2 field
        contract.tradingClass = bytearray(fields[13]).decode()

        # read order fields
        order = Order()
        order.action = bytearray(fields[14]).decode()
        order.totalQuantity = float(fields[15])
        order.orderType :bytearray(fields[16]).decode()
        order.lmtPrice = fields[17]
        #        order.lmtPrice = decode(float, fields, SHOW_UNSET)
        order.auxPrice = fields[18]
        #    order.auxPrice = decode(float, fields, SHOW_UNSET)
        order.tif = bytearray(fields[17]).decode()
        order.ocaGroup = bytearray(fields[18]).decode()
        order.account = bytearray(fields[19]).decode()
        order.openClose = bytearray(fields[20]).decode()

        order.origin = int(fields[21])

        order.orderRef = bytearray(fields[22]).decode()
        order.clientId = int(fields[23])
        order.permId = int(fields[24])

        order.outsideRth = fields[25]
        order.hidden = fields[26]
        order.discretionaryAmt = float(fields[28])
        order.goodAfterTime = bytearray(fields[29]).decode()  # ver 5 field

        _sharesAllocation = bytearray(fields[30]).decode()  # deprecated ver 6 field

        order.faGroup = bytearray(fields[31]).decode()  # ver 7 field
        order.faMethod = bytearray(fields[32]).decode()  # ver 7 field
        order.faPercentage = bytearray(fields[33]).decode()  # ver 7 field
        order.faProfile = bytearray(fields[34]).decode()  # ver 7 field

        order.modelCode = bytearray(fields[35]).decode()

        order.goodTillDate = bytearray(fields[36]).decode()  # ver 8 field

        order.rule80A = bytearray(fields[37]).decode()  # ver 9 field
        order.percentOffset = fields[38]
        #order.percentOffset = decode(float, fields, SHOW_UNSET)  # ver 9 field
        order.settlingFirm = bytearray(fields[39]).decode()  # ver 9 field
        order.shortSaleSlot = int(fields[])  # ver 9 field
        order.designatedLocation = bytearray(fields[40]).decode()  # ver 9 field
        order.exemptCode = int(fields[41])
        order.auctionStrategy = int(fields[42])
        order.startingPrice = float(fields[43])
        order.stockRefPrice = float(fields[44])
        order.delta = float(fields[45])
        order.stockRangeLower = float(fields[45])
        order.stockRangeUpper = float(fields[46])
        order.displaySize = float(fields[47])


        order.blockOrder = int(fields[48]) == 1
        order.sweepToFill = int(fields[49]) == 1
        order.allOrNone = int(fields[50]) == 1
        order.minQty = int(fields[51])
        order.ocaType = int(fields[52])
        order.eTradeOnly = int(fields[53]) == 1
        order.firmQuoteOnly = int(fields[54]) == 1
        order.nbboPriceCap = float(fields[55])

        order.parentId = int(fields[56])
        order.triggerMethod = int(fields[57])

        order.volatility = float(fields[58])
        order.volatilityType = int(fields[59])
        order.deltaNeutralOrderType = bytearray(fields[59]).decode()  # ver 11 field (had a hack for ver 11)
        order.deltaNeutralAuxPrice = float(fields[60])

        if order.deltaNeutralOrderType:
            order.deltaNeutralConId = int(fields[61])
            order.deltaNeutralSettlingFirm = bytearray(fields[62]).decode()
            order.deltaNeutralClearingAccount = bytearray(fields[63]).decode()
            order.deltaNeutralClearingIntent = bytearray(fields[64]).decode()
            order.deltaNeutralOpenClose = bytearray(fields[65]).decode()
            order.deltaNeutralShortSale = int(fields[66])
            order.deltaNeutralShortSaleSlot = int(fields[67])
            order.deltaNeutralDesignatedLocation = bytearray(fields[68]).decode()

        order.continuousUpdate = int(fields[69]) == 1
        order.referencePriceType = int(fields[70])
        order.trailStopPrice = float(fields[71])
        order.trailingPercent = float(fields[72])

        order.basisPoints = float(fields[73])
        order.basisPointsType = int(fields[74])
        contract.comboLegsDescrip = bytearray(fields[75]).decode()  # ver 14 field

        if version >= 29:
            comboLegsCount = int(fields[])

            if comboLegsCount > 0:
                contract.comboLegs = []
                for _ in range(comboLegsCount):
                    comboLeg = ComboLeg()
                    comboLeg.conId = int(fields[])
                    comboLeg.ratio = int(fields[])
                    comboLeg.action :bytearray(fields[]).decode()
                    comboLeg.exchange :bytearray(fields[]).decode()
                    comboLeg.openClose = int(fields[])
                    comboLeg.shortSaleSlot = int(fields[])
                    comboLeg.designatedLocation :bytearray(fields[]).decode()
                    comboLeg.exemptCode = int(fields[])
                    contract.comboLegs.append(comboLeg)

            orderComboLegsCount = int(fields[])
            if orderComboLegsCount > 0:
                order.orderComboLegs = []
                for _ in range(orderComboLegsCount):
                    orderComboLeg = OrderComboLeg()
                    orderComboLeg.price = decode(float, fields, SHOW_UNSET)
                    order.orderComboLegs.append(orderComboLeg)

        if version >= 26:
            smartComboRoutingParamsCount = int(fields[])
            if smartComboRoutingParamsCount > 0:
                order.smartComboRoutingParams = []
                for _ in range(smartComboRoutingParamsCount):
                    tagValue = TagValue()
                    tagValue.tag :bytearray(fields[]).decode()
                    tagValue.value :bytearray(fields[]).decode()
                    order.smartComboRoutingParams.append(tagValue)


        order.scaleInitLevelSize = decode(int, fields, SHOW_UNSET)
        order.scaleSubsLevelSize = decode(int, fields, SHOW_UNSET)


        order.scalePriceIncrement = decode(float, fields, SHOW_UNSET)  # ver 15 field

        if version >= 28 and order.scalePriceIncrement != UNSET_DOUBLE \
                and order.scalePriceIncrement > 0.0:
            order.scalePriceAdjustValue = decode(float, fields, SHOW_UNSET)
            order.scalePriceAdjustInterval = decode(int, fields, SHOW_UNSET)
            order.scaleProfitOffset = decode(float, fields, SHOW_UNSET)
            order.scaleAutoReset = decode(bool, fields)
            order.scaleInitPosition = decode(int, fields, SHOW_UNSET)
            order.scaleInitFillQty = decode(int, fields, SHOW_UNSET)
            order.scaleRandomPercent = decode(bool, fields)

        if version >= 24:
            order.hedgeType :bytearray(fields[]).decode()
            if order.hedgeType:
                order.hedgeParam :bytearray(fields[]).decode()

        if version >= 25:
            order.optOutSmartRouting = decode(bool, fields)

        order.clearingAccount :bytearray(fields[]).decode()  # ver 19 field
        order.clearingIntent :bytearray(fields[]).decode()  # ver 19 field

        if version >= 22:
            order.notHeld = decode(bool, fields)

        if version >= 20:
            deltaNeutralContractPresent = decode(bool, fields)
            if deltaNeutralContractPresent:
                contract.deltaNeutralContract = Contract()
                contract.deltaNeutralContract.conId = int(fields[])
                contract.deltaNeutralContract.delta = float(fields[])
                contract.deltaNeutralContract.price = float(fields[])

        if version >= 21:
            order.algoStrategy :bytearray(fields[]).decode()
            if order.algoStrategy:
                algoParamsCount = int(fields[])
                if algoParamsCount > 0:
                    order.algoParams = []
                    for _ in range(algoParamsCount):
                        tagValue = TagValue()
                        tagValue.tag :bytearray(fields[]).decode()
                        tagValue.value :bytearray(fields[]).decode()
                        order.algoParams.append(tagValue)

        if version >= 33:
            order.solicited = decode(bool, fields)

        orderState = OrderState()

        order.whatIf = decode(bool, fields)  # ver 16 field

        orderState.status :bytearray(fields[]).decode()  # ver 16 field
        if self.server_version >= MIN_SERVER_VER_WHAT_IF_EXT_FIELDS:
            orderState.initMarginBefore :bytearray(fields[]).decode()
            orderState.maintMarginBefore :bytearray(fields[]).decode()
            orderState.equityWithLoanBefore :bytearray(fields[]).decode()
            orderState.initMarginChange :bytearray(fields[]).decode()
            orderState.maintMarginChange :bytearray(fields[]).decode()
            orderState.equityWithLoanChange :bytearray(fields[]).decode()

        orderState.initMarginAfter :bytearray(fields[]).decode()  # ver 16 field
        orderState.maintMarginAfter :bytearray(fields[]).decode()  # ver 16 field
        orderState.equityWithLoanAfter :bytearray(fields[]).decode()  # ver 16 field

        orderState.commission = decode(float, fields, SHOW_UNSET)  # ver 16 field
        orderState.minCommission = decode(float, fields, SHOW_UNSET)  # ver 16 field
        orderState.maxCommission = decode(float, fields, SHOW_UNSET)  # ver 16 field
        orderState.commissionCurrency :bytearray(fields[]).decode()  # ver 16 field
        orderState.warningText :bytearray(fields[]).decode()  # ver 16 field

        if version >= 34:
            order.randomizeSize = decode(bool, fields)
            order.randomizePrice = decode(bool, fields)

        if self.server_version >= MIN_SERVER_VER_PEGGED_TO_BENCHMARK:
            if order.orderType == "PEG BENCH":
                order.referenceContractId = int(fields[])
                order.isPeggedChangeAmountDecrease = decode(bool, fields)
                order.peggedChangeAmount = float(fields[])
                order.referenceChangeAmount = float(fields[])
                order.referenceExchangeId :bytearray(fields[]).decode()

            conditionsSize = int(fields[])
            if conditionsSize > 0:
                order.conditions = []
                for _ in range(conditionsSize):
                    conditionType = int(fields[])
                    condition = order_condition.Create(conditionType)
                    condition.decode(fields)
                    order.conditions.append(condition)

                order.conditionsIgnoreRth = decode(bool, fields)
                order.conditionsCancelOrder = decode(bool, fields)

            order.adjustedOrderType :bytearray(fields[]).decode()
            order.triggerPrice = float(fields[])
            order.trailStopPrice = float(fields[])
            order.lmtPriceOffset = float(fields[])
            order.adjustedStopPrice = float(fields[])
            order.adjustedStopLimitPrice = float(fields[])
            order.adjustedTrailingAmount = float(fields[])
            order.adjustableTrailingUnit = int(fields[])

        if self.server_version >= MIN_SERVER_VER_SOFT_DOLLAR_TIER:
            name :bytearray(fields[]).decode()
            value :bytearray(fields[]).decode()
            displayName :bytearray(fields[]).decode()
            order.softDollarTier = SoftDollarTier(name, value, displayName)

        if self.server_version >= MIN_SERVER_VER_CASH_QTY:
            order.cashQty = float(fields[])

        if self.server_version >= MIN_SERVER_VER_AUTO_PRICE_FOR_HEDGE:
            order.dontUseAutoPriceForHedge = decode(bool, fields)

        if self.server_version >= MIN_SERVER_VER_ORDER_CONTAINER:
            order.isOmsContainer = decode(bool, fields)

        # self.response_handler.openOrder(order.order_id, contract, order, orderState)

    @staticmethod
    def portfolio_value(fields):
        message_id = int(fields[0])
        version = int(fields[1])

        # read contract fields
        contract = Contract()
        contract.id = int(fields[2])
        contract.symbol = bytearray(fields[3]).decode()
        contract.security_type                     = bytearray(fields[4]).decode()
        contract.last_trade_date_or_contract_month = bytearray(fields[5]).decode()
        contract.strike                            = float(fields[6])
        contract.right                             = bytearray(fields[7]).decode()
        contract.multiplier                        = bytearray(fields[8]).decode()
        contract.primaryExchange                   = bytearray(fields[9]).decode()
        contract.currency = bytearray(fields[10]).decode()
        contract.localSymbol = bytearray(fields[11]).decode()  # ver 2 field
        contract.tradingClass = bytearray(fields[12]).decode()

        portfolio_info = {
            'position' : float(fields[13]),
            'market_price':float(fields[14]),
            'average_cost':float(fields[15]),
            'unrealized_pnl':float(fields[16]),
            'realized_pnl':float(fields[17]),
            'account_name':bytearray(fields[18]).decode()
        }
        return contract, portfolio_info

    def execution_data(self, fields):
        message_id = int(fields[0])
        version    = self.server_version
        request_id = int(fields[1])
        order_id   = int(fields[2])

        # Parse contract information
        contract = Contract()
        contract.id = int(fields[3])
        contract.symbol = bytearray(fields[4]).decode()
        contract.security_type = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month = bytearray(fields[6]).decode()
        contract.strike        = float(fields[7])
        contract.right         = bytearray(fields[8]).decode()
        contract.multiplier    = bytearray(fields[9]).decode()
        contract.exchange      = bytearray(fields[10]).decode()
        contract.currency      = bytearray(fields[11]).decode()
        contract.local_symbol  = bytearray(fields[12]).decode()
        contract.trading_class = bytearray(fields[13]).decode()

        # decode execution fields
        execution = Execution()
        execution.order_id   = order_id
        execution.execId     = bytearray(fields[14]).decode()
        execution.time       = bytearray(fields[15]).decode()
        execution.acctNumber = bytearray(fields[16]).decode()
        execution.exchange   = bytearray(fields[17]).decode()
        execution.side       = bytearray(fields[18]).decode()
        execution.shares     = float(fields[19])


        execution.price = float(fields[20])
        execution.permId = int(fields[21])
        execution.clientId = int(fields[22])
        execution.liquidation = int(fields[23])


        execution.cumQty = float(fields[[24]])
        execution.avgPrice = float(fields[25])
        execution.orderRef = bytearray(fields[26]).decode()
        execution.evRule = bytearray(fields[27]).decode()
        execution.evMultiplier = float(fields[28])
        execution.modelCode = bytearray(fields[29]).decode()
        execution.lastLiquidity = int(fields[30])


    @staticmethod
    def historical_data_update(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        bar = Bar()
        bar.bar_count = int(fields[2])
        bar.date      = bytearray(fields[3]).decode()
        bar.open      = float(fields[4])
        bar.close     = float(fields[5])
        bar.high      = float(fields[6])
        bar.low       = float(fields[7])
        bar.average   = float(fields[8])
        bar.volume    = int(fields[9])

        return message_id, request_id, bar

    @staticmethod
    def real_time_bar(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        bar = Bar()
        bar.time = int(fields[2])
        bar.open = float(fields[3])
        bar.high = float(fields[4])
        bar.low = float(fields[5])
        bar.close = float(fields[6])
        bar.volume = int(fields[])
        bar.wap = float(fields[])
        bar.count = int(fields[])

    def processTickOptionComputationMsg(self, fields):
        optPrice = None
        pvDividend = None
        gamma = None
        vega = None
        theta = None
        undPrice = None

        message_id = int(fields[0])
        version = int(fields[1])
        request_id = int(fields[2])
        tick_typeInt = int(fields[3])

        impliedVol = float(fields[4])
        delta = float(fields[5])

        if impliedVol < 0:  # -1 is the "not computed" indicator
            impliedVol = None
        if delta == -2:  # -2 is the "not computed" indicator
            delta = None

        if version >= 6 or \
                tick_typeInt == TickType.MODEL_OPTION or \
                tick_typeInt == TickType.DELAYED_MODEL_OPTION:

            optPrice = float(fields[])
            pvDividend = float(fields[])

            if optPrice == -1:  # -1 is the "not computed" indicator
                optPrice = None
            if pvDividend == -1:  # -1 is the "not computed" indicator
                pvDividend = None

        if version >= 6:
            gamma = float(fields[])
            vega = float(fields[])
            theta = float(fields[])
            undPrice = float(fields[])

            if gamma == -2:  # -2 is the "not yet computed" indicator
                gamma = None
            if vega == -2:  # -2 is the "not yet computed" indicator
                vega = None
            if theta == -2:  # -2 is the "not yet computed" indicator
                theta = None
            if undPrice == -1:  # -1 is the "not computed" indicator
                undPrice = None

    @staticmethod
    def delta_neutral_validation(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        #deltaNeutralContract = DeltaNeutralContract() #TODO: decide if we should have a DeltaNeutralContract
        delta_neutral_contract = Contract()

        delta_neutral_contract.contract_id = int(fields[2])
        delta_neutral_contract.delta       = float(fields[3])
        delta_neutral_contract.price       = float(fields[4])
        return message_id, request_id, delta_neutral_contract


    @staticmethod
    def position_data(fields):
        message_id = int(fields[0])
        version = int(fields[1])

        account = bytearray(fields[2]).decode()

        # decode contract fields
        contract = Contract()
        contract.id = int(fields[3])
        contract.symbol = bytearray(fields[4]).decode()
        contract.security_type                     = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month = bytearray(fields[6]).decode()
        contract.strike                            = float(fields[7])
        contract.right       = bytearray(fields[8]).decode()
        contract.multiplier  = bytearray(fields[9]).decode()
        contract.exchange    = bytearray(fields[10]).decode()
        contract.currency    = bytearray(fields[11]).decode()
        contract.localSymbol = bytearray(fields[12]).decode()
        contract.tradingClass = bytearray(fields[13]).decode()

        position = float(fields[14])


        avgCost = 0.
        if version >= 3:
            avgCost = float(fields[])

        # self.response_handler.position(account, contract, position, avgCost)

    @staticmethod
    def position_multi(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        account = bytearray(fields[2]).decode()

        # decode contract fields
        contract = Contract()
        contract.id = int(fields[3])
        contract.symbol = bytearray(fields[4]).decode()
        contract.security_type = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month = bytearray(fields[6]).decode()
        contract.strike = float(fields[7])
        contract.right = bytearray(fields[8]).decode()
        contract.multiplier = bytearray(fields[9]).decode()
        contract.exchange = bytearray(fields[10]).decode()
        contract.currency = bytearray(fields[11]).decode()
        contract.local_symbol = bytearray(fields[12]).decode()
        contract.trading_class = bytearray(fields[13]).decode()

        position = float(fields[14])
        average_cost = float(fields[15])
        modelCode :bytearray(fields[16]).decode()

        return

    def processSecurityDefinitionOptionParameterMsg(self, fields):
        message_id = int(fields[0])

        request_id = int(fields[1])
        exchange :bytearray(fields[]).decode()
        underlyingConId = int(fields[])
        tradingClass :bytearray(fields[]).decode()
        multiplier :bytearray(fields[]).decode()

        expCount = int(fields[])
        expirations = set()
        for _ in range(expCount):
            expiration :bytearray(fields[]).decode()
            expirations.add(expiration)

        strikeCount = int(fields[])
        strikes = set()
        for _ in range(strikeCount):
            strike = float(fields[])
            strikes.add(strike)



    def processSecurityDefinitionOptionParameterEndMsg(self, fields):
        message_id = int(fields[0])

        request_id = int(fields[1])


    def processSmartComponents(self, fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        n = int(fields[])

        smartComponentMap = []
        for _ in range(n):
            smartComponent = SmartComponent()
            smartComponent.bitNumber = int(fields[])
            smartComponent.exchange :bytearray(fields[]).decode()
            smartComponent.exchangeLetter :bytearray(fields[]).decode()
            smartComponentMap.append(smartComponent)

    def processTickReqParams(self, fields):
        message_id = int(fields[0])
        tickerId = int(fields[])
        minTick = float(fields[])
        bboExchange :bytearray(fields[]).decode()
        snapshotPermissions = int(fields[])

    def processMktDepthExchanges(self, fields):
        message_id = int(fields[0])
        depthMktDataDescriptions = []
        nDepthMktDataDescriptions = int(fields[])

        if nDepthMktDataDescriptions > 0:
            for _ in range(nDepthMktDataDescriptions):
                desc = DepthMktDataDescription()
                desc.exchange :bytearray(fields[]).decode()
                desc.security_type :bytearray(fields[]).decode()
                if self.server_version >= MIN_SERVER_VER_SERVICE_DATA_TYPE:
                    desc.listingExch :bytearray(fields[]).decode()
                    desc.serviceDataType :bytearray(fields[]).decode()
                    desc.aggGroup = int(fields[])
                else:
                    int(fields[])  # boolean notSuppIsL2
                depthMktDataDescriptions.append(desc)

    def processTickNews(self, fields):
        message_id = int(fields[0])
        tickerId = int(fields[])
        timeStamp = int(fields[])
        providerCode :bytearray(fields[]).decode()
        articleId :bytearray(fields[]).decode()
        headline :bytearray(fields[]).decode()
        extraData :bytearray(fields[]).decode()

    def processNewsProviders(self, fields):
        message_id = int(fields[0])
        newsProviders = []
        nNewsProviders = int(fields[])
        if nNewsProviders > 0:
            for _ in range(nNewsProviders):
                provider = NewsProvider()
                provider.code :bytearray(fields[]).decode()
                provider.name :bytearray(fields[]).decode()
                newsProviders.append(provider)


    @staticmethod
    def news_articles(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        article = {
        'type' :  int(fields[2]),
        'text' : bytearray(fields[3]).decode()
        }
        return message_id, request_id, article

    @staticmethod
    def historical_news(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        time = bytearray(fields[2]).decode()
        providerCode = bytearray(fields[3]).decode()
        articleId = bytearray(fields[4]).decode()
        headline = bytearray(fields[5]).decode()

    def processHistoricalNewsEnd(self, fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        has_more = decode(bool, fields)

    @staticmethod
    def histogram_data(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        num_points = int(fields[2])
        field_index = 3
        histogram = []
        for index in range(num_points):
            data_point = {
                'price': float(fields[field_index]),
                'count': int(fields[field_index + 1])
            }
            field_index += 2
            histogram.append(data_point)
        return message_id, request_id, histogram


    def processMarketRuleMsg(self, fields):
        message_id = int(fields[0])
        marketRuleId = int(fields[])

        nPriceIncrements = int(fields[])
        priceIncrements = []

        if nPriceIncrements > 0:
            for _ in range(nPriceIncrements):
                prcInc = PriceIncrement()
                prcInc.lowEdge = float(fields[])
                prcInc.increment = float(fields[])
                priceIncrements.append(prcInc)


    def pnl(self, fields):
        """

        :param fields: Message Fields
        :returns: message_id, request_id, pnl
        """
        message_id = int(fields[0])
        request_id = int(fields[1])
        pnl = {
            'daily'      : float(fields[2]),
            'unrealized' : float(fields[3]),
            'realized'   : float(fields[4])
        }
        return message_id, request_id, pnl



    @staticmethod
    def pnl_single(fields):
        """
        Gets the profit and loss for a single position
        :param fields:
        :return:
        """

        message_id = int(fields[0])
        request_id = int(fields[1])
        pnl = {
            'position':int(fields[2]),
            'daily': float(fields[3]),
            'unrealized':float(fields[4]),
            'realized':float(fields[5]),
            'value':float(fields[6])
        }
        return message_id, request_id, pnl

    @staticmethod
    def historical_ticks(self, fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_count = int(fields[2])
        field_index = 3

        ticks = []

        for _ in range(tick_count):
            historical_tick = {
                'message_id': int(fields[0]),
                'time':int(fields[field_index]),
                'price':float(fields[field_index+1]),
                'size':int(fields[field_index+2])
            }
            field_index += 3
            ticks.append(historical_tick)

        done = int(fields[field_index]) == 1


    @staticmethod
    def historical_ticks_bid_ask(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_count = int(fields[2])
        field_index = 3

        ticks = []

        for _ in range(tick_count):
            mask = int(fields[field_index + 1])
            historical_tick_bid_ask = {
                'time':int(fields[field_index]),
                'mask':int(fields[field_index+1]),
                'ask_past_high': mask & 1 != 0,
                'bid_past_low': mask & 2 != 0,
                'price_bid' : fields[field_index+2],
                'price_ask': float(fields[field_index+3]),
                'size_bid': int(fields[field_index+4]),
                'size_ask': int(fields[field_index+5])
            }
            ticks.append(historical_tick_bid_ask)

        done = int(fields[field_index]) == 1

    @staticmethod
    def historical_ticks_last(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_count = int(fields[2])

        ticks = []

        for _ in range(tick_count):
            historicalTickLast = HistoricalTickLast()
            historicalTickLast.time = int(fields[])
            mask = int(fields[])
            tickAttribLast = TickAttribLast()
            tickAttribLast.pastLimit = mask & 1 != 0
            tickAttribLast.unreported = mask & 2 != 0
            historicalTickLast.tickAttribLast = tickAttribLast
            historicalTickLast.price = float(fields[])
            historicalTickLast.size = int(fields[])
            historicalTickLast.exchange :bytearray(fields[]).decode()
            historicalTickLast.specialConditions :bytearray(fields[]).decode()
            ticks.append(historicalTickLast)

        done = decode(bool, fields)


    @staticmethod
    def tick_by_tick(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_type  = int(fields[2])
        time       = int(fields[3])

        if tick_type == 0:
            # None
            pass
        elif tick_type == 1 or tick_type == 2:
            # Last or AllLast
            price = float(fields[4])
            size = int(fields[5])
            mask = int(fields[6])

            tickAttribLast = TickAttribLast()
            tickAttribLast.pastLimit = mask & 1 != 0
            tickAttribLast.unreported = mask & 2 != 0
            exchange = bytearray(fields[7]).decode()
            specialConditions = bytearray(fields[8]).decode()
        elif tick_type == 3:
            # BidAsk
            bidPrice = float(fields[4])#float(fields[])
            askPrice = float(fields[5])#float(fields[])
            bidSize = float(fields[6])#int(fields[])
            askSize = int(fields[7])#int(fields[])
            mask = int(fields[8])#int(fields[])
            tickAttribBidAsk = TickAttribBidAsk()
            tickAttribBidAsk.bidPastLow = mask & 1 != 0
            tickAttribBidAsk.askPastHigh = mask & 2 != 0


        elif tick_type == 4:
            # MidPoint
            midPoint = float(fields[])
            

    ######################################################################

    def readLastTradeDate(self, fields, contract: ContractDetails, isBond: bool):
        last_trade_date_or_contract_month :bytearray(fields[]).decode()
        if last_trade_date_or_contract_month is not None:
            splitted = last_trade_date_or_contract_month.split()
            if len(splitted) > 0:
                if isBond:
                    contract.maturity = splitted[0]
                else:
                    contract.contract.last_trade_date_or_contract_month = splitted[0]

            if len(splitted) > 1:
                contract.lastTradeTime = splitted[1]

            if isBond and len(splitted) > 2:
                contract.timeZoneId = splitted[2]

    ######################################################################

