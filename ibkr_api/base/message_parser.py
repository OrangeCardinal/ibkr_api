"""
Extracts data from messages received from the Bridge Connection
and returns it the format message_id, request_id, data

data is usually a dictionary on a given object
"""
from ibkr_api.base.constants                        import UNSET_DOUBLE
from ibkr_api.base.constants                        import UNSET_INTEGER
from ibkr_api.classes.bar                           import Bar
from ibkr_api.classes.contracts.contract            import Contract
from ibkr_api.classes.contracts.stock               import Stock
from ibkr_api.classes.contracts.contract_details    import ContractDetails
from ibkr_api.classes.enum.tick_type                import TickType
from ibkr_api.classes.execution                     import Execution
from ibkr_api.classes.option_chain                  import OptionChain
from ibkr_api.classes.orders.order                  import Order
from ibkr_api.classes.order_state                   import OrderState

from dateutil   import parser as date_parser
from datetime   import date, datetime
from    math    import  ceil
import pandas   as pd
import logging
import xmltodict
import time

logger = logging.getLogger(__name__)


class MessageParser(object):
    def __init__(self):
        self.server_version = 147

    @staticmethod
    def _optional_field(value, conversion_type):
        """
        Check if a value exists, and if so cast it to the correct type

        :param value: String value
        :param conversion_type: Type of field we wish to treat this value as
        :return: A value converted to the specified type
        """
        if value == '' and isinstance(0, conversion_type):
            value = UNSET_INTEGER
        elif isinstance(0, conversion_type):
            value = int(value)
        elif value == '' and isinstance(0.0,conversion_type):
            value = UNSET_DOUBLE
        elif isinstance(0.0,conversion_type):
            value = float(value)
        elif value == '' and isinstance(True,conversion_type):
            value = False
        elif isinstance(True, conversion_type):
            value = int(value) == 1
        return value

    @staticmethod
    def _parse_ib_date(date_val):
        if date_val:
            print(date_val[:-3])
            print(date_val[-3:])
            date_val = date_parser.parse(date_val)
        return date_val

    #TODO: Remove this function? not sure, probably (can remove after function above handles timezones)
    @staticmethod
    def _parse_last_trade_or_contract_month(fields, contract: ContractDetails, is_bond: bool):
        last_trade_date_or_contract_month = fields[1]
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
    def commission_report(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        commission_report = {
            'execute_id'            : fields[2],
            'commission'            : float(fields[3]),
            'currency'              : fields[4],
            'realized_pnl'          : float(fields[5]),
            'yield'                 : float(fields[6]),
            'yield_redemption_date' : fields[7]
        }
        return message_id, request_id, commission_report

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
        contract.symbol                             = fields[3]
        contract.security_type                      = fields[4]
        contract.last_trade_date_or_contract_month  = MessageParser._parse_ib_date(fields[5])
        contract.strike                             = float(fields[6])
        contract.right                              = fields[7]
        contract.exchange                           = fields[8]
        contract.currency                           = fields[9]
        contract.local_symbol                       = fields[10]
        contract.market_name                        = fields[11]
        contract.trading_class                      = fields[12]
        contract.id                                 = int(fields[13])
        contract.min_tick                           = float(fields[14])
        contract.md_size_multiplier                 = int(fields[15])
        contract.multiplier                         = fields[16]
        contract.order_types                        = fields[17]
        contract.valid_exchanges                    = fields[18]
        contract.price_magnifier                    = int(fields[19])
        contract.under_contract_id                  = int(fields[20])
        contract.long_name                          = fields[21]
        contract.primary_exchange                   = fields[22]
        contract.contract_month                     = fields[23]
        contract.industry                           = fields[24]
        contract.category                           = fields[25]
        contract.sub_category                       = fields[26]
        contract.time_zone_id                       = fields[27]
        contract.trading_hours                      = fields[28]
        contract.regular_trading_hours              = fields[29]
        contract.ev_rule                            = fields[30]
        contract.ev_multiplier                      = fields[31]

        ##########################################
        # Parse Regular Trading Hour Information #
        ##########################################
        if contract.regular_trading_hours:
            regular_trading_hours = {}
            daily_schedule = contract.regular_trading_hours.split(';')
            for date_hours in daily_schedule:
                parts = date_hours.split('-')
                if len(parts) == 1:
                    (trading_date, closed) = parts[0].split(':')
                    regular_trading_hours[trading_date] = {'market_open':False}
                elif len(parts) == 2:
                    start_date, start_time = parts[0].split(':')
                    end_date, end_time     = parts[1].split(':')
                    regular_trading_hours[start_date] = {'market_open':True,
                                                         'start_date':start_date    ,'start_time':start_time,
                                                         'end_date':end_date        ,'end_time':end_time
                                                         }

            contract.regular_trading_hours = regular_trading_hours

        ######################################
        # Parse Security ID List Information #
        ######################################
        security_id_list_count      = int(fields[32])
        contract.security_id_list   = []
        index                       = 33
        if security_id_list_count > 0:
            for _ in range(security_id_list_count):
                tag = {
                    'name'      :   fields[index+1],
                    'value'     :   fields[index+2]
                }
                index += 2
                contract.security_id_list.append(tag)

        contract.aggregate_group        = int(fields[index])
        contract.under_symbol           = fields[index+1]
        contract.under_sec_type         = fields[index+2]
        contract.market_rule_ids        = fields[index+3]
        contract.real_expiration_date   = fields[index+4]

        return request_id, message_id, contract

    @staticmethod
    def contract_data_end(fields):
        """
        Parse the contract_data_end message and return well formatted data

        :param fields:
        :return:
        """

        message_id  = int(fields[0])
        request_id  = int(fields[1])
        return_code = int(fields[2])
        return message_id, request_id, None

    @staticmethod
    def bond_contract_data(fields):

        contract = Contract()
        message_id = int(fields[0])
        version = int(fields[1])
        request_id = int(fields[2])
        contract.symbol = fields[3]
        contract.security_type                      = fields[4]
        contract.cusip                              = fields[5]
        contract.coupon                             = int(fields[6])
        contract.last_trade_date_or_contract_month  = MessageParser._parse_ib_date(fields[7])
        contract.issue_date                         = fields[8]
        contract.ratings                            = fields[9]
        contract.bond_type                          = fields[10]
        contract.couponType                         = fields[11]
        contract.convertible                        = fields[12]
        contract.callable                           =  fields[13]
        contract.putable                            = fields[14]
        contract.descAppend                         = fields[15]
        contract.exchange                           = fields[16]
        contract.currency                           = fields[17]
        contract.marketName                         = fields[18]
        contract.tradingClass                       = fields[19]
        contract.id                                 = int(fields[20])
        contract.min_tick                           = float(fields[21])
        contract.mdSizeMultiplier                   = int(fields[22])
        contract.orderTypes                         = fields[23]
        contract.valid_exchanges                    = fields[24]
        contract.next_option_date                   = fields[25]
        contract.next_option_type                   = fields[26]
        contract.next_option_partial                = fields[27]
        contract.notes                              = fields[28]
        contract.long_name                          = fields[29]
        contract.evRule                             = fields[30]
        contract.evMultiplier                       = int(fields[31])
        sec_id_list_count                              = int(fields[32])
        if sec_id_list_count > 0:
            contract.security_id_list = []
            for _ in range(sec_id_list_count):
                tagValue = {
                    'tag'   :     fields[32]    ,
                    'value' :     fields[33]
                }
                contract.security_id_list.append(tagValue)

        contract.agg_group = int(fields[34])
        contract.market_rule_ids = fields[35]

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
            data['account_id']  = fields[field_index]
            data['family_code'] = fields[field_index+1]
            field_index += 2
            family_codes.append(data)
        return family_codes

    @staticmethod
    def head_time_stamp(fields):
        """
        Parse the head_time_stamp message and return well formatted data

        :param fields:
        :return:
        """

        message_id          = int(fields[0])
        request_id          = int(fields[1])
        head_time_stamp     = MessageParser._parse_ib_date(fields[2])
        data            = {
            'time_stamp'   :   MessageParser._parse_ib_date(fields[2])
        }
        current_time    = datetime.now()
        time_diff       = current_time - data['time_stamp']
        if time_diff.days < 365:
            data['duration_string'] = "{0} D".format(time_diff.days)
        else:
            years = ceil(time_diff.days / 365.0)
            data['duration_string']    = "{0} Y".format(years)

        return message_id, request_id, data

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
            bar_date            = fields[bar_index]
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
            'text'      : fields[4]
        }
        return message_id, request_id, info

    @staticmethod
    def managed_accounts(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        account    = fields[2]

        #accounts = []  # List of Accounts to Return
        return message_id, request_id, account


    @staticmethod
    def market_data_type(fields):
        data = {
            'message_id':int(fields[0]),
            'request_id':int(fields[1]),
            'market_data_type':fields[2]
        }
        return data


    @staticmethod
    def market_depth_l2(fields):
        """
        Parses the market_depth_l2 message from the Bridge
        :param fields:
        :return:
        """

        data = {
            'message_id'        : int(fields[0]),
            'request_id'        : int(fields[1]),
            'position'          : int(fields[2]),
            'market_maker'      : fields[3],
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
            'exchange'      : fields[2]
        }
        return data

    @staticmethod
    def reroute_market_depth_request(fields):

        data = {
            'request_id'    : int(fields[0]),
            'contract_id'   : int(fields[1]),
            'exchange'      : fields[2]
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

            contract.symbol                             = fields[field_index+2]
            data['symbol']                     = contract.symbol

            contract.security_type                      = fields[field_index+3]
            data['security_type']                       = contract.security_type

            contract.last_trade_date_or_contract_month  = fields[field_index+4]

            contract.strike                             = int(fields[field_index+5])
            data['strike']                              = contract.strike

            contract.right                              = fields[field_index+6]
            data['right']                               = contract.right

            contract.exchange                           = fields[field_index+7]
            contract.currency                           = fields[field_index+8]
            contract.local_symbol                       = fields[field_index+9]
            contract.market_name                        = fields[field_index+10]
            contract.trading_class                      = fields[field_index+11]

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
        parameter_xml       = fields[2]
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
                'name'          : fields[field_index]       ,
                'value'         : fields[field_index+1]     ,
                'display_name'  : fields[field_index+2]
            }
            field_index += 3
            tiers.append(tier)
        return message_id, request_id, tiers

    @staticmethod
    def symbol_samples(fields):
        request_id  = int(fields[1])
        num_samples = int(fields[2])
        class_map   = {'STK':Stock()}
        field_index = 3
        contracts = []
        for index in range(num_samples):
            security_type               = fields[field_index + 2]
            #todo: switch this for a dict based lookup
            if security_type == 'STK':
                contract                = Stock()
            else:
                contract                = Contract()

            contract.id                 = int(fields[field_index])
            contract.symbol             = fields[field_index + 1]
            contract.security_type      = security_type
            contract.primary_exchange   = fields[field_index+3]
            contract.currency           = fields[field_index+4]
            num_security_types          = int(fields[field_index+5])
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
            'min_tick'              : float(fields[2])      ,
            'bbo_exchange'          : fields[3]             ,
            'snapshot_permisions'   : fields[4]
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
            'tick_type_id': int(fields[3])  ,
            'value'       : fields[4]
        }

        return message_id, request_id, data

    @staticmethod
    def order_status(fields):
        info = {
            'message_id'            : int(fields[0]),
            'order_id'              : int(fields[1]),
            'status'                : fields[2],
            'filled'                : float(fields[3]),
            'remaining'             : float(fields[4]),
            'average_fill_price'    : float(fields[5]),
            'perm_id'               : int(fields[6]),
            'parent_id'             : int(fields[7]),
            'last_fill_price'       : int(fields[8]),
            'client_id'             : int(fields[9]),
            'why_held'              : fields[10],
            'market_cap_price'      : float(fields[11]),
        }
        return info


    @staticmethod
    def open_orders(fields):
        """
        Parses the open_orders message and returns well formatted data

        :param fields: Message Fields

        :returns: message_id
        :returns: None (No Request ID is returned with this type of message)
        :returns: Order
        """
        fields_iterator     = iter(fields)
        optional_field      = MessageParser._optional_field

        order               = Order()
        contract            = Contract()
        order_state                                     = OrderState()

        # Fields 0 - 9
        message_id                                          = int(next(fields_iterator))

        order.order_id                                      = int(next(fields_iterator))

        contract.id                                         = int(next(fields_iterator))
        contract.symbol                                     = next(fields_iterator)
        contract.security_type                              = next(fields_iterator)
        contract.last_trade_date_or_contract_month          = next(fields_iterator)
        contract.strike                                     = next(fields_iterator)
        contract.right                                      = next(fields_iterator)
        contract.multiplier                                 = next(fields_iterator)
        contract.exchange                                   = next(fields_iterator)
        contract.currency                                   = next(fields_iterator)

        # Fields 10 - 19
        contract.local_symbol                               = next(fields_iterator)
        contract.trading_class                              = next(fields_iterator)
        order.contract                                      = contract

        order.action                                        = next(fields_iterator)
        order.total_quantity                                = float(next(fields_iterator))
        order.order_type                                    = next(fields_iterator)
        order.limit_price                                   = float(next(fields_iterator))
        order.aux_price                                     = next(fields_iterator)
        order.time_in_force                                           = next(fields_iterator)
        order.oca_group                                     = next(fields_iterator)
        order.account                                       = next(fields_iterator)
        order.open_close                                    = next(fields_iterator)

        # Fields 20 - 29
        order.origin                                    = int(next(fields_iterator))
        order.order_ref                                 = next(fields_iterator)
        order.client_id                                 = int(next(fields_iterator))
        order.perm_id                                   = int(next(fields_iterator))
        order.outside_rth                               = next(fields_iterator)
        order.hidden                                    = next(fields_iterator)
        order.discretionary_amt                         = next(fields_iterator) #float(fields[29]) #TODO: Fix here

        order.good_after_time                           = next(fields_iterator)
        _sharesAllocation                               = next(fields_iterator)  # deprecated ver 6 field
        order.fa_group                                  = next(fields_iterator)
        order.fa_method                                 = next(fields_iterator)
        order.fa_percentage                             = next(fields_iterator)
        order.fa_profile                                = next(fields_iterator)
        order.model_code                                = next(fields_iterator)
        order.good_till_date                            = next(fields_iterator)
        order.rule80A                                   = next(fields_iterator)
        order.percent_offset                            = next(fields_iterator) #float(fields[39]) #TODO: Fix here

        order.settling_firm                             = next(fields_iterator)
        order.short_sale_slot                           = next(fields_iterator)
        order.designated_location                       = next(fields_iterator) #TODO: Should be int?
        order.exempt_code                               = next(fields_iterator)
        order.auction_strategy                          = optional_field(next(fields_iterator),int)
        order.starting_price                            = optional_field(next(fields_iterator), float)
        order.stock_ref_price                           = optional_field(next(fields_iterator), float)
        order.delta                                     = optional_field(next(fields_iterator), float)
        order.stock_range_lower                         = optional_field(next(fields_iterator), float)
        order.stock_range_upper                         = optional_field(next(fields_iterator), float)

        order.display_size                               = next(fields_iterator)
        order.block_order                               = int(next(fields_iterator)) == 1
        order.sweep_to_fill                             = int(next(fields_iterator)) == 1
        order.all_or_none                               = optional_field(next(fields_iterator), bool)
        order.min_qty                                   = next(fields_iterator)
        order.oca_type                                  = int(next(fields_iterator))
        order.e_trade_only                              = int(next(fields_iterator)) == 1
        order.firm_quote_only                           = optional_field(next(fields_iterator), bool)
        order.nbbo_price_cap                            = next(fields_iterator)
        order.parent_id                                 = int(next(fields_iterator))

        order.trigger_method                            = optional_field(next(fields_iterator), int)
        order.volatility                                = next(fields_iterator)
        order.volatility_type                           = next(fields_iterator)
        order.delta_neutral_order_type                  = next(fields_iterator)
        order.delta_neutral_aux_price                   = next(fields_iterator)

        if order.delta_neutral_order_type:
            order.delta_neutral_con_id                  = int(next(fields_iterator))
            order.delta_neutral_settling_firm           = next(fields_iterator)
            order.delta_neutral_clearing_account        = next(fields_iterator)
            order.delta_neutral_clearing_intent         = next(fields_iterator)
            order.delta_neutral_open_close              = next(fields_iterator)
            order.delta_neutral_short_sale              = next(fields_iterator)
            order.delta_neutral_short_sale_slot         = next(fields_iterator)
            order.delta_neutral_designated_location     = next(fields_iterator)


        order.continuous_update             = optional_field(next(fields_iterator),int)
        order.reference_price_type          = optional_field(next(fields_iterator),int)
        order.trail_stop_price              = optional_field(next(fields_iterator), float)
        order.trailing_percent              = next(fields_iterator)
        order.basis_points                  = next(fields_iterator)
        order.basis_points_type             = next(fields_iterator)
        contract.combo_legs_description     = next(fields_iterator)
        combo_legs_count                    = int(next(fields_iterator))

        # Process the contract's combo legs
        contract.combo_legs = []
        for _ in range(combo_legs_count):
            combo_leg = {
                'contract_id'           : int(next(fields_iterator)),
                'ratio'                 : int(next(fields_iterator)),
                'action'                : next(fields_iterator),
                'exchange'              : next(fields_iterator),
                'open_close'            : int(next(fields_iterator)),
                'short_sale_slot'         : int(next(fields_iterator)),
                'designated_location'    : next(fields_iterator),
                'exempt_code'            : int(next(fields_iterator))
            }
            contract.combo_legs.append(combo_leg)

        # Process the order's combo legs
        order_combo_legs_count = int(next(fields_iterator))
        order.order_combo_legs = []
        for _ in range(order_combo_legs_count):
            order_combo_leg = {
                'price' : float(next(fields_iterator))
            }
            order.order_combo_legs.append(order_combo_leg)

        # Process the smart routing parameters
        smart_combo_routing_params_count = int(next(fields_iterator))
        order.smart_combo_routing_params = []
        for _ in range(smart_combo_routing_params_count):
            tag_value = {
                'tag'    : next(fields_iterator),
                'value'  : next(fields_iterator)
            }
            order.smart_combo_routing_params.append(tag_value)


        order.scale_init_level_size = optional_field(next(fields_iterator),int)
        order.scale_subs_level_size = optional_field(next(fields_iterator),int)
        order.scale_price_increment = optional_field(next(fields_iterator),float)

        # Set order scale data
        if order.scale_price_increment != UNSET_DOUBLE and order.scale_price_increment > 0.0:
            order.scale_price_adjust_value      = float(next(fields_iterator))
            order.scale_price_adjust_interval   = int(next(fields_iterator))
            order.scale_profit_offset           = float(next(fields_iterator))
            order.scale_auto_reset              = int(next(fields_iterator)) == 1
            order.scale_init_position           = int(next(fields_iterator))
            order.scale_init_fill_qty           = int(next(fields_iterator))
            order.scale_random_percent          = int(next(fields_iterator)) == 1


        order.hedge_type = next(fields_iterator)
        if order.hedge_type:
            order.hedge_param = next(fields_iterator)

        order.opt_out_smart_routing         = optional_field(next(fields_iterator),bool)
        order.clearing_account              = next(fields_iterator)
        order.clearing_intent               = next(fields_iterator)
        order.not_held                      = int(next(fields_iterator)) == 1


        # Process the delta neutral contract
        delta_neutral_contract_present = optional_field(next(fields_iterator),bool)

        if delta_neutral_contract_present:
            contract.delta_neutral_contract             = Contract()
            contract.delta_neutral_contract.contract_id = int(next(fields_iterator))
            contract.delta_neutral_contract.delta       = float(next(fields_iterator))
            contract.delta_neutral_contract.price       = float(next(fields_iterator))



        order.algorithmic_strategy  = next(fields_iterator)

        algo_params_count           = 0
        if order.algorithmic_strategy:
            algo_params_count = int(next(fields_iterator))

        order.algorithmic_parameters = []

        for _ in range(algo_params_count):
            tag_value = {
                'tag'   : next(fields_iterator),
                'value' : next(fields_iterator)
            }
            order.algorithmic_parameters.append(tag_value)

        order_state                                     = OrderState()
        order.solicited                                 = optional_field(next(fields_iterator),bool)
        order.what_if                                   = optional_field(next(fields_iterator), bool)
        order_state.status                              = next(fields_iterator)
        order_state.init_margin_before                  = next(fields_iterator)
        order_state.maintenance_margin_before           = next(fields_iterator)
        order_state.equity_with_loan_before             = next(fields_iterator)
        order_state.init_margin_change                  = next(fields_iterator)
        order_state.maintenance_margin_change           = next(fields_iterator)
        order_state.equity_with_loan_change             = next(fields_iterator)

        order_state.initial_margin_after                = next(fields_iterator)
        order_state.maintenance_margin_after            = next(fields_iterator)
        order_state.equityWithLoanAfter                 = next(fields_iterator)

        order_state.commission                          = next(fields_iterator)
        order_state.min_commission                      = next(fields_iterator)
        order_state.max_commission                      = next(fields_iterator)
        order_state.commission_currency                 = next(fields_iterator)
        order_state.warning_text                        = next(fields_iterator)

        order.randomize_size                            = int(next(fields_iterator)) == 1
        order.randomize_price                           = int(next(fields_iterator)) == 1

        conditions_size = 0
        if order.order_type == "PEG BENCH":
            order.reference_contract_id          = int(next(fields_iterator))
            order.is_pegged_change_amount_decrease = int(next(fields_iterator)) == 1
            order.pegged_change_amount           = float(next(fields_iterator))
            order.reference_change_amount        = float(next(fields_iterator))
            order.reference_exchange_id          = next(fields_iterator)

            conditions_size = int(next(fields_iterator))

        order.conditions = []
        for _ in range(conditions_size):
            conditionType = int(next(fields_iterator))
            #condition = order_condition.Create(conditionType)
            #condition.decode(fields)
            #order.conditions.append(condition)

        order.conditions_ignore_rth = int(next(fields_iterator)) == 1
        order.conditions_cancel_order = next(fields_iterator)

        order.adjusted_order_type       = next(fields_iterator)
        order.trigger_price             = next(fields_iterator)
        order.trail_stop_price          = float(next(fields_iterator))
        order.limit_price_offset        = float(next(fields_iterator))
        order.adjusted_stop_price       = float(next(fields_iterator))
        order.adjusted_stop_limit_price = float(next(fields_iterator))
        order.adjusted_trailing_amount  = float(next(fields_iterator))
        order.adjustable_trailing_unit  = next(fields_iterator)
        name                            = next(fields_iterator)
        value                           = next(fields_iterator)
        display_name                     = next(fields_iterator)
        #order.softDollarTier = SoftDollarTier(name, value, displayName)

        order.cash_qty                      = float(next(fields_iterator))
        order.dont_use_auto_price_for_hedge = int(next(fields_iterator)) == 1
        #order.is_oms_container              = int(next(fields_iterator)) == 1 #TODO: debug why this got cut off
        return message_id, None, order


    @staticmethod
    def open_orders_end(fields):
        """
        Process the open_orders_end message and return well formatted data

        :param fields:
        :return:
        """
        message_id = int(fields[0])
        request_id  = int(fields[1])
        return message_id, request_id, None

    @staticmethod
    def portfolio_value(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        # read contract fields
        contract = Contract()
        contract.id                                = int(fields[2])
        contract.symbol                            = fields[3]
        contract.security_type                     = fields[4]
        contract.last_trade_date_or_contract_month = fields[5]
        contract.strike                            = float(fields[6])
        contract.right                             = fields[7]
        contract.multiplier                        = fields[8]
        contract.primaryExchange                   = fields[9]
        contract.currency                          = fields[10]
        contract.localSymbol                       = fields[11]
        contract.tradingClass                      = fields[12]

        portfolio_info = {
            'position'      : float(fields[13]),
            'market_price'  : float(fields[14]),
            'average_cost'  : float(fields[15]),
            'unrealized_pnl': float(fields[16]),
            'realized_pnl'  : float(fields[17]),
            'account_name'  : fields[18]
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
        contract.symbol                             = fields[4]
        contract.security_type                      = fields[5]
        contract.last_trade_date_or_contract_month  = fields[6]
        contract.strike                             = float(fields[7])
        contract.right                              = fields[8]
        contract.multiplier                         = fields[9]
        contract.exchange                           = fields[10]
        contract.currency                           = fields[11]
        contract.local_symbol                       = fields[12]
        contract.trading_class                      = fields[13]

        # Parse Execution Information
        execution                                   = Execution()
        execution.order_id                          = order_id
        execution.id                                = fields[14]
        execution.datetime                          = MessageParser._parse_ib_date(fields[15])
        execution.account_number                    = fields[16]
        execution.exchange                          = fields[17]
        execution.side                              = fields[18]
        execution.shares                            = float(fields[19])
        execution.price                             = float(fields[20])
        execution.permId                            = int(fields[21])
        execution.client_id                         = int(fields[22])
        execution.liquidation                       = int(fields[23])
        execution.quantity                          = float(fields[24])
        execution.average_price                     = float(fields[25])
        execution.order_reference                   = fields[26]
        execution.ev_rule                           = fields[27]
        execution.ev_multiplier                     = fields[28]
        execution.model_code                        = fields[29]
        execution.last_liquidity                    = int(fields[30])
        execution.contract                          = contract

        data = {'execution':execution , 'contract':contract}
        return message_id, request_id, data

    @staticmethod
    def execution_data_end(fields):
        message_id      = int(fields[0])
        request_id      = int(fields[1])
        something       = fields[2]
        return message_id, request_id, None


    @staticmethod
    def historical_data_update(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        bar           = Bar()
        bar.bar_count = int(fields[2])
        bar.date      = fields[3]
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
        pv_dividend = None
        gamma = None
        vega = None
        theta = None
        underlying_price = None

        message_id = int(fields[0])
        version    = int(fields[1])
        request_id = int(fields[2])
        tick_type  = int(fields[3])

        implied_vol = float(fields[4])
        delta      = float(fields[5])

        if implied_vol < 0:  # -1 is the "not computed" indicator
            implied_vol = None

        if delta == -2:  # -2 is the "not computed" indicator
            delta = None

        field_index = 6
        if  tick_type in [TickType.MODEL_OPTION,TickType.DELAYED_MODEL_OPTION]:
            option_price = float(fields[field_index])
            pv_dividend = float(fields[field_index+1])
            field_index += 2

            if option_price == -1:  # -1 is the "not computed" indicator
                option_price = None
            if pv_dividend == -1:  # -1 is the "not computed" indicator
                pv_dividend = None


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


        account = fields[2]

        # decode contract fields
        contract                                    = Contract()
        contract.id                                 = int(fields[3])
        contract.symbol                             = fields[4]
        contract.security_type                      = fields[5]
        contract.last_trade_date_or_contract_month  = fields[6]
        contract.strike                             = float(fields[7])
        contract.right                              = fields[8]
        contract.multiplier                         = fields[9]
        contract.exchange                           = fields[10]
        contract.currency                           = fields[11]
        contract.local_symbol                       = fields[12]
        contract.trading_class                      = fields[13]

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
        account                                     = fields[2]

        # decode contract fields
        contract = Contract()
        contract.id                                 = int(fields[3])
        contract.symbol                             = fields[4]
        contract.security_type                      = fields[5]
        contract.last_trade_date_or_contract_month  = fields[6]
        contract.strike                             = float(fields[7])
        contract.right                              = fields[8]
        contract.multiplier                         = fields[9]
        contract.exchange                           = fields[10]
        contract.currency                           = fields[11]
        contract.local_symbol                       = fields[12]
        contract.trading_class                      = fields[13]

        position                                    = float(fields[14])
        average_cost                                = float(fields[15])
        model_code                                   = fields[16]

        return

    @staticmethod
    def security_definition_option_parameter(fields):
        message_id                  = int(fields[0])
        request_id                  = int(fields[1])
        exchange                    = fields[2]
        underlying_contract_id      = int(fields[3])
        underlying_symbol           = fields[4]
        multiplier                  = fields[5]
        exp_count                   = int(fields[6])

        # Create a list of all expirations
        expirations = []
        field_index  = 7
        for _ in range(exp_count):
            expiration = fields[field_index]
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
        """
        Parse the security_definition_option_parameter_end message and return well formatted data

        :param fields:
        :returns: message_id, request_id, None
        """
        message_id = int(fields[0])
        request_id = int(fields[1])
        return message_id, request_id, None


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
                'exchange'          : fields[field_index+1],
                'exchange_letter'   : fields[field_index+2]
            }
            field_index += 3
            smart_components.append(smart_component)
        return message_id, request_id, smart_components

    @staticmethod
    def tick_req(fields):
        message_id           = int(fields[0])
        ticker_id            = int(fields[1])
        min_tick             = float(fields[2])
        bbo_exchange         = fields[3]
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
                'exchange'          : fields[field_index],
                'security_type'     : fields[field_index+1],
                'listing_exchange'  : fields[field_index+2],
                'service_data_type' : fields[field_index+3],
                'aggregate_group'         : int(fields[field_index+4])
            }
            field_index += 5
            depth_mkt_data_descriptions.append(desc)
        return message_id, depth_mkt_data_descriptions

    @staticmethod
    def tick_news(fields):
        message_id   = int(fields[0])
        ticker_id    = int(fields[1])
        time_stamp    = int(fields[2])
        provider_code = fields[3]
        article_id    = fields[4]
        headline     = fields[5]
        extra_data    = fields[6]


    @staticmethod
    def news_providers(fields):
        message_id = int(fields[0])
        news_providers = []
        num_news_providers = int(fields[1])
        field_index = 2
        for _ in range(num_news_providers):
            provider = {
                'code' : fields[field_index],
                'name' : fields[field_index+1]
            }
            field_index += 2
            news_providers.append(provider)


    @staticmethod
    def news_articles(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])
        article = {
        'type' : int(fields[2]),
        'text' : fields[3]
        }
        return message_id, request_id, article

    @staticmethod
    def historical_news(fields):
        message_id = int(fields[0])
        request_id = int(fields[1])

        news = {
            'time'          : fields[2],
            'provider_code' : fields[3],
            'article_id'    : fields[4],
            'headline'      : fields[5]
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
        """
        Parse the 'market_rule' message and return well formatted data

        :param fields:
        :return:
        """

        message_id      = int(fields[0])
        market_rule_id  = int(fields[1])

        n_price_increments  = int(fields[2])
        field_index         = 3
        price_increments    = []

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
            'position'      :   int(fields[2])      ,
            'daily'         :   float(fields[3])    ,
            'unrealized'    :   float(fields[4])    ,
            'realized'      :   float(fields[5])    ,
            'value'         :   float(fields[6])
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
                'message_id'    :   int(fields[0])                  ,
                'time'          :   int(fields[field_index])        ,
                'price'         :   float(fields[field_index+1])    ,
                'size'          :   int(fields[field_index+2])
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
                'time'              : int(fields[field_index]),
                'mask'              : int(fields[field_index+1]),
                'ask_past_high'     : mask & 1 != 0,
                'bid_past_low'      : mask & 2 != 0,
                'price_bid'         : fields[field_index+2],
                'price_ask'         : float(fields[field_index+3]),
                'size_bid'          : int(fields[field_index+4]),
                'size_ask'          : int(fields[field_index+5])
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
                'exchange' : fields[field_index+4],
                'specialConditions': fields[field_index+5]
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
            exchange = fields[7]
            special_conditions = fields[8]
        elif tick_type == 3:
            # BidAsk
            bid_price = float(fields[4])#float(fields[])
            ask_price = float(fields[5])#float(fields[])
            bid_size = float(fields[6])#int(fields[])
            ask_size = int(fields[7])#int(fields[])
            mask = int(fields[8])#int(fields[])
            #tickAttribBidAsk = TickAttribBidAsk()
            #tickAttribBidAsk.bidPastLow = mask & 1 != 0
            #tickAttribBidAsk.askPastHigh = mask & 2 != 0
        elif tick_type == 4:
            # MidPoint
            mid_point = float(fields[4])


        return message_id, request_id