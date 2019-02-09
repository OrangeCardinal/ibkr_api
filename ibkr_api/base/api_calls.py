import logging


from ibkr_api.base.bridge_connection    import BridgeConnection
from ibkr_api.base.constants            import *
from ibkr_api.base.errors               import NOT_CONNECTED, Errors, BAD_MESSAGE
from ibkr_api.base.messages             import Messages
from ibkr_api.base.message_parser       import MessageParser

from ibkr_api.classes.contracts.contract import Contract
from ibkr_api.classes.orders.order import Order
from ibkr_api.classes.scanner import Scanner

from enum import Enum
from functools import wraps
import socket

logger = logging.getLogger(__name__)


def check_connection(func):
    @wraps(func)
    def new_func(self, *func_args,**func_kwargs):
        if not self.conn.is_connected():
            #self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            logger.warning("Not connected to the Bridge Application (TWS/IB Gateway).")
            return None
        func(self, *func_args, **func_kwargs)
    return new_func

class ApiCalls(object):
    """
    Encapsulates all the requests that are available via the API

    ## Responsibilities
    Call the underlying API call
    Call any user defined request_handler function as needed
    """


    def __init__(self, response_handler=None, request_handler=None):
        self.api_state              = "Detached from Bridge"
        self.client_id              = None
        self.conn                   = None                 # Connection between this application and the bridge

        self.host                   = None                 # Bridge's Host
        self.optional_capabilities  = ""                   # Hell if I know, IBKR's documentation has nothing...
        self.port                   = None                 # Bridge's Port
        self.request_id             = 0                    # Unique Identifier for the request
        self.server_version_        = None

        self.connection_time  = None
        self.message_parser   = MessageParser()   # Converts from message data to object(s)
        self.request_handler  = request_handler   # Functions if exist are called before and/or after api calls
        self.response_handler = response_handler  # API Responses Functions provided by the end user


    @staticmethod
    def _get_optional_fields(contract):
        """
        Process the fields a contract may not have (using the default if it doesn't exist)

        :param contract:
        :return:
        """
        fields = {
            'last_trade_date_or_contract_month' : ''    ,
            'strike'                            : 0.0   , #was empty string, I think correct default is 0.0
            'right'                             : ''    ,
            'multiplier'                        : ''
        }


        if hasattr(contract,'multiplier'):
            fields['multiplier'] = contract.multiplier

        if hasattr(contract,'last_trade_date_or_contract_month'):
            fields['last_trade_date_or_contract_month'] = contract.last_trade_date_or_contract_month

        if hasattr(contract,'strike'):
            fields['strike'] = contract.strike

        if hasattr(contract,'right'):
            fields['right'] = contract.right

        return fields

    def _send_message(self, fields):
        """
        Send the message if connected.
        If not connected, and a response handler is defined, send an error back
        otherwise just raise an error

        :param fields: The message's fields
        :return:
        """
        if not self.conn.is_connected() and self.response_handler:
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
        elif not self.conn.is_connected():
            logger.error(Errors.connect_fail()['message'])
        else:
            self.conn.send_message(fields)

    ####################
    # Public Functions #
    ####################
    def get_local_request_id(self):
        request_id = self.request_id
        self.request_id += 1
        return request_id

    @check_connection
    def calculate_implied_volatility(self,
                                     request_id             : int,
                                     contract               : Contract,
                                     option_price           : float,
                                     underlying_price       : float,
                                     implied_vol_options    : list):
        """
        Creates a 'calculate_implied_volatility' message
        Sends Message to Bridge

        :param request_id: Unique Identifier for this Request
        :param contract: Option which we want to calculate the Implied Volatility of
        :param option_price: Option Price
        :param underlying_price: Underlying Price
        :param implied_vol_options:
        :return:
        """

        message_version = 3


        message_id = Messages.outbound['calculate_implied_volatility']
        fields = [message_id, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, contract.last_trade_date_or_contract_month, contract.strike,
                  contract.right, contract.multiplier, contract.exchange, contract.primary_exchange,
                  contract.currency, contract.local_symbol, contract.trading_class, option_price, underlying_price]

        impl_vol_opt_str = ""
        tag_values_count = len(implied_vol_options) if implied_vol_options else 0
        if implied_vol_options:
            for opt in implied_vol_options:
                impl_vol_opt_str += str(opt)
        fields.extend([tag_values_count, impl_vol_opt_str])

        self.conn.send_message(fields)

    @check_connection
    def calculate_option_price(self, request_id: int, contract: Contract,
                               volatility: float, underlying_price: float,
                               optPrcOptions: list):
        """Call this function to calculate option price and greek values
        for a supplied volatility and underlying price.

        request_id:int -    The ticker ID.
        contract:Contract - Describes the contract.
        volatility:double - The volatility.
        underlying_price:double - Price of the underlying.
        """

        message_version = 3

        # send req market data msg
        message_id = Messages.outbound['request_calc_option_price']
        fields = [message_id, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, contract.last_trade_date_or_contract_month, contract.strike,
                  contract.right, contract.multiplier, contract.exchange, contract.currency, contract.local_symbol]

        fields.extend([contract.trading_class, volatility, underlying_price])


        option_price_options = ""
        tag_values_count = len(optPrcOptions) if optPrcOptions else 0
        if optPrcOptions:
            for implVolOpt in optPrcOptions:
                option_price_options += str(implVolOpt)
        fields.extend([tag_values_count, optPrcOptions])

        self.conn.send_message(fields)

    @check_connection
    def cancel_account_summary(self, request_id: int):
        """Cancels the request for Account Window Summary tab data.

        request_id:int - The ID of the data request being canceled."""

        message_version = 1
        message_id = Messages.outbound['cancel_account_summary']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_account_updates_multi(self, request_id: int):
        message_version = 1
        message_id = Messages.outbound['cancel_account_updates_multi']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)


    @check_connection
    def cancel_calculate_implied_volatility(self, request_id: int):
        """Call this function to cancel a request to calculate
        volatility for a supplied option price and underlying price.

        request_id:int - The request ID.  """
        message_version = 1
        message_id = Messages.outbound['cancel_calculate_implied_volatility']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_calculate_option_price(self, request_id: int):
        """Call this function to cancel a request to calculate the option
        price and greek values for a supplied volatility and underlying price.

        request_id:int - The request ID.  """

        message_version = 1
        message_id = Messages.outbound['cancel_calc_option_price']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)



    @check_connection
    def cancel_fundamental_data(self, request_id: int):
        """
        Call this function to stop receiving fundamental data.

        request_id:int - The ID of the data request.
        """
        message_version = 1
        message_id = Messages.outbound['cancel_fundamental_data']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)


    @check_connection
    def cancel_market_data(self, request_id: int):
        """After calling this function, market data for the specified id
        will stop flowing.

        request_id: int - The ID that was specified in the call to
            reqMktData(). """
        # send req market data msg
        message_version = 2
        message_id = Messages.outbound['cancel_market_data']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_market_depth(self, request_id: int, is_smart_depth: bool):
        """
        Cancels a prior request to to
        :param request_id: Id of the prior call to request_market_depth
        :param is_smart_depth: Specifies SMART depth request
        :return: None
        """
        message_version = 1

        # send cancel market depth msg
        message_id = Messages.outbound['cancel_market_depth']
        fields = [message_id, message_version, request_id]

        if self.server_version() >= MIN_SERVER_VER_SMART_DEPTH:
            fields.append(is_smart_depth)

        self.conn.send_message(fields)

    @check_connection
    def cancel_order(self, order_id: int):
        """Call this function to cancel an order.

        order_id:int - The order ID that was specified previously in the call
            to placeOrder()"""

        message_version = 1
        message_id = Messages.outbound['cancel_order']
        fields = [message_id, message_version, order_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_positions(self):
        """Cancels real-time position updates."""
        message_version = 1
        message_id = Messages.outbound['cancel_positions']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    @check_connection
    def cancel_positions_multi(self, request_id: int):
        message_version = 1
        message_id = Messages.outbound['cancel_positions_multi']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_pnl(self, request_id: int):
        """

        :param request_id:
        :return:
        """
        message_id = Messages.outbound['cancel_pnl']
        fields = [message_id, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_pnl_single(self, request_id: int):
        message_id = Messages.outbound['cancel_pnl_single']
        fields = [message_id, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_real_time_bars(self, request_id: int):
        """Call the cancel_real_time_bars() function to stop receiving real time bar results.

        request_id:int - The Id that was specified in the call to reqRealTimeBars(). """

        # send req market data msg
        message_version = 1
        message_id = Messages.outbound['cancel_real_time_bars']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_scanner_subscription(self, request_id: int):
        """request_id:int - The ticker ID. Must be a unique value."""
        message_version = 1
        message_id = Messages.outbound['cancel_scanner_subscription']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)


    @check_connection
    def cancel_tick_by_tick_data(self, request_id: int):
        message_id = Messages.outbound['cancel_tick_by_tick_data']
        fields = [message_id, request_id]
        self.conn.send_message(fields)

    @check_connection
    def exercise_options(self, request_id: int, contract: Contract,
                         exercise_or_lapse: int, exercise_quantity: int,
                         account: str, override: int):
        """

        :param request_id: Unique identifier for this request
        :param contract: Contract of the option to be acted upon
        :param exercise_or_lapse:  1 = exercise, 2 = lapse
        :param exercise_quantity:
        :param account:
        :param override:
        :return:
        """
        """request_id:int - The ticker id. multipleust be a unique value.
        contract:Contract - This structure contains a description of the
            contract to be exercised
        exercise_or_lapse:int - Specifies whether you want the option to lapse
            or be exercised.

        exercise_quantity:int - The quantity you want to exercise.
        account:str - destination account
        override:int - Specifies whether your setting will override the system's
            natural action. For example, if your action is "exercise" and the
            option is not in-the-money, by natural action the option would not
            exercise. If you have override set to "yes" the natural action would
             be overridden and the out-of-the money option would be exercised.
            Values are: 0 = no, 1 = yes."""

        insert_offset = 0
        message_version = 2
        message_id = Messages.outbound['exercise_options']

        fields = [message_id, message_version, request_id,
                  contract.symbol, contract.security_type   , contract.last_trade_date_or_contract_month,
                  contract.strike, contract.right           , contract.multiplier, contract.exchange,
                  contract.currency, contract.local_symbol  , exercise_or_lapse,
                  exercise_quantity, account, override, contract.id, contract.trading_class]

        self.conn.send_message(fields)

    @check_connection
    def place_order(self, order_id: int, contract: Contract, order: Order):
        """
        Create the place_order message
        Send the message to the Bridge Application(TWS/IBGateway)

        :param order_id: Identifier for the Order
        :param contract: Contract Object used for info like symbol, strike, multiplier, expiration,
        :param order:
        :return:
        """

        # Gather the fields needed for the message
        message_id                          = Messages.outbound['place_order']
        message_version                     = 45
        last_trade_date_or_contract_month   = getattr(contract ,'last_trade_date_or_contract_month' , '')
        strike                              = getattr(contract ,'strike'                            , 0.0)
        right                               = getattr(contract ,'right'                             , '')
        multiplier                          = getattr(contract ,'multiplier'                        , '')

        aux_price                           = getattr(order ,   'aux_price'                 ,   '')
        volatility                          = getattr(order ,   'volatility'                ,   '')
        volatility_type                     = getattr(order ,   'volatility_type'           ,   '')
        delta_neutral_order_type            = getattr(order ,   'delta_neutral_order_type'  ,   '')
        delta_neutral_aux_price             = getattr(order ,   'delta_neutral_aux_price'   ,   '')
        continuous_update                   = getattr(order ,   'continuous_update'         ,   0)
        reference_price_type                = getattr(order ,   'reference_price_type'      ,   '')
        trail_stop_price                    = getattr(order ,   'trail_stop_price'          ,   '')
        trailing_percent                    = getattr(order ,   'trailing_percent'          ,   '')
        scale_init_level_size               = getattr(order ,   'scale_init_level_size'     ,   '')
        scale_subs_level_size               = getattr(order ,   'scale_subs_level_size'     ,   '')
        scale_price_increment               = getattr(order ,   'scale_price_increment'     ,   0.0)
        scale_table                         = getattr(order ,   'scale_table'               ,   '')

        fields      = [message_id, order_id, contract.id]
        fields +=   [
                    contract.symbol                     ,
                    contract.security_type              ,
                    last_trade_date_or_contract_month   ,
                    strike                              ,
                    right                               ,
                    multiplier                          ,
                    contract.exchange                   ,
                    contract.primary_exchange           ,
                    contract.currency                   ,
                    contract.local_symbol               ,
                    contract.trading_class              ,
                    contract.security_id_type           ,
                    contract.security_id                ,
                    order.action                        ,
                    order.total_quantity                ,
                    order.order_type                    ,
                    order.limit_price                   ,
                    aux_price                           ,
                    order.time_in_force                 ,
                    order.oca_group                     ,
                    order.account                       ,
                    order.open_close                    ,
                    order.origin                        ,
                    order.order_ref                     ,
                    order.transmit                      ,
                    order.parent_id                     ,
                    order.block_order                   ,
                    order.sweep_to_fill                 ,
                    order.display_size                  ,
                    order.trigger_method                ,
                    order.outside_rth                   ,
                    order.hidden]

        # Send combo legs for BAG requests (srv v8 and above)
        if contract.security_type == "BAG":
            combo_legs_count = len(contract.combo_legs) if contract.combo_legs else 0
            fields.append(combo_legs_count)
            if combo_legs_count > 0:
                for combo_leg in contract.combo_legs:
                    assert combo_leg
                    fields += [combo_leg.conId,
                               combo_leg.ratio,
                               combo_leg.action,
                               combo_leg.exchange,
                               combo_leg.openClose,
                               combo_leg.shortSaleSlot,
                               combo_leg.designatedLocation,
                               combo_leg.exemptCode]

        # Send order combo legs for BAG requests
        if contract.security_type == "BAG":
            order_combo_legs_count = len(order.order_combo_legs) if order.order_combo_legs else 0
            fields.append(order_combo_legs_count)

            if order_combo_legs_count:
                for orderComboLeg in order.order_combo_legs:
                    assert orderComboLeg
                    fields.append(orderComboLeg.price)

        if contract.security_type == "BAG":
            smartComboRoutingParamsCount = len(order.smart_combo_routing_params) if order.smart_combo_routing_params else 0
            fields.append(smartComboRoutingParamsCount)
            if smartComboRoutingParamsCount > 0:
                for tagValue in order.smart_combo_routing_params:
                    fields += [tagValue.tag, tagValue.value]

        ######################################################################
        # Send the shares allocation.
        #
        # This specifies the number of order shares allocated to each Financial
        # Advisor managed account. The format of the allocation string is as
        # follows:
        #                      <account_code1>/<number_shares1>,<account_code2>/<number_shares2>,...N
        # E.g.
        #              To allocate 20 shares of a 100 share order to account 'U101' and the
        #      residual 80 to account 'U203' enter the following share allocation string:
        #          U101/20,U203/80
        #####################################################################
        # send deprecated sharesAllocation field
        fields += ["",
                   order.discretionary_amt,
                   order.good_after_time,
                   order.good_till_date,

                   order.financial_advisers_group,
                   order.financial_advisers_method,
                   order.financial_advisers_percentage,
                   order.financial_advisers_profile,
                   order.model_code
                   ]


        # institutional Short Sale Slot Data
        fields += [order.short_sale_slot,  # 0 for retail, 1 or 2 for institutions
                   order.designated_location,  # populate only when short_sale_slot = 2.
                   order.exempt_code]

        fields.append(order.oca_type)

        fields += [order.rule80A,
                   order.settling_firm,
                   order.all_or_none,
                   order.min_qty,
                   order.percent_offset,
                   order.e_trade_only,
                   order.firm_quote_only,
                   order.nbbo_price_cap,
                   order.auction_strategy,
                   # AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
                   order.starting_price,
                   order.stock_ref_price,
                   order.delta,
                   order.stock_range_lower,
                   order.stock_range_upper,

                   order.override_percentage_constraints,

                   volatility,
                   volatility_type,
                   delta_neutral_order_type,
                   delta_neutral_aux_price]

        if hasattr(order,'delta_neutral_order_type'):
            fields += [order.delta_neutral_con_id               ,
                       order.delta_neutral_settling_firm        ,
                       order.delta_neutral_clearing_account     ,
                       order.delta_neutral_clearing_intent      ,
                       order.delta_neutral_open_close           ,
                       order.delta_neutral_short_sale           ,
                       order.delta_neutral_short_sale_slot      ,
                       order.delta_neutral_designated_location]

        fields += [continuous_update            ,
                   reference_price_type         ,
                   trail_stop_price             ,
                   trailing_percent             ,
                   scale_init_level_size        ,
                   scale_subs_level_size        ,
                   scale_price_increment]

        if hasattr(order,'scale_price_increment'): # TODO: add back this --> and scale_price_increment > 0:
            fields += [order.scale_price_adjust_value,
                       order.scale_price_adjust_interval,
                       order.scale_profit_offset,
                       order.scale_auto_reset,
                       order.scale_init_position,
                       order.scale_init_fill_qty,
                       order.scale_random_percent]


        fields += [scale_table, order.active_start_time, order.active_stop_time]

        # HEDGE orders
        fields.append(order.hedge_type)
        if order.hedge_type:
            fields.append(order.hedge_param)


        fields += [order.opt_out_smart_routing  ,
                   order.clearing_account       ,
                   order.clearing_intent        ,
                   order.not_held]


        if contract.delta_neutral_contract:
            fields += [True,
                       contract.delta_neutral_contract.conId,
                       contract.delta_neutral_contract.delta,
                       contract.delta_neutral_contract.price]
        else:
            fields.append(False)


        fields.append(order.algorithmic_strategy)
        if order.algorithmic_strategy:
            algo_params_count = len(order.algorithm_parameters) if order.algorithm_parameters else 0
            fields.append(algo_params_count)
            if algo_params_count > 0:
                for algoParam in order.algorithm_parameters:
                    fields += [algoParam.tag, algoParam.value]


        fields.append(order.algorithm_id)
        fields.append(order.what_if)

        # send miscOptions parameter
        miscOptionsStr = ""
        if order.order_misc_options:
            for tagValue in order.order_misc_options:
                miscOptionsStr += str(tagValue)
        fields.append(miscOptionsStr)


        fields.append(order.solicited)


        fields.extend([order.randomize_size, order.randomize_price])


        if order.order_type == "PEG BENCH":
            fields.extend([order.reference_contract_id, order.is_pegged_change_amount_decrease, order.pegged_change_amount,
                           order.reference_change_amount, order.reference_exchange_id])

            fields.append(len(order.conditions))

            if len(order.conditions) > 0:
                for cond in order.conditions:
                    fields.append(cond.type())
                    # TODO: make sure I ported logic in whatever happens 1 line below
                    # fields += cond.self.conn.make_message()

                fields.extend([order.conditions_ignore_rth, order.conditions_cancel_order])

            fields.extend([order.adjusted_order_type, order.trigger_price, order.limit_price_offset, order.adjusted_stop_price,
                           order.adjusted_trailing_amount, order.adjusted_trailing_unit])


        fields.append(order.ext_operator)
        fields.extend([order.softDollarTier.name, order.softDollarTier.val])
        fields.append(order.cash_qty)
        fields.append(order.mifid2DecisionMaker)
        fields.append(order.mifid2DecisionAlgo)
        fields.append(order.mifid2ExecutionTrader)
        fields.append(order.mifid2ExecutionAlgo)
        fields.append(order.dont_use_auto_price_for_hedge)
        fields.append(order.is_oms_container)
        fields.append(order.discrentionary_up_to_limit_price)
        fields.append(0) # TODO: Figure out missing field

        self.conn.send_message(fields)

    @check_connection
    def replace_financial_advisor(self, financial_advisor_data: int, cxml: str):
        """Call this function to modify FA configuration information from the
        API. Note that this can also be done manually in TWS itself.

        financial_advisor_data:int - Specifies the type of Financial Advisor
            configuration data beingingg requested. Valid values include:
            1 = GROUPS
            2 = PROFILE
            3 = ACCOUNT ALIASES
        cxml: str - The XML string containing the new FA configuration
            information.  """

        message_version = 1
        message_id = Messages.outbound['replace_fa']
        fields = [message_id, message_version, financial_advisor_data, cxml]
        self.conn.send_message(fields)

    @check_connection
    def request_account_updates(self, subscribe: bool, account_code: str):
        """Call this function to start getting account values, portfolio,


        subscribe:bool - If set to TRUE, the client will start receiving account
            and Portfolio updates. If set to FALSE, the client will stop
            receiving this information.
        account_code:str -The account code for which to receive account and
            portfolio updates."""
        message_version = 2
        message_id = Messages.outbound['request_acct_data']
        fields = [message_id, message_version, subscribe, account_code]
        self.conn.send_message(fields)


    @check_connection
    def request_account_updates_multi(self, request_id: int, account: str, model_code: str,
                                      ledger_and_nlv: bool):
        """Requests account updates for account and/or model."""

        message_version         = 1
        message_id              = Messages.outbound['request_account_updates_multi']
        fields                  = [message_id, message_version, request_id, account, model_code, ledger_and_nlv]
        self.conn.send_message(fields)

    @check_connection
    def request_account_summary(self, request_id: int,  tags: str, group_name: str='All'):
        """
        Sends a request to stream the data that appears in the TWS Account Window Summary Tab

        :param request_id: Unique identifier for this request
        :param tags: Single Value or list of Account Tags (see enum `AccountTag` for legal values
        :param group_name: set to All to return for all accounts, otherwise Financial Advisor group name (Default All)
        :return: None
        """
        message_version = 1
        message_id      = Messages.outbound['request_account_summary']
        fields          = [message_id, message_version, request_id, group_name, tags]
        self.conn.send_message(fields)

    @check_connection
    def request_all_open_orders(self):
        """Call this function to request the open orders placed from all
        clients and also from TWS. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  No association is made between the returned orders and the
        requesting client."""
        message_version = 1
        message_id = Messages.outbound['request_all_open_orders']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    @check_connection
    def request_auto_open_orders(self, auto_bind: bool):
        """Call this function to request that newly created TWS orders
        be implicitly associated with the client. When a new TWS order is
        created, the order will be associated with the client, and fed back
        through the openOrder() and orderStatus() functions on the EWrapper.

        Note:  This request can only be made from a client with client_id of 0.

        auto_bind: If set to TRUE, newly created TWS orders will be implicitly
        associated with the client. If set to FALSE, no association will be
        made.

        """
        message_version = 1
        message_id = Messages.outbound['request_auto_open_orders']
        fields = [message_id, message_version, auto_bind]
        message_sent = self.conn.send_message(fields)
        return message_sent

    def request_contract_data(self, contract: Contract, request_id=None):
        """
        Creates a request_contract_data message
        Sends the message to the Bridge

        :param contract: Contract to get data about
        :param request_id: Unique Identifier for this Request
        :return:
        """

        if request_id is None:
           request_id = self.get_local_request_id()

        # send req market data msg
        message_version = 8

        # Handle the Fields that may not exist in a contract
        last_trade_date_or_contract_month = ''
        if hasattr(contract, 'last_trade_date_or_contract_month'):
            last_trade_date_or_contract_month = contract.last_trade_date_or_contract_month

        multiplier = ''
        if hasattr(contract,'multiplier'):
            multiplier = contract.multiplier
        right = ''
        if hasattr(contract, 'right'):
            right = contract.right

        strike = ''
        if hasattr(contract, 'strike'):
            strike = contract.strike

        message_id = Messages.outbound['request_contract_data']
        fields = [message_id, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, last_trade_date_or_contract_month,strike, right,
                  multiplier,contract.exchange, contract.primary_exchange,contract.currency, contract.local_symbol,
                  contract.trading_class,contract.include_expired,  contract.security_id_type, contract.security_id]

        self._send_message(fields)
        return request_id

    def request_current_time(self):
        """Asks the current system time on the server side.

        Related Response Messages
        IN.CURRENT_TIME
        """
        message_version = 1
        message_id = Messages.outbound['request_current_time']
        fields = [message_id, message_version]
        self._send_message(fields)

    def request_executions(self, request_id: int, client_id="", account_code="", time="",
                           symbol="", security_type="", exchange="", side=""):

        """When this function is called, the execution reports that meet the
        filter criteria are downloaded to the client via the execDetails()
        function. To view executions beyond the past 24 hours, open the
        Trade Log in TWS and, while the Trade Log is displayed, request
        the executions again from the API.

        request_id:int - The ID of the data request. Ensures that responses are
            matched to requests if several requests are in process.
        execFilter:ExecutionFilter - This object contains attributes that
            describe the filter criteria used to determine which execution
            reports are returned.

        NOTE: Time format must be 'yyyymmdd-hh:mm:ss' Eg: '20030702-14:55'"""

        # Create and Send the Message
        message_version = 3
        message_id = Messages.outbound['request_executions']
        fields = [ message_id, message_version, request_id, client_id, account_code, time,
                   symbol, security_type, exchange, side]
        self._send_message(fields)

    @check_connection
    def request_global_cancel(self):
        """Use this function to cancel all open orders globally. It
        cancels both API and TWS open orders.

        If the order was created in TWS, it also gets canceled. If the order
        was initiated in the API, it also gets canceled."""

        message_version = 1
        message_id = Messages.outbound['request_global_cancel']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    # Note that formatData parameter affects intraday bars only
    # 1-day bars always return with date in YYYYMMDD format
    @check_connection
    def request_head_time_stamp(self,
                                request_id      : int       ,
                                contract        : Contract  ,
                                what_to_show    : str       ,
                                use_rth         : int       ,
                                format_date     : int):
        """
        Creates a 'request_head_timestamp' message and sends the message to the bridge

        :param request_id:
        :param contract:
        :param what_to_show:
        :param use_rth:
        :param format_date:
        :return:
        """

        # Handle Optional Contract Fields
        fields = self._get_optional_fields(contract)


        message_id = Messages.outbound['request_head_time_stamp']
        fields = [message_id, request_id, contract.id, contract.symbol, contract.security_type,
                  fields['last_trade_date_or_contract_month'], fields['strike'], fields['right'], fields['multiplier'],
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class,
                  contract.include_expired, use_rth, what_to_show, format_date]
        self.conn.send_message(fields)

    @check_connection
    def request_historical_news(self, request_id: int, conId: int, providerCodes: str,
                                startDateTime: str, end_date_time: str, totalResults: int, historicalNewsOptions: list):

        message_id = Messages.outbound['request_historical_news']
        fields = [message_id, request_id, conId, providerCodes, startDateTime, end_date_time, totalResults]

        # send historicalNewsOptions parameter
        if self.server_version() >= MIN_SERVER_VER_NEWS_QUERY_ORIGINS:
            func_options = ""
            if historicalNewsOptions:
                for tagValue in historicalNewsOptions:
                    func_options += str(tagValue)
            fields.append(func_options)

        self.conn.send_message(fields)

    @check_connection
    def request_historical_ticks(self, request_id: int, contract: Contract, start_date_time: str,
                                 end_date_time: str, number_of_ticks: int, what_to_show: str, useRth: int,
                                 ignore_size: bool, misc_options: list):

        misc_options_string = ""
        if misc_options:
            for tagValue in misc_options:
                misc_options_string += str(tagValue)

        message_id = Messages.outbound['request_historical_ticks']
        fields = [message_id, request_id, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class,
                  contract.include_expired, start_date_time, end_date_time, number_of_ticks, what_to_show, useRth,
                  ignore_size, misc_options_string]
        self.conn.send_message(fields)

    @check_connection
    def request_managed_accounts(self):
        """Call this function to request the list of managed accounts. The list
        will be returned by the managedAccounts() function on the EWrapper.

        Note:  This request can only be made when connected to a FA managed account."""

        message_version = 1
        message_id = Messages.outbound['request_managed_accounts']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    @check_connection
    def request_market_data_type(self, market_data_type: int):
        """The API can receive frozen market data from Trader
        Workstation. Frozen market data is the last data recorded in our system.
        During normal trading hours, the API receives real-time market data. If
        you use this function, you are telling TWS to automatically switch to
        frozen market data after the close. Then, before the opening of the next
        trading day, market data will automatically switch back to real-time
        market data.

        market_data_type:int - 1 for real-time streaming market data or 2 for
            frozen market data"""

        # Create and send the message
        message_version = 1
        message_id = Messages.outbound['request_market_data_type']
        fields = [message_id, message_version, market_data_type]
        self.conn.send_message(fields)

    @check_connection
    def request_market_depth_exchanges(self):
        """

        :return:
        """

        message_id = Messages.outbound['request_market_depth']
        fields = [message_id]
        self.conn.send_message(fields)

    @check_connection
    def request_market_rule(self, market_rule_id: int):
        """
        Create the 'request_market_rule' Message
        Send the message to the Bridge

        :param market_rule_id:
        :return:
        """

        message_id = Messages.outbound['request_market_rule']
        fields = [message_id, market_rule_id]
        self.conn.send_message(fields)

    @check_connection
    def request_news_providers(self):
        """
        Request a list of news providers.

        :return: True/False - True if message was sent, False otherwise
        """

        message_id = Messages.outbound['request_news_providers']
        fields = [message_id]
        message_sent = self.conn.send_message(fields)
        return message_sent

    @check_connection
    def request_open_orders(self):
        """Call this function to request the open orders that were
        placed from this client. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  The client with a client_id of 0 will also receive the TWS-owned
        open orders. These orders will be associated with the client and a new
        order_id will be generated. This association will persist over multiple
        API and TWS sessions.  """

        message_version = 1
        message_id = Messages.outbound['request_open_orders']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    @check_connection
    def request_positions(self):
        """Requests real-time position data for all accounts."""

        message_version = 1
        message_id = Messages.outbound['request_positions']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    @check_connection
    def request_positions_multi(self, request_id: int, account: str, model_code: str):
        """
        Requests positions for account and/or model.
        """

        message_version = 1
        message_id = Messages.outbound['request_positions_multi']
        fields = [message_id, message_version, request_id, account, model_code]
        self.conn.send_message(fields)

    @check_connection
    def request_smart_components(self, request_id: int, bboExchange: str):

        message_id  = Messages.outbound['request_smart_components']
        fields      = [message_id, request_id, bboExchange]
        self.conn.send_message(fields)

    @check_connection
    def set_server_log_level(self, log_level: int):
        """The default detail level is ERROR. For more details, see API
        Logging."""

        message_version = 1
        message_id = Messages.outbound['set_server_log_level']
        fields = [message_id, message_version, log_level]
        self.conn.send_message(fields)

    @check_connection
    def start_api(self):
        """  Initiates the message exchange between the client application and
        the TWS/IB Gateway. """
        message_version = 2
        message_id = Messages.outbound['start_api']
        fields = [message_id, message_version, self.client_id, self.optional_capabilities]
        self.conn.send_message(fields)


    @check_connection
    def subscribe_to_group_events(self,
                                  request_id: int,
                                  group_id  : int):
        """
        Associate a prior request to a display group

        :param request_id: Unique identifier for this request
        :param group_id: The ID of the group, currently it is a number from 1 to 7.
        :return:
        """
        message_version = 1
        message_id = Messages.outbound['subscribe_to_group_events']
        fields = [message_id, message_version, request_id, group_id]
        self.conn.send_message(fields)

    def connect(self, host, port, client_id):
        """
        This function must be called before any other. There is no
        feedback for a successful connection, but a subsequent attempt to
        connect will return the message \"Already connected.\"

        host:str - The host name or IP address of the machine where TWS is
            running. Leave blank to connect to the local host.
        port:int - Must match the port specified in TWS on the
            Configure>API>Socket Port field.
        client_id:int - A number used to identify this client connection. All
            orders placed/modified from this client will be associated with
            this client identifier.

            Note: Each client MUST connect with a unique client_id."""

        # Establish connection to the bridge (TWS/IBGW)
        self.api_state = "Establishing Connection to the Bridge Application(TWS/IB Gateway)"
        self.host = host
        self.port = port
        self.client_id = client_id
        logger.info("Connecting to %s:%d w/ id:%d", self.host, self.port, self.client_id)
        self.conn = BridgeConnection(self.host, self.port)

        try:
            self.conn.connect()

            # Send a message to connect to the Bridge (No response is given)
            v100prefix = "API\0"
            v100version = "v%d..%d" % (MIN_CLIENT_VER, MAX_CLIENT_VER)
            msg = self.conn.make_msg(v100version)
            msg = str.encode(v100prefix, 'ascii') + msg
            self.conn.send_message(msg)

            message = self.conn.receive_messages(False)[0]
            (server_version, conn_time) = message

            self.connection_time = conn_time
            logger.info("Connection Time: {0}".format(self.connection_time))

            self.server_version_ = int(server_version)
            logger.info("Server Version: {0}".format(self.server_version_))

            self.start_api()
            logger.info("Connected to %s:%d w/ id:%d", self.host, self.port, self.client_id)

        except socket.error:
            logging.error(socket.error)
            self.api_state  = "Disconnected from the Bridge Application(TWS/IB Gateway)."

    def request_historical_data(self,
                                request_id      : int       ,
                                contract        : Contract  ,
                                end_date_time   : str       ,
                                duration        : str       ,
                                bar_size_setting            ,
                                what_to_show                ,
                                use_rth         : int       ,
                                format_date     : int       ,
                                keep_up_to_date : bool      ,
                                chart_options   : list):
        """
        Make the 'historical_data' message
        Send the message to the Bridge
        :param request_id: Unique Identifier for this request
        :param contract: Contract that we are interested in getting historical data from
        :param end_date_time: 
        :param duration: 
        :param bar_size_setting: string or `BarSize` enum
        :param what_to_show: String or `Show` enum
        :param use_rth: 
        :param format_date: 
        :param keep_up_to_date: 
        :param chart_options: Not sure what this is yet
        :return: 
        """
        """Requests contracts' historical data. When requesting historical data, a
        finishing time and date is required along with a duration string. The
        resulting bars will be returned in EWrapper.historicalData()

        request_id:int - The id of the request. Must be a unique value. When the
            market data returns, it whatToShowill be identified by this tag. This is also
            used when canceling the market data.
        contract:Contract - This object contains a description of the contract for which
            market data is being requested.
        end_date_time:str - Defines a query end date and time at any point during the past 6 mos.
            Valid values include any date/time within the past six months in the format:
            yyyymmdd HH:mm:ss ttt

            where "ttt" is the optional time zone.
        durationStr:str - Set the query duration up to one week, using a time unit
            of seconds, days or weeks. Valid values include any integer followed by a space
            and then S (seconds), D (days) or W (week). If no unit is specified, seconds is used.

        useRTH:int - Determines whether to return all data available during the requested time span,
            or only data that falls within regular trading hours. Valid values include:

            0 - all data is returned even where the market in question was outside of its
            regular trading hours.
            1 - only data within the regular trading hours is returned, even if the
            requested time span falls partially or completely outside of the RTH.
        formatDate: int - Determines the date format applied to returned bars. validd values include:

            1 - dates applying to bars returned in the format: yyyymmdd{space}{space}hh:mm:dd
            2 - dates are returned as a long integer specifying the number of seconds since
                1/1/1970 GMT.
        """

        # Create Message
        message_id = Messages.outbound['request_historical_data']

        # Handle cases where the representing Enum is passed in instead of a string
        if isinstance(bar_size_setting,Enum):
            bar_size_setting = bar_size_setting.value

        if isinstance(what_to_show,Enum):
            what_to_show = what_to_show.value

        # Stocks don't have these attributes, if they don't exist empty values are passed instead as the Bridge expects
        last_trade_date_or_contract_month = ""
        if hasattr(contract,'last_trade_date_or_contract_month'):
            last_trade_date_or_contract_month = contract.last_trade_date_or_contract_month

        right = ""
        if hasattr(contract, 'right'):
            right = contract.right

        strike = ""
        if hasattr(contract, 'strike'):
            strike = contract.strike

        multiplier = ""
        if hasattr(contract,'multiplier'):
            multiplier = contract.multiplier

        fields = [message_id, request_id, contract.id, contract.symbol, contract.security_type,
                    last_trade_date_or_contract_month,strike, right, multiplier, contract.exchange,
                    contract.primary_exchange, contract.currency, contract.local_symbol, contract.trading_class,
                    contract.include_expired,end_date_time, bar_size_setting, duration, use_rth, what_to_show, format_date]


       # Send combo legs for BAG requests
        if contract.security_type == "BAG":
            fields.append(len(contract.combo_legs))
            for combo_leg in contract.combo_legs:
                fields.append(combo_leg.contract_id)
                fields.append(combo_leg.ratio)
                fields.append(combo_leg.action)
                fields.append(combo_leg.exchange)


        fields.append(keep_up_to_date)

        # send chartOptions parameter
        chart_options_str = ""
        if chart_options:
            for tagValue in chart_options:
                chart_options_str += str(tagValue)
        fields.append(chart_options_str)

        # Send the Message
        self._send_message(fields)

    @check_connection
    def request_news_bulletins(self, all_messages: bool):
        """
        Request to receive news bulletins.
        
        :param all_messages: If set to TRUE, returns all the existing bulletins for the current day
                             If set to FALSE, will only return new bulletins.
        :return:
        """
        message_version = 1
        message_id      = Messages.outbound['request_news_bulletins']
        fields          = [message_id, message_version, all_messages]
        self.conn.send_message(fields)

    @check_connection
    def request_pnl(self, request_id: int, account: str, model_code: str):

        message_id  = Messages.outbound['request_pnl']
        fields      = [message_id, request_id, account, model_code]
        self.conn.send_message(fields)

    @check_connection
    def request_pnl_single(self, request_id: int, account: str, model_code: str, contract_id: int):
        message_id = Messages.outbound['request_pnl_single']
        fields = [message_id, request_id, account, model_code, contract_id]
        self.conn.send_message(fields)

    @check_connection
    def request_tick_by_tick_data(self,
                                  request_id        : int,
                                  contract          : Contract,
                                  tick_type         : str,
                                  number_of_ticks   : int,
                                  ignore_size       : bool):

        message_id = Messages.outbound['request_tick_by_tick_data']
        fields = [message_id, request_id, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class, tick_type, number_of_ticks, ignore_size
                  ]

        self.conn.send_message(fields)

    def server_version(self):
        """Returns the version of the TWS instance to which the API
        application is connected."""

        return self.server_version_

    def verify_request(self, api_name: str, api_version: str):
        """
        Allows for an application to request what the correct message should be for a given api/version.
        """


        #if not self.extra_auth:
        #    self.response_handler.error(NO_VALID_ID, BAD_MESSAGE.code(), BAD_MESSAGE.msg() +
        #                                "  Intent to authenticate needs to be expressed during initial connect request.")
        #    return

        message_version = 1
        message_id = Messages.outbound['verify_request']
        fields = [message_id, message_version, api_name, api_version]
        self._send_message(fields)

    @check_connection
    def request_market_data(self,
                            request_id          : int,
                            contract            : Contract,
                            generic_tick_list   : str,
                            snapshot            : bool,
                            regulatory_snapshot : bool,
                            market_data_options : list):
        """
        Start streaming market data. Will result in 'tick_price' and 'tick_size' inbound messages being generated.

        :param request_id: Unique Identifier for this request
        :param contract:
        :param generic_tick_list: List of Tick Types. See the enum TickType for legal values.
        :param snapshot: Check to return a single snapshot of Market data ave the market data subscription cancel
        :param regulatory_snapshot: With the US Value Snapshot Bundle for stocks, these are available for 0.01 USD each.
        :param market_data_options: For internal use only. Use default XYZ
        :return: None
        """


        """Call this function to request market data. The market data
                will be returned by the tickPrice and tickSize events.

                request_id: int - The ticker id. Must be a unique value. When the
                    market data returns, it will be identified by this tag. This is
                    also used when canceling the market data.
                contract:Contract - This structure contains a description of the
                    Contractt for which market data is being requested.
                genericTickList:str - A commma delimited list of generic tick types.
                    Tick types can be found in the Generic Tick Types page.
                    Prefixing w/ 'mdoff' indicates that top market data shouldn't tick.
                    You can specify the news source by postfixing w/ ':<source>.
                    Example: "mdoff,292:FLY+BRF"
                snapshot:bool - Check to return a single snapshot of Market data and
                    have the market data subscription cancel. Do not enter any
                    genericTicklist values if you use snapshots.
        """


        message_version = 11

        # send req market data msg
        message_id = Messages.outbound['request_market_data']
        fields = [message_id, message_version, request_id, contract.id, contract.symbol, contract.security_type,
                          contract.last_trade_date_or_contract_month,
                          contract.strike, contract.right, contract.multiplier, contract.exchange,
                          contract.primary_exchange,
                          contract.currency, contract.local_symbol, contract.trading_class]


        # Send Combo Legs for BAG Requests
        if contract.security_type == "BAG":
            combo_leg_count = len(contract.combo_legs) if contract.combo_legs else 0
            fields.append(combo_leg_count)
            for combo_leg in contract.combo_legs:
                fields.append(combo_leg.conId)
                fields.append(combo_leg.ratio)
                fields.append(combo_leg.action)
                fields.append(combo_leg.exchange)

        # Send Delta Neutral Contract Fields
        if contract.delta_neutral_contract:
            fields.append(True)
            fields.append(contract.delta_neutral_contract.conId)
            fields.append(contract.delta_neutral_contract.delta)
            fields.append(contract.delta_neutral_contract.price)
        else:
            fields.append(False)


        # TODO: Clarify what market_data_options is for
        market_data_options = ""
        fields.extend([generic_tick_list, snapshot, regulatory_snapshot, market_data_options])

        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    def tws_connection_time(self):
        """Returns the time the API application made a connection to TWS."""

        return self.connection_time


    @check_connection
    def request_order_ids(self):
        """
        Construct the request_order_ids message
        Send the message to the Bridge application

        :return:
        """

        num_ids         = 1 # Deprecated field that is still expected but ignored in the message
        message_version = 1
        message_id      = Messages.outbound['request_order_ids']
        fields = [message_id, message_version, num_ids]
        self.conn.send_message(fields)

    @check_connection
    def request_market_depth(self,
                             request_id             : int       ,
                             contract               : Contract  ,
                             num_rows               : int       ,
                             is_smart_depth         : bool      ,
                             market_depth_options   : list
                             ):
        """

        :param request_id: Unique identifier for this request
        :param contract:
        :param num_rows:
        :param is_smart_depth:
        :param market_depth_options:
        :return:
        """
        """Call this function to request market depth for a specific
        contract. The market depth will be returned by the updateMktDepth() and
        updateMktDepthL2() events.

        Requests the contract's market depth (order book). Note this request must be
        direct-routed to an exchange and not smart-routed. The number of simultaneous
        market depth requests allowed in an account is calculated based on a formula
        that looks at an accounts equity, commissions, and quote booster packs.

        request_id:int - The ticker id. Must be a unique value. When the market
            depth data returns, it will be identified by this tag. This is
            also used when canceling the market depth
        contract:Contact - This structure contains a description of the contract
            for which market depth data is being requested.
        num_rows:int - Specifies the numRowsumber of market depth rows to display.
        is_smart_depth:bool - specifies SMART depth request
        market_depth_options:list - For internal use only. Use default value
            XYZ."""

        message_version = 5
        message_id = Messages.outbound['request_market_depth']
        # send req market depth msg
        fields = [  message_id                                  ,   message_version         ,
                    request_id                                  ,   contract.id             ,
                    contract.symbol                             ,   contract.security_type  ,
                    contract.last_trade_date_or_contract_month  ,   contract.strike         ,
                    contract.right                              ,   contract.multiplier     ,
                    contract.exchange                           ,   contract.currency       ,
                    contract.local_symbol                       ,   contract.trading_class  ,
                    num_rows                                    ,   is_smart_depth          ,
                ]

        # send market_depth_options parameter
        if self.server_version() >= MIN_SERVER_VER_LINKING:
            # current doc says this part if for "internal use only" -> won't support it
            if market_depth_options:
                raise NotImplementedError("not supported")
            mktDataOptionsStr = ""
            fields += [mktDataOptionsStr, ]

        self.conn.send_message(fields)

    @check_connection
    def cancel_news_bulletins(self):
        """Call this function to stop receiving news bulletins."""

        message_version = 1
        message_id = Messages.outbound['cancel_news_bulletins']
        fields = [message_id, message_version]
        self.conn.send_message(fields)

    @check_connection
    def request_financial_advisor(self, financial_advisor_data: int):
        """
        Requests Financial Advisor Configuration Information.
        The data returns in an XML string via a "receiveFA" ActiveX event.

        :param financial_advisor_data:  Specifies the type of Financial Advisor. See the enum FinancialAdvisor for legal values.
        :return: None
        """
        #Create the Message
        message_version = 1
        message_id      = Messages.outbound['request_fa']
        fields          = [message_id, message_version, int(financial_advisor_data)]

        self.conn.send_message(fields)

    @check_connection
    def cancel_historical_data(self, request_id: int):
        """Used if an internet disconnect has occurred or the results of a query
        are otherwise delayed and the application is no longer interested in receiving
        the data.

        request_id:int - The ticker ID. Must be a unique value."""
        message_version = 1
        message_id = Messages.outbound['cancel_historical_data']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def cancel_head_time_stamp(self, request_id: int):
        """

        :param request_id:
        :return:
        """
        message_id = Messages.outbound['cancel_head_timestamp']
        fields = [message_id, request_id]
        self.conn.send_message(fields)

    @check_connection
    def request_histogram_data(self, ticker_id: int, contract: Contract,
                               use_real_time_hours: bool, time_period: str):

        message_id = Messages.outbound['request_histogram_data']
        fields = [message_id, ticker_id, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class, contract.include_expired, use_real_time_hours,
                  time_period]
        self.conn.send_message(fields)

    @check_connection
    def cancel_histogram_data(self, request_id: int):
        message_id = Messages.outbound['cancel_histogram_data']
        fields = [message_id, request_id]
        self.conn.send_message(fields)

    @check_connection
    def request_scanner_parameters(self):
        """Requests an XML string that describes all possible scanner queries."""

        #if not self.conn.is_connected():
        #    self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
        #    return

        message_version = 1
        message_id = Messages.outbound['request_scanner_parameters']
        fields = [message_id, message_version]
        self.conn.send_message(fields)


    @check_connection
    def request_scanner_subscription(self,
                                     request_id       : int           ,
                                     scanner          : Scanner       ,
                                     scanner_options  : list          ,
                                     filter_options   : list
                                     ):
        """

        :param request_id: Unique identifier for this request
        :param scanner:
        :param scanner_options:
        :param filter_options:
        :return:
        """
        """request_id:int - Identifier for the given request
        scannerSubscription:Scanner - This structure contains
            possible parameters used to filter results.
        scanner_subscription_options:list - For internal use only.
            Use default value XYZ."""

        message_version = 4
        message_id = Messages.outbound['request_scanner_subscription']
        fields = [message_id]

        fields += [request_id,
                   scanner.numberOfRows                 ,
                   scanner.instrument                   ,
                   scanner.location_code                ,
                   scanner.scan_code                    ,
                   scanner.above_price                  ,
                   scanner.below_price                  ,
                   scanner.above_volume                 ,
                   scanner.market_cap_above             ,
                   scanner.market_cap_below             ,
                   scanner.moody_rating_above           ,
                   scanner.moody_rating_below           ,
                   scanner.sp_rating_above              ,
                   scanner.sp_rating_below              ,
                   scanner.maturity_date_above          ,
                   scanner.maturity_date_below          ,
                   scanner.coupon_rate_above            ,
                   scanner.coupon_rate_below            ,
                   scanner.exclude_convertible          ,
                   scanner.average_option_volume_above  ,
                   scanner.scanner_setting_pairs,
                   scanner.stock_type_filter]

        # send scannerSubscriptionFilterOptions parameter
        filter_options_str = ""
        if filter_options:
            for tagValueOpt in filter_options:
                filter_options_str += str(tagValueOpt)
        fields += [filter_options_str]

        # send scanner_scanner_options parameter
        scanner_options_str = ""
        if scanner_options:
            for tagValueOpt in scanner_options:
                scanner_options_str += str(tagValueOpt)
        fields += [scanner_options_str, ]

        self.conn.send_message(fields)

    @check_connection
    def request_real_time_bars(self,
                                request_id          : int,
                                contract            : Contract,
                                bar_size            : int,
                                what_to_show        : str,
                                use_rth             : bool,
                                real_time_bars_options : list):
        """
        Send a request to start streaming real time bar
        :param request_id:
        :param contract:
        :param bar_size:
        :param what_to_show:
        :param use_rth:
        :param real_time_bars_options:
        :return: None
        """
        """Call the reqRealTimeBars() function to start receiving real time bar
        results through the realtimeBar() EWrapper function.

        request_id:int - The Id for the request. Must be a unique value. When the
            data is received, it will be identified by this Id. This is also
            used when canceling the request.
        contract:Contract - This object contains a description of the contract
            for which real time bars are being requested
        bar_size:int - Currently only 5 second bars are supported, if any other
            value is used, an exception will be thrown.
        what_to_show:str - Determines the nature of the data extracted. Valid
            values include:
            TRADES
            BID
            ASK
            MIDPOINT
        use_rth:bool - Regular Trading Hours only. Valid values include:
            0 = all data available during the time span requested is returned,
                including time intervals when the market in question was
                outside of regular trading hours.
            1 = only data within the regular trading hours for the product
                requested is returned, even if the time time span falls
                partially or completely outside.
        realTimeBarOptions:list - For internal use only. Use default value XYZ."""

        message_version = 3
        message_id = Messages.outbound['request_real_time_bars']
        fields = [message_id, message_version, request_id, contract.id,
                  contract.symbol, contract.security_type, contract.last_trade_date_or_contract_month,
                  contract.strike, contract.right, contract.multiplier, contract.exchange,
                  contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class, bar_size, what_to_show, use_rth]

        # send real_time_bars_options parameter
        realTimeBarsOptionsStr = ""
        if real_time_bars_options:
            for tagValueOpt in real_time_bars_options:
                realTimeBarsOptionsStr += str(tagValueOpt)
        fields += [realTimeBarsOptionsStr, ]

        self.conn.send_message(fields)


    def request_fundamental_data(self, request_id: int, contract: Contract,
                                 report_type: str, request_options: list):
        """
        Request Fundamental Data for a stock.
        The appropriate market data subscription must be set up in Account Management before you can receive this data.
        Contract.id can be specified in the Contract object but not trading_class or multiplier.
        This is because reqFundamentalData()   is used only for stocks and stocks do not have a multiplier and
        trading class.

        Response Messages
        IN.FUNDAMENTAL_DATA - The Requested Data


        reqFundamentalData() can handle contract_id specified in the Contract object,
        but not trading_class or multiplier. This is because reqFundamentalData()
        is used only for stocks and stocks do not have a multiplier and
        trading class.

        request_id:int - The ID of the data request. Ensures that responses are
             matched to requests if several requests are in process.
        contract:Contract - This structure contains a description of the
            contract for which fundamental data is being requested.
        report_type:str - One of the following XML reports:
            ReportSnapshot (company overview)
            ReportsFinSummary (financial summary)
            ReportRatios (financial ratios)
            ReportsFinStatements (financial statements)
            RESC (analyst estimates)
            CalendarReport (company calendar) """

        logger.info("Request #{0} - Calling request_fundamental_data".format(request_id))
        # Create the message body
        message_version = 2
        message_id = Messages.outbound['request_fundamental_data']
        fields = [message_id, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, contract.exchange, contract.primary_exchange, contract.currency,
                  contract.local_symbol, report_type]

        request_options_str = ""
        tag_values_count = len(request_options) if request_options else 0
        if request_options:
            for fundDataOption in request_options:
                request_options_str += str(fundDataOption)
        fields.extend([tag_values_count, request_options_str])

        # Make the actual request
        self._send_message(fields)

    @check_connection
    def request_news_article(self, request_id: int, provider_code: str, articleId: str, news_article_options: list):

        fields = []
        message_id = Messages.outbound['request_news_article']
        fields += [message_id, request_id, provider_code, articleId]

        # send news_article_options parameter

        newsArticleOptionsStr = ""
        if news_article_options:
            for tagValue in news_article_options:
                newsArticleOptionsStr += str(tagValue)

            fields.append(newsArticleOptionsStr)

        self.conn.send_message(fields)

    @check_connection
    def query_display_groups(self, request_id: int):
        """API requests used to integrate with TWS color-grouped windows (display groups).
        TWS color-grouped windows are identified by an integer number. Currently that number ranges from 1 to 7 and are mapped to specific colors, as indicated in TWS.

        request_id:int - The unique number that will be associated with the
            response """

        message_version = 1
        message_id = Messages.outbound['query_display_groups']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def update_display_group(self, request_id: int, contract_info: str):
        """

        :param request_id:
        :param contract_info:
        :return: None
        """
        """request_id:int - The requestId specified in subscribeToGroupEvents().
        contract_info:str - The encoded value that uniquely represents the
            contract in IB. Possible values include:

            none = empty selection
            contractID@exchange - any non-combination contract.
                Examples: 8314@SMART for IBM SMART; 8314@ARCA for IBM @ARCA.
            combo = if any combo is selected."""

        message_version = 1
        message_id = Messages.outbound['update_display_group']
        fields = [message_id, message_version, request_id, contract_info]
        self.conn.send_message(fields)

    @check_connection
    def unsubscribe_from_group_events(self, request_id: int):
        """request_id:int - The requestId specified in subscribeToGroupEvents()."""

        message_version = 1
        message_id = Messages.outbound['unsubscribe_from_group_events']
        fields = [message_id, message_version, request_id]
        self.conn.send_message(fields)

    @check_connection
    def verify_message(self, api_data: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        message_version = 1
        message_id = Messages.outbound['verify_message']
        fields = [message_id, message_version, api_data]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    @check_connection
    def verify_and_auth_request(self, api_name: str, api_version: str,
                                opaque_is_vkey: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""

        if not self.extra_auth:
            self.response_handler.error(NO_VALID_ID, BAD_MESSAGE.code(), BAD_MESSAGE.msg() +
                                        "  Intent to authenticate needs to be expressed during initial connect request.")
            return

        message_version = 1
        message_id = Messages.outbound['verify_and_auth_request']
        fields = [message_id, message_version, api_name, api_version, opaque_is_vkey]
        self.conn.send_message(fields)

    @check_connection
    def verify_and_auth_message(self, api_data: str, xyzResponse: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""

        message_version     = 1
        message_id          = Messages.outbound['verify_and_auth_message']
        fields              = [message_id, message_version, api_data, xyzResponse]
        message             = self.conn.make_message(fields)
        self.conn.send_message(message)

    @check_connection
    def request_security_definition_option_parameters(self, request_id: int, underlying_symbol: str,
                                                      futFopExchange: str, underlying_security_type: str,
                                                      underlying_contract_id: int):
        """Requests security definition option parameters for viewing a
        contract's option chain request_id the ID chosen for the request
        underlying_symbol futFopExchange The exchange on which the returned
        options are trading. Can be set to the empty string "" for all
        exchanges. underlying_security_type The type of the underlying security,
        i.e. STK underlying_contract_id the contract ID of the underlying security.
        Response comes via EWrapper.securityDefinitionOptionParameter()
        """

        message_id = Messages.outbound['request_security_definition_option_parameters']
        fields = [message_id, request_id, underlying_symbol,
                  futFopExchange, underlying_security_type, underlying_contract_id]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    @check_connection
    def request_soft_dollar_tiers(self, request_id: int):
        """
        Requests pre-defined Soft Dollar Tiers.
        This is only supported for registered professional advisers, hedge funds, and mutual funds who have
        configured Soft Dollar Tiers in Account Management.
        """

        message_id = Messages.outbound['request_soft_dollar_tiers']
        fields = [message_id, request_id]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    @check_connection
    def request_family_codes(self):
        """
        Get Information on Related Accounts (aka "Family Codes")
        :return:
        """

        message_id = Messages.outbound['request_family_codes']
        fields = [message_id]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    @check_connection
    def request_matching_symbols(self, request_id: int, pattern: str):
        """

        :param request_id:
        :param pattern:
        :return:
        """
        # Create and send the Message

        message_id = Messages.outbound['request_matching_symbols']
        fields = [message_id, request_id, pattern]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)