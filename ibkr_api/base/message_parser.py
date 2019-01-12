"""
Extracts data from messages received from the Bridge Connection
and returns it the format message_id, request_id, data

data is usually a dictionary on a given object
"""
from ibkr_api.base.constants import UNSET_DOUBLE
from ibkr_api.classes.contracts.contract         import Contract
from ibkr_api.classes.contracts.contract_details import ContractDetails
from ibkr_api.classes.execution                  import Execution
from ibkr_api.classes.option_chain               import OptionChain
from ibkr_api.classes.order                      import Order
from ibkr_api.classes.order_state                import OrderState

from ibkr_api.classes.bar                        import Bar
from ibkr_api.classes.enum.tick_type             import TickType

from dateutil   import parser as date_parser
from datetime   import date
import pandas   as pd
import logging
import xmltodict
import time

logger = logging.getLogger(__name__)


class MessageParser(object):
    def __init__(self):
        self.server_version = 147

    @staticmethod
    def _parse_ib_date(date_val):
        if date_val:
            print(date_val[:-3])
            print(date_val[-3:])
            date_val = date_parser.parse(date_val)
        return date_val


    @staticmethod
    def commission_report(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        commission_report = {
            'execute_id'            : bytearray(fields[2]).decode(),
            'commission'            : float(fields[3]),
            'currency'              : bytearray(fields[4]).decode(),
            'realized_pnl'          : float(fields[5]),
            'yield'                 : float(fields[6]),
            'yield_redemption_date' : bytearray(fields[7]).decode()
        }
        return message_id, request_id, commission_report


    #TODO: Remove this function? not sure, probably
    @staticmethod
    def _parse_last_trade_or_contract_month(fields, contract: ContractDetails, is_bond: bool):
        last_trade_date_or_contract_month = bytearray(fields[1]).decode()
        if last_trade_date_or_contract_month is not None:
            field_parts = last_trade_date_or_contract_month.split()
            if len(field_parts) > 0:
                if is_bond:
                    contract.maturity = field_parts[0]
                else:
                    contract.contract.last_trade_date_or_contract_month = field_parts[0]

            if len(field_parts) > 1:
                contract.lastTradeTime = field_parts[1]

            if is_bond and len(field_parts) > 2:
                contract.timeZoneId = field_parts[2]

    @staticmethod
    def contract_data(fields):
        """
        Parses the contract_data message returned by the BridgeConnection
        :param fields:
        :return:
        """
        contract = Contract()

        message_id                                  = int(fields[0])
        message_version                             = fields[1]
        request_id                                  = int(fields[2])
        contract.symbol                             = bytearray(fields[3]).decode()
        contract.security_type                      = bytearray(fields[4]).decode()
        contract.last_trade_date_or_contract_month  = MessageParser._parse_ib_date(bytearray(fields[5]).decode())

        contract.strike                 = float(fields[6])
        contract.right                  = bytearray(fields[7]).decode()
        contract.exchange               = bytearray(fields[8]).decode()
        contract.currency               = bytearray(fields[9]).decode()
        contract.local_symbol           = bytearray(fields[10]).decode()
        contract.market_name            = bytearray(fields[11]).decode()
        contract.trading_class          = bytearray(fields[12]).decode()
        contract.id                     = int(fields[13])
        contract.min_tick               = float(fields[14])
        contract.md_size_multiplier     = int(fields[15])
        contract.multiplier             = bytearray(fields[16]).decode()
        contract.order_types            = bytearray(fields[17]).decode()
        contract.valid_exchanges        = bytearray(fields[18]).decode()
        contract.price_magnifier        = int(fields[19])
        contract.under_contract_id      = int(fields[20])
        contract.long_name              = bytearray(fields[21]).decode()
        contract.primary_exchange       = bytearray(fields[22]).decode()
        contract.contract_month         = bytearray(fields[23]).decode()
        contract.industry               = bytearray(fields[24]).decode()
        contract.category               = bytearray(fields[25]).decode()
        contract.sub_category           = bytearray(fields[25]).decode()
        contract.time_zone_id           = bytearray(fields[26]).decode()
        contract.trading_hours          = bytearray(fields[27]).decode()

        # Parse Regular Trading Hour Information
        contract.regular_trading_hours  = bytearray(fields[28]).decode()
        if contract.regular_trading_hours:
            regular_trading_hours = {}
            daily_schedule = contract.regular_trading_hours.split(';')
            for date_hours in daily_schedule:
                parts = date_hours.split(':')
                regular_trading_hours[parts[0]] = parts[1:]
            contract.regular_trading_hours = regular_trading_hours
        contract.ev_rule                = bytearray(fields[29]).decode()
        contract.ev_multiplier          = bytearray(fields[30]).decode()

        #security_id_list_count          = int(fields[31])
        #print("Security: {0}".format(security_id_list_count)) #TODO: Fix here down

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


        contract.aggGroup = int(fields[])


        contract.underSymbol = bytearray(fields[]).decode()
        contract.underSecType = bytearray(fields[]).decode()


        contract.marketRuleIds = bytearray(fields[]).decode()
        contract.realExpirationDate = bytearray(fields[]).decode()
        """
        return request_id, message_id, contract

    @staticmethod
    def bond_contract_data(fields):

        contract = Contract()
        message_id = int(fields[0])
        version = int(fields[1])
        request_id = int(fields[2])
        contract.symbol = bytearray(fields[3]).decode()
        contract.security_type                      = bytearray(fields[4]).decode()
        contract.cusip                              = bytearray(fields[5]).decode()
        contract.coupon                             = int(fields[6])
        contract.last_trade_date_or_contract_month  = MessageParser._parse_ib_date(bytearray(fields[7]).decode())
        contract.issue_date                         = bytearray(fields[8]).decode()
        contract.ratings                            = bytearray(fields[9]).decode()
        contract.bond_type                          = bytearray(fields[10]).decode()
        contract.couponType                         = bytearray(fields[11]).decode()
        contract.convertible                        = fields[12]
        contract.callable                           =  fields[13]
        contract.putable                            = fields[14]
        contract.descAppend                         = bytearray(fields[15]).decode()
        contract.exchange                           = bytearray(fields[16]).decode()
        contract.currency                           = bytearray(fields[17]).decode()
        contract.marketName                         = bytearray(fields[18]).decode()
        contract.tradingClass                       = bytearray(fields[19]).decode()
        contract.id                                 = int(fields[20])
        contract.min_tick                           = float(fields[21])
        contract.mdSizeMultiplier                   = int(fields[22])
        contract.orderTypes                         = bytearray(fields[23]).decode()
        contract.valid_exchanges                    = bytearray(fields[24]).decode()
        contract.next_option_date                   = bytearray(fields[25]).decode()
        contract.next_option_type                   = bytearray(fields[26]).decode()
        contract.next_option_partial                = fields[27]
        contract.notes                              = bytearray(fields[28]).decode()
        contract.long_name                          = bytearray(fields[29]).decode()
        contract.evRule                             = bytearray(fields[30]).decode()
        contract.evMultiplier                       = int(fields[31])
        secIdListCount                              = int(fields[32])
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

        return message_id, request_id, contract

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
        message_id = int(fields[0])
        request_id = int(fields[1])
        timestamp  = time.ctime(int(fields[2]))
        return message_id, request_id, timestamp

    @staticmethod
    def family_codes(fields):
        """

        :param fields:
        :return: Family Codes
        """
        message_id          = int(fields[0])
        num_family_codes    = int(fields[1])
        family_codes        = []
        field_index         = 2
        for i in range(num_family_codes):
            data = {}
            data['account_id']  = bytearray(fields[field_index]).decode()
            data['family_code'] = bytearray(fields[field_index+1]).decode()
            field_index += 2
            family_codes.append(data)
        return family_codes

    @staticmethod
    def historical_data(fields):
        """
        :param fields: The previously parsed message fields
        :return: Message ID, Request ID, Data
        """
        bars = []
        message_id = int(fields[0])
        request_id = int(fields[1])
        data       = {
            'start_date' : fields[2],
            'end_date'   : fields[3],
            'bar_count'  : int(fields[4])
        }
        df_data     = {'date':[],'open':[],'high':[],'low':[],'close':[]}
        current_bar = 1
        bar_index   = 5

        #TODO: Fix the date code here (it is losing info)
        while current_bar <= data['bar_count']:
            # Create the Bar class and append it to the list of Bars
            bar                 = Bar()
            bar_date            = bytearray(fields[bar_index]).decode()
            year, month, day    = int(bar_date[0:4]), int(bar_date[4:6]), int(bar_date[6:8])
            bar.date            = date(year, month, day)
            bar.open            = float(fields[bar_index+1])
            bar.high            = float(fields[bar_index+2])
            bar.low             = float(fields[bar_index+3])
            bar.close           = float(fields[bar_index+4])
            bar.volume          = int(fields[bar_index+5])
            bar.average         = float(fields[bar_index+6])
            bar.bar_count       = int(fields[bar_index+7])
            bars.append(bar)

            # Prepare the data for the data frame
            df_data['date'].append(bar.date)
            df_data['open'].append(bar.open)
            df_data['high'].append(bar.high)
            df_data['low'].append(bar.low)
            df_data['close'].append(bar.close)

            # Update indexes
            bar_index          += 8
            current_bar        += 1


        data['data_frame'] = pd.DataFrame(data=df_data)
        data['bars'] = bars
        return message_id, request_id, data
    
    @staticmethod
    def info_message(fields):
        """
        Information Messages. The bridge sends these whenever it wants to communicate with the client.

        # Message Fields
        0 - Message ID
        1 - Request ID
        2 - Ticker ID (~Contract ID , -1 No Ticker associated)
        3 - Info Code
        4 - Info
        :param fields:
        :return:
        """
        message_id = int(fields[0])
        request_id = int(fields[1])
        info = {
            'ticker_id' : int(fields[2]),
            'code'      : int(fields[3]),
            'text'      : bytearray(fields[4]).decode()
        }
        return message_id, request_id, info

    @staticmethod
    def managed_accounts(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        account    = bytearray(fields[2]).decode()

        #accounts = []  # List of Accounts to Return
        return message_id, request_id, account


    @staticmethod
    def market_data_type(fields):
        data = {
            'message_id':int(fields[0]),
            'request_id':int(fields[1]),
            'market_data_type':bytearray(fields[2]).decode()
        }
        return data


    @staticmethod
    def market_depth_l2(fields):

        data = {
            'message_id'        : int(fields[0]),
            'request_id'        : int(fields[1]),
            'position'          : int(fields[2]),
            'market_maker'      : bytearray(fields[3]).decode(),
            'operation'         : int(fields[4]),
            'side'              : int(fields[5]),
            'price'             : float(fields[6]),
            'size'              : int(fields[7]),
            'is_smart_depth'    : bool(fields[8])
            }
        
        return data

    @staticmethod
    def next_valid_id(fields):
        """
        Parses the next_valid_id message from the Bridge
        Contains the next request id that can be used
        :param fields:
        :return:
        """
        message_id      = int(fields[0])
        request_id      = int(fields[1])
        next_id         = int(fields[2])
        return message_id, request_id, next_id

    @staticmethod
    def order_bound(fields):
        message_id      = int(fields[0])
        request_id      = int(fields[1])
        api_client_id   = int(fields[2])
        api_order_id    = int(fields[3])
        return message_id, request_id, api_client_id, api_order_id

    @staticmethod
    def reroute_market_data_request(fields):

        data = {
            'request_id'    : int(fields[0]),
            'contract_id'   : int(fields[1]),
            'exchange'      : bytearray(fields[2]).decode()
        }
        return data
    
    @staticmethod
    def reroute_market_depth_request(fields):

        data = {
            'request_id'    : int(fields[0]),
            'contract_id'   : int(fields[1]),
            'exchange'      : bytearray(fields[2]).decode()
        }
        return data

    @staticmethod
    def scanner_data(fields):
        """
        Parses the scanner_data message and returns properly formatted data
        
        :param fields: 
        :return: 
        """


        message_id          = int(fields[0])
        request_id          = int(fields[1])
        #TODO: figure out what fields[2] represents
        number_of_elements  = int(fields[3])
        field_index         = 4
        results             = []
        for i in range(number_of_elements):
            data                                        = {}
            contract                                    = Contract()
            data['rank']                                = int(fields[field_index])

            contract.id                                 = int(fields[field_index+1])
            data['contract_id']                         = contract.id

            contract.symbol                             = bytearray(fields[field_index+2]).decode()
            data['symbol']                     = contract.symbol

            contract.security_type                      = bytearray(fields[field_index+3]).decode()
            data['security_type']                       = contract.security_type

            contract.last_trade_date_or_contract_month  = bytearray(fields[field_index+4]).decode()

            contract.strike                             = int(fields[field_index+5])
            data['strike']                              = contract.strike

            contract.right                              = bytearray(fields[field_index+6]).decode()
            data['right']                               = contract.right

            contract.exchange                           = bytearray(fields[field_index+7]).decode()
            contract.currency                           = bytearray(fields[field_index+8]).decode()
            contract.local_symbol                       = bytearray(fields[field_index+9]).decode()
            contract.market_name                        = bytearray(fields[field_index+10]).decode()
            contract.trading_class                      = bytearray(fields[field_index+11]).decode()

            data['contract']     = contract
            data['distance']     = fields[field_index+12]
            data['benchmark']    = fields[field_index+13]
            data['projection']   = fields[field_index+14]
            data['legs_str']     = fields[field_index+15]
            field_index         += 16
            results.append(data)
        return message_id,request_id,results

    @staticmethod
    def scanner_parameters(fields):
        message_id          = int(fields[0])
        request_id          = int(fields[1])
        parameter_xml       = bytearray(fields[2]).decode()
        scanner_parameters  = xmltodict.parse(parameter_xml)
        return message_id, request_id, scanner_parameters

    @staticmethod
    def soft_dollar_tiers(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        num_tiers = int(fields[2])
        field_index = 3
        tiers = []
        for i in range(num_tiers):
            tier = {
                'name'          : bytearray(fields[field_index]).decode()   ,
                'value'         : bytearray(fields[field_index+1]).decode() ,
                'display_name'  : bytearray(fields[field_index+2]).decode()
            }
            field_index += 3
            tiers.append(tier)
        return message_id, request_id, tiers

    @staticmethod
    def symbol_samples(fields):
        request_id = int(fields[1])
        num_samples = int(fields[2])
        field_index = 3
        contracts = []
        for index in range(num_samples):
            contract = Contract()
            contract.id               = int(fields[field_index])
            contract.symbol           = bytearray(fields[field_index+1]).decode()
            contract.security_type    = bytearray(fields[field_index+2]).decode()
            contract.primary_exchange = bytearray(fields[field_index+3]).decode()
            contract.currency         = bytearray(fields[field_index+4]).decode()

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
        """
        Process tick_price messages received from the Bridge (TWS/IB Gateway)

        :param fields:
        :return:
        """
        message_id      = int(fields[0])
        request_id      = int(fields[2])
        tick_type_id    = int(fields[3])
        price           = float(fields[4])
        size            = int(fields[5])
        attr_mask       = int(fields[6])
        tick_type       = TickType(tick_type_id)

        tick_data =    {
            'tick_type_id'      : tick_type_id          ,
            'size'              : size                  ,
            'price'             : price                 ,
            'can_auto_execute'  : attr_mask & 1 != 0    ,
            'past_limit'        : attr_mask & 2 != 0    ,
            'pre_open'          : attr_mask & 4 != 0    ,
            'tick_type'         : tick_type
        }

        return message_id, request_id, tick_data

    @staticmethod
    def tick_request_params(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        data = {
            'min_tick'              : float(fields[2])                  ,
            'bbo_exchange'          : bytearray(fields[3]).decode()     ,
            'snapshot_permisions'   : bytearray(fields[4]).decode()
        }
        return message_id, request_id, data

    @staticmethod
    def tick_size(fields):
        message_id = int(fields[0])
        #TODO: Figure out what fields[1] is

        request_id = int(fields[2])
        tick_type_id = int(fields[3])
        tick_type    = TickType(tick_type_id)
        data = {
            'tick_type_id'  :   tick_type_id    ,
            'size'          :   int(fields[4])  ,
            'tick_type'     :   tick_type

        }

        return message_id, request_id, data

    @staticmethod
    def tick_string(fields):
        message_id = int(fields[0])
        #TODO: Figure out what fields[1] is
        request_id = int(fields[2])
        data = {
            'tick_type_id': int(fields[3]),
            'value'       : bytearray(fields[4])
        }

        return message_id, request_id, data

    @staticmethod
    def order_status(fields):
        info = {
            'message_id'            : int(fields[0]),
            'order_id'              : int(fields[1]),
            'status'                : bytearray(fields[2]).decode(),
            'filled'                : float(fields[3]),
            'remaining'             : float(fields[4]),
            'average_fill_price'    : float(fields[5]),
            'perm_id'               : int(fields[6]),
            'parent_id'             : int(fields[7]),
            'last_fill_price'       : int(fields[8]),
            'client_id'             : int(fields[9]),
            'why_held'              : bytearray(fields[10]).decode(),
            'market_cap_price'      : float(fields[11]),
        }
        return info


    @staticmethod
    def open_order(fields):

        message_id      = int(fields[0])
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
        contract.currency                          = bytearray(fields[11]).decode()
        contract.localSymbol                       = bytearray(fields[12]).decode()
        contract.tradingClass                      = bytearray(fields[13]).decode()

        # Parse Order Information
        order                                       = Order()
        order.action                                = bytearray(fields[14]).decode()
        order.total_quantity                        = float(fields[15])
        order.order_type                            = bytearray(fields[16]).decode()
        order.lmtPrice                              = float(fields[17])
        order.auxPrice                              = fields[18]
        order.tif                                   = bytearray(fields[17]).decode()
        order.ocaGroup                              = bytearray(fields[18]).decode()
        order.account                               = bytearray(fields[19]).decode()
        order.openClose                             = bytearray(fields[20]).decode()
        order.origin                                = int(fields[21])
        order.orderRef                              = bytearray(fields[22]).decode()
        order.client_id                             = int(fields[23])
        order.permId                                = int(fields[24])
        order.outside_rth                           = fields[25]
        order.hidden                                = fields[26]
        order.discretionaryAmt                      = float(fields[28])
        order.goodAfterTime                         = bytearray(fields[29]).decode()

        _sharesAllocation                           = bytearray(fields[30]).decode()  # deprecated ver 6 field

        order.fa_group                              = bytearray(fields[31]).decode()
        order.fa_method                             = bytearray(fields[32]).decode()
        order.fa_percentage                         = bytearray(fields[33]).decode()
        order.fa_profile                            = bytearray(fields[34]).decode()
        order.model_code                            = bytearray(fields[35]).decode()
        order.good_till_date                        = bytearray(fields[36]).decode()
        order.rule80A                               = bytearray(fields[37]).decode()
        order.percent_offset                        = float(fields[38])
        order.settling_firm                         = bytearray(fields[39]).decode()
        order.short_sale_slot                       = int(fields[40])
        order.designated_location                   = bytearray(fields[41]).decode()
        order.exempt_code                           = int(fields[42])
        order.auction_strategy                      = int(fields[43])
        order.startingPrice                         = float(fields[44])
        order.stockRefPrice                         = float(fields[45])
        order.delta                                 = float(fields[46])
        order.stockRangeLower                       = float(fields[47])
        order.stockRangeUpper                       = float(fields[48])
        order.displaySize                           = float(fields[49])


        order.block_order                           = int(fields[48]) == 1
        order.sweep_to_fill                         = int(fields[49]) == 1
        order.all_or_none                           = int(fields[50]) == 1
        order.min_qty                               = int(fields[51])
        order.oca_type                              = int(fields[52])
        order.eTradeOnly                            = int(fields[53]) == 1
        order.firm_quote_only                       = int(fields[54]) == 1
        order.nbbo_price_cap                        = float(fields[55])

        order.parent_id                             = int(fields[56])
        order.trigger_method                        = int(fields[57])

        order.volatility = float(fields[58])
        order.volatility_type = int(fields[59])
        order.delta_neutral_order_type = bytearray(fields[59]).decode()  # ver 11 field (had a hack for ver 11)
        order.delta_neutral_aux_price = float(fields[60])

        if order.delta_neutral_order_type:
            order.delta_neutral_con_id              = int(fields[61])
            order.delta_neutral_settling_firm       = bytearray(fields[62]).decode()
            order.delta_neutral_clearing_account    = bytearray(fields[63]).decode()
            order.deltaNeutralClearingIntent     = bytearray(fields[64]).decode()
            order.deltaNeutralOpenClose          = bytearray(fields[65]).decode()
            order.deltaNeutralShortSale          = int(fields[66])
            order.deltaNeutralShortSaleSlot      = int(fields[67])
            order.deltaNeutralDesignatedLocation = bytearray(fields[68]).decode()

        order.continuousUpdate   = int(fields[69]) == 1
        order.referencePriceType = int(fields[70])
        order.trail_stop_price     = float(fields[71])
        order.trailing_percent    = float(fields[72])

        order.basisPoints         = float(fields[73])
        order.basisPointsType     = int(fields[74])
        contract.combo_legs_description = bytearray(fields[75]).decode()  # ver 14 field


        # Process the contract's combo legs
        combo_legs_count = int(fields[77])
        contract.combo_legs = []
        field_index = 78
        for _ in range(combo_legs_count):
            combo_leg = {
                'contract_id'        : int(fields[field_index]),
                'ratio'              : int(fields[field_index+1]),
                'action'             : bytearray(fields[field_index+2]).decode(),
                'exchange'           : bytearray(fields[field_index+3]).decode(),
                'openClose'          : int(fields[field_index+4]),
                'shortSaleSlot'      : int(fields[field_index+5]),
                'designatedLocation' : bytearray(fields[field_index+6]).decode(),
                'exemptCode'         : int(fields[field_index+7])
            }
            field_index += 8
            contract.combo_legs.append(combo_leg)

        # Process the order's combo legs
        order_combo_legs_count = int(fields[field_index])
        order.orderComboLegs = []
        for _ in range(order_combo_legs_count):
            order_combo_leg = {
                'price' : float(fields[field_index])
            }
            field_index += 1
            order.orderComboLegs.append(order_combo_leg)

        # Process the smart routing parameters
        smartComboRoutingParamsCount = int(fields[field_index])
        order.smartComboRoutingParams = []
        field_index += 1
        for _ in range(smartComboRoutingParamsCount):
            tag_value = {
                'tag'    : bytearray(fields[field_index]).decode(),
                'value'  : bytearray(fields[field_index+1]).decode()
            }
            field_index += 2
            order.smartComboRoutingParams.append(tag_value)


        order.scaleInitLevelSize = int(fields[field_index])
        order.scaleSubsLevelSize = int(fields[field_index+1])
        order.scalePriceIncrement = float(fields[field_index+2])
        field_index += 3

        # Set order scale data
        if order.scalePriceIncrement != UNSET_DOUBLE and order.scalePriceIncrement > 0.0:
            order.scalePriceAdjustValue     = float(fields[field_index])
            order.scalePriceAdjustInterval  = int(fields[field_index+1])
            order.scaleProfitOffset         = float(fields[field_index+2])
            order.scaleAutoReset            = int(fields[field_index+3]) == 1
            order.scaleInitPosition         = int(fields[field_index+4])
            order.scaleInitFillQty          = int(fields[field_index+5])
            order.scaleRandomPercent        = int(fields[field_index+6]) == 1
            field_index                    += 7


        order.hedgeType = bytearray(fields[field_index]).decode()
        if order.hedgeType:
            order.hedgeParam :bytearray(fields[field_index+1]).decode()
            field_index += 2
        else:
            field_index += 1


        order.optOutSmartRouting    = int(fields[field_index]) == 1
        order.clearingAccount       = bytearray(fields[field_index+1]).decode()  # ver 19 field
        order.clearingIntent        = bytearray(fields[field_index+2]).decode()  # ver 19 field
        order.notHeld               = int(fields[field_index+3]) == 1
        field_index                += 4

        # Process the delta neutral contract
        deltaNeutralContractPresent = int(fields[field_index]) == 1
        if deltaNeutralContractPresent:
            contract.delta_neutral_contract = Contract()
            contract.delta_neutral_contract.contract_id = int(fields[field_index + 1])
            contract.delta_neutral_contract.delta = float(fields[field_index + 2])
            contract.delta_neutral_contract.price = float(fields[field_index + 3])
            field_index += 4
        else:
            field_index += 1

        order.algorithmic_strategy = bytearray(fields[field_index]).decode()
        if order.algorithmic_strategy:
            algo_params_count = int(fields[field_index+1])
            field_index += 2
        else:
            field_index +=1

        order.algorithmic_parameters = []
        
        for _ in range(algo_params_count):
            tag_value = {
                'tag'   : bytearray(fields[field_index]).decode(),
                'value' : bytearray(fields[field_index+1]).decode()
            }
            field_index += 2
            order.algorithmic_parameters.append(tag_value)

        order_state                         = OrderState()
        order.solicited                     = int(fields[field_index]) == 1
        order.whatIf                        = int(fields[field_index+1]) == 1
        order_state.status                  = bytearray(fields[field_index+2]).decode()
        order_state.initMarginBefore        = bytearray(fields[field_index+3]).decode()
        order_state.maintMarginBefore       = bytearray(fields[field_index+4]).decode()
        order_state.equityWithLoanBefore    = bytearray(fields[field_index+5]).decode()
        order_state.initMarginChange        = bytearray(fields[field_index+6]).decode()
        order_state.maintMarginChange       = bytearray(fields[field_index+7]).decode()
        order_state.equityWithLoanChange    = bytearray(fields[field_index+8]).decode()

        order_state.initMarginAfter         = bytearray(fields[field_index+9]).decode()
        order_state.maintMarginAfter        = bytearray(fields[field_index+10]).decode()
        order_state.equityWithLoanAfter     = bytearray(fields[field_index+11]).decode()

        order_state.commission              = float(fields[field_index+12])
        order_state.minCommission           = float(fields[field_index+13])
        order_state.maxCommission           = float(fields[field_index+14])
        order_state.commissionCurrency      = bytearray(fields[field_index+15]).decode()
        order_state.warningText             = bytearray(fields[field_index+16]).decode()

        order.randomizeSize                 = int(fields[field_index+17]) == 1
        order.randomizePrice                = int(fields[field_index+18]) == 1
        field_index += 19
        

        conditions_size = 0
        if order.order_type == "PEG BENCH":
            order.reference_contract_id          = int(fields[field_index])
            order.is_pegged_change_amount_decrease = int(fields[field_index + 1]) == 1
            order.pegged_change_amount           = float(fields[field_index + 2])
            order.reference_change_amount        = float(fields[field_index + 3])
            order.reference_exchange_id          = bytearray(fields[field_index + 4]).decode()

            conditions_size = int(fields[field_index+5])
            field_index += 6

        order.conditions = []
        for _ in range(conditions_size):
            conditionType = int(fields[field_index])
            field_index += 1
            #condition = order_condition.Create(conditionType)
            #condition.decode(fields)
            #order.conditions.append(condition)

        order.conditionsIgnoreRth = int(fields[field_index]) == 1
        order.conditionsCancelOrder = int(fields[field_index+1]) == 1

        order.adjusted_order_type       = bytearray(fields[field_index + 2]).decode()
        order.trigger_price             = float(fields[field_index + 3])
        order.trail_stop_price          = float(fields[field_index + 4])
        order.limit_price_offset        = float(fields[field_index + 5])
        order.adjusted_stop_price       = float(fields[field_index + 6])
        order.adjusted_stop_limit_price = float(fields[field_index + 7])
        order.adjusted_trailing_amount  = float(fields[field_index + 8])
        order.adjustable_trailing_unit  = int(fields[field_index + 9])
        name                            = bytearray(fields[field_index+10]).decode()
        value                           = bytearray(fields[field_index+11]).decode()
        displayName                     = bytearray(fields[field_index+12]).decode()
        #order.softDollarTier = SoftDollarTier(name, value, displayName)

        order.cash_qty = float(fields[field_index + 13])
        order.dontUseAutoPriceForHedge = int(fields[field_index+14]) == 1
        order.isOmsContainer = int(fields[field_index+15]) == 1
            

    @staticmethod
    def portfolio_value(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        # read contract fields
        contract = Contract()
        contract.id                                = int(fields[2])
        contract.symbol                            = bytearray(fields[3]).decode()
        contract.security_type                     = bytearray(fields[4]).decode()
        contract.last_trade_date_or_contract_month = bytearray(fields[5]).decode()
        contract.strike                            = float(fields[6])
        contract.right                             = bytearray(fields[7]).decode()
        contract.multiplier                        = bytearray(fields[8]).decode()
        contract.primaryExchange                   = bytearray(fields[9]).decode()
        contract.currency                          = bytearray(fields[10]).decode()
        contract.localSymbol                       = bytearray(fields[11]).decode()
        contract.tradingClass                      = bytearray(fields[12]).decode()

        portfolio_info = {
            'position'      : float(fields[13]),
            'market_price'  : float(fields[14]),
            'average_cost'  : float(fields[15]),
            'unrealized_pnl': float(fields[16]),
            'realized_pnl'  : float(fields[17]),
            'account_name'  : bytearray(fields[18]).decode()
        }

        data = {'portfolio_info':portfolio_info, 'contract':contract}
        return message_id, request_id, data

    @staticmethod
    def execution_data(fields):
        message_id                                  = int(fields[0])
        request_id                                  = int(fields[1])
        order_id                                    = int(fields[2])

        # Parse Contract Information
        contract                                    = Contract()
        contract.id                                 = int(fields[3])
        contract.symbol                             = bytearray(fields[4]).decode()
        contract.security_type                      = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month  = bytearray(fields[6]).decode()
        contract.strike                             = float(fields[7])
        contract.right                              = bytearray(fields[8]).decode()
        contract.multiplier                         = bytearray(fields[9]).decode()
        contract.exchange                           = bytearray(fields[10]).decode()
        contract.currency                           = bytearray(fields[11]).decode()
        contract.local_symbol                       = bytearray(fields[12]).decode()
        contract.trading_class                      = bytearray(fields[13]).decode()

        # Parse Execution Information
        execution                                   = Execution()
        execution.order_id                          = order_id
        execution.id                                = bytearray(fields[14]).decode()
        execution.datetime                          = MessageParser._parse_ib_date(bytearray(fields[15]).decode())
        execution.account_number                    = bytearray(fields[16]).decode()
        execution.exchange                          = bytearray(fields[17]).decode()
        execution.side                              = bytearray(fields[18]).decode()
        execution.shares                            = float(fields[19])
        execution.price                             = float(fields[20])
        execution.permId                            = int(fields[21])
        execution.client_id                         = int(fields[22])
        execution.liquidation                       = int(fields[23])
        execution.quantity                          = float(fields[24])
        execution.average_price                     = float(fields[25])
        execution.order_reference                   = bytearray(fields[26]).decode()
        execution.ev_rule                           = bytearray(fields[27]).decode()
        execution.ev_multiplier                     = bytearray(fields[28]).decode()
        execution.model_code                        = bytearray(fields[29]).decode()
        execution.last_liquidity                    = int(fields[30])
        execution.contract                          = contract

        data = {'execution':execution , 'contract':contract}
        return message_id, request_id, data

    @staticmethod
    def execution_data_end(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        something    = bytearray(fields[2]).decode()
        return message_id, request_id, None


    @staticmethod
    def historical_data_update(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        bar           = Bar()
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
        request_id  = int(fields[1])

        bar         = Bar()
        bar.time    = int(fields[2])
        bar.open    = float(fields[3])
        bar.high    = float(fields[4])
        bar.low     = float(fields[5])
        bar.close   = float(fields[6])
        bar.volume  = int(fields[7])
        bar.wap     = float(fields[8])
        bar.count   = int(fields[9])
        return message_id, request_id, bar

    @staticmethod
    def tick_option_computation(fields):
        option_price = None
        pvDividend = None
        gamma = None
        vega = None
        theta = None
        underlying_price = None

        message_id = int(fields[0])
        version    = int(fields[1])
        request_id = int(fields[2])
        tick_type  = int(fields[3])

        impliedVol = float(fields[4])
        delta      = float(fields[5])

        if impliedVol < 0:  # -1 is the "not computed" indicator
            impliedVol = None
            
        if delta == -2:  # -2 is the "not computed" indicator
            delta = None

        field_index = 6
        if  tick_type in [TickType.MODEL_OPTION,TickType.DELAYED_MODEL_OPTION]:
            option_price = float(fields[field_index])
            pvDividend = float(fields[field_index+1])
            field_index += 2

            if option_price == -1:  # -1 is the "not computed" indicator
                option_price = None
            if pvDividend == -1:  # -1 is the "not computed" indicator
                pvDividend = None


        gamma = float(fields[field_index])
        vega = float(fields[field_index+1])
        theta = float(fields[field_index+2])
        underlying_price = float(fields[field_index+3])

        if gamma == -2:  # -2 is the "not yet computed" indicator
            gamma = None
        if vega == -2:  # -2 is the "not yet computed" indicator
            vega = None
        if theta == -2:  # -2 is the "not yet computed" indicator
            theta = None
        if underlying_price == -1:  # -1 is the "not computed" indicator
            underlying_price = None


    @staticmethod
    def delta_neutral_validation(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        #delta_neutral_contract = DeltaNeutralContract() #TODO: decide if we should have a DeltaNeutralContract
        delta_neutral_contract = Contract()

        delta_neutral_contract.contract_id = int(fields[2])
        delta_neutral_contract.delta       = float(fields[3])
        delta_neutral_contract.price       = float(fields[4])
        return message_id, request_id, delta_neutral_contract


    @staticmethod
    def position_data(fields):
        """
        Process the position_data message from the Bridge Connection
        :param fields:
        :return:
        """

        message_id = int(fields[0])
        request_id = int(fields[1])


        account = bytearray(fields[2]).decode()

        # decode contract fields
        contract                                    = Contract()
        contract.id                                 = int(fields[3])
        contract.symbol                             = bytearray(fields[4]).decode()
        contract.security_type                      = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month  = bytearray(fields[6]).decode()
        contract.strike                             = float(fields[7])
        contract.right                              = bytearray(fields[8]).decode()
        contract.multiplier                         = bytearray(fields[9]).decode()
        contract.exchange                           = bytearray(fields[10]).decode()
        contract.currency                           = bytearray(fields[11]).decode()
        contract.local_symbol                       = bytearray(fields[12]).decode()
        contract.trading_class                      = bytearray(fields[13]).decode()

        position                                    = float(fields[14])
        average_cost                                = float(fields[15])

        position = {'account':account, 'contract':contract,'position':position,'average_cost':average_cost}
        return message_id, request_id, position

    @staticmethod
    def position_end(fields):
        """
        Process the position_end message
        :param fields: Parsed Bridge Connection Message
        :return:
        """
        message_id = int(fields[0])
        request_id = int(fields[1])
        return message_id, request_id, None

    @staticmethod
    def position_multi(fields):
        message_id                                  = int(fields[0])
        request_id                                  = int(fields[1])
        account = bytearray(fields[2]).decode()

        # decode contract fields
        contract = Contract()
        contract.id                                 = int(fields[3])
        contract.symbol                             = bytearray(fields[4]).decode()
        contract.security_type                      = bytearray(fields[5]).decode()
        contract.last_trade_date_or_contract_month  = bytearray(fields[6]).decode()
        contract.strike                             = float(fields[7])
        contract.right                              = bytearray(fields[8]).decode()
        contract.multiplier                         = bytearray(fields[9]).decode()
        contract.exchange                           = bytearray(fields[10]).decode()
        contract.currency                           = bytearray(fields[11]).decode()
        contract.local_symbol                       = bytearray(fields[12]).decode()
        contract.trading_class                      = bytearray(fields[13]).decode()

        position                                    = float(fields[14])
        average_cost                                = float(fields[15])
        modelCode                                   = bytearray(fields[16]).decode()

        return

    @staticmethod
    def security_definition_option_parameter(fields):
        message_id                  = int(fields[0])
        request_id                  = int(fields[1])
        exchange                    = bytearray(fields[2]).decode()
        underlying_contract_id      = int(fields[3])
        underlying_symbol           = bytearray(fields[4]).decode()
        multiplier                  = bytearray(fields[5]).decode()
        exp_count                   = int(fields[6])

        # Create a list of all expirations
        expirations = []
        field_index  = 7
        for _ in range(exp_count):
            expiration = bytearray(fields[field_index]).decode()
            field_index += 1
            expirations.append(expiration)


        strike_count = int(fields[field_index])
        field_index += 1
        strikes = []
        for _ in range(strike_count):
            strike = float(fields[field_index])
            field_index += 1
            strikes.append(strike)

        chain = OptionChain(exchange,underlying_contract_id,underlying_symbol,multiplier,expirations,strikes)
        return message_id, request_id, chain

    @staticmethod
    def security_definition_option_parameter_end(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        return message_id, request_id


    @staticmethod
    def smart_components(fields):
        """
        Parse smart_components messages and return well formatted data

        :param fields:
        :returns: bit_number      - ????
                  exchange        - Name of the Exchange
                  exchange_letter - the one letter code for the given exchange
        """

        message_id       = int(fields[0])
        request_id       = int(fields[1])
        num_components   = int(fields[2])
        field_index      = 3
        smart_components = []
        for _ in range(num_components):
            smart_component = {
                'bit_number'        : int(fields[field_index]),
                'exchange'          : bytearray(fields[field_index+1]).decode(),
                'exchange_letter'   : bytearray(fields[field_index+2]).decode()
            }
            field_index += 3
            smart_components.append(smart_component)
        return message_id, request_id, smart_components

    @staticmethod
    def tick_req(fields):
        message_id           = int(fields[0])
        ticker_id            = int(fields[1])
        min_tick             = float(fields[2])
        bbo_exchange         = bytearray(fields[3]).decode()
        snapshot_permissions = int(fields[4])
        return

    @staticmethod
    def market_depth_exchanges(fields):
        message_id = int(fields[0])
        depth_mkt_data_descriptions = []
        num_exchanges = int(fields[1])
        field_index = 2
        for _ in range(num_exchanges):
            desc = {
                'exchange'          : bytearray(fields[field_index]).decode(),
                'security_type'     : bytearray(fields[field_index+1]).decode(),
                'listing_exchange'  : bytearray(fields[field_index+2]).decode(),
                'service_data_type' : bytearray(fields[field_index+3]).decode(),
                'agg_group'         : int(fields[field_index+4])
            }
            field_index += 5
            depth_mkt_data_descriptions.append(desc)
        return message_id, depth_mkt_data_descriptions

    @staticmethod
    def tick_news(fields):
        message_id   = int(fields[0])
        ticker_id    = int(fields[1])
        timeStamp    = int(fields[2])
        providerCode = bytearray(fields[3]).decode()
        articleId    = bytearray(fields[4]).decode()
        headline     = bytearray(fields[5]).decode()
        extraData    = bytearray(fields[6]).decode()


    @staticmethod
    def news_providers(fields):
        message_id = int(fields[0])
        news_providers = []
        num_news_providers = int(fields[1])
        field_index = 2
        for _ in range(num_news_providers):
            provider = {
                'code' : bytearray(fields[field_index]).decode(),
                'name' : bytearray(fields[field_index+1]).decode()
            }
            field_index += 2
            news_providers.append(provider)


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

        news = {
            'time'          : bytearray(fields[2]).decode(),
            'provider_code' : bytearray(fields[3]).decode(),
            'article_id'    : bytearray(fields[4]).decode(),
            'headline'      : bytearray(fields[5]).decode()
        }
        return message_id, request_id, news



    @staticmethod
    def historical_news_end(fields):
        """

        :param fields: Bridge Message Fields
        :return: message_id -
        :return: request_id - The initial request's request_id
        :return: has_more - More data is available
        """
        message_id = int(fields[0])
        request_id = int(fields[1])
        has_more = int(fields[2]) == 1
        return message_id, request_id, has_more

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


    @staticmethod
    def market_rule(fields):
        message_id = int(fields[0])
        market_rule_id = int(fields[1])

        n_price_increments = int(fields[2])
        field_index = 3
        price_increments = []

        if n_price_increments > 0:
            for _ in range(n_price_increments):
                price_increment = {
                'low_edge'  : float(fields[field_index]),
                'increment' : float(fields[field_index + 1])
                }
                field_index += 2
                price_increments.append(price_increment)
        return message_id, market_rule_id, price_increments

    @staticmethod
    def pnl(fields):
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
        return message_id, request_id, ticks

    @staticmethod
    def historical_ticks_last(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_count = int(fields[2])

        ticks = []

        field_index = 3
        for _ in range(tick_count):
            mask = int(field_index+1)
            historicalTickLast = {
                'time' : int(fields[field_index]),
                'mask' : int(fields[field_index+1]),
                'price' : float(fields[field_index+2]),
                'size' : int(fields[field_index+3]),
                'exchange' : bytearray(fields[field_index+4]).decode(),
                'specialConditions': bytearray(fields[field_index+5]).decode()
            }
            field_index += 6
            ticks.append(historicalTickLast)

            #TODO: Add back in this logic
            #tickAttribLast = TickAttribLast()
            #tickAttribLast.pastLimit = mask & 1 != 0
            #tickAttribLast.unreported = mask & 2 != 0
            #'tickAttribLast' : tickAttribLast

        done = int(fields[field_index]) == 1
        return message_id, request_id, ticks


    @staticmethod
    def tick_by_tick(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        tick_type  = int(fields[2])
        time       = int(fields[3])

        #TODO: Change comparisons to use TickType
        if tick_type == 0:
            # None
            pass
        elif tick_type == 1 or tick_type == 2:
            # Last or AllLast
            price = float(fields[4])
            size = int(fields[5])
            mask = int(fields[6])

            #tickAttribLast = TickAttribLast()
            #tickAttribLast.pastLimit = mask & 1 != 0
            #tickAttribLast.unreported = mask & 2 != 0
            exchange = bytearray(fields[7]).decode()
            specialConditions = bytearray(fields[8]).decode()
        elif tick_type == 3:
            # BidAsk
            bidPrice = float(fields[4])#float(fields[])
            askPrice = float(fields[5])#float(fields[])
            bidSize = float(fields[6])#int(fields[])
            askSize = int(fields[7])#int(fields[])
            mask = int(fields[8])#int(fields[])
            #tickAttribBidAsk = TickAttribBidAsk()
            #tickAttribBidAsk.bidPastLow = mask & 1 != 0
            #tickAttribBidAsk.askPastHigh = mask & 2 != 0
        elif tick_type == 4:
            # MidPoint
            midPoint = float(fields[4])


        return message_id, request_id