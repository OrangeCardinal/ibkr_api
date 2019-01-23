"""
IBKR_API is the simplest interface available. 
The Bridge returns data in an asynchronous manner and on top of that one request for many requests results in several
messages of varying message types. This class hides all this complexity from the end user and allows for easy tasks to be
automated. For more advanced usage please see the ClientApplication and MultiClientApplication classes. 

The main class to use from API user's point of view.
It takes care of almost everything:
- creating the connection to TWS/IB Gateway
- executing api requests
- gathering and returning the api response data
"""
from functools import wraps

import datetime
import logging
import time

from ibkr_api.base.api_calls                import ApiCalls
from ibkr_api.base.messages                 import Messages
from ibkr_api.base.message_parser           import MessageParser

from ibkr_api.classes.contracts.contract    import Contract
from ibkr_api.classes.orders.order import Order
from ibkr_api.classes.scanner               import Scanner

logger = logging.getLogger(__name__)

def drop_message_id_and_request_id(func):
    """
    Drops the message id and request id values and only returns the 'actual' data a user expects

    :param func: Original Function
    :return: Function with modified return values
    """
    @wraps(func)
    def new_func(self, *func_args,**func_kwargs):
        data = func(self, *func_args, **func_kwargs)

        # Strip out any Message ID and Request ID values which are not needed for this call
        if isinstance(data,list) and len(data) > 1:
            real_return_value = []
            for item in data:
                if item[2] is not None:
                    real_return_value.append(item[2])
        elif isinstance(data,list) or isinstance(data,tuple):
            real_return_value = data[2]
        else:
            real_return_value = data

        # If there is only one element in the array, return the element not the array
        if real_return_value is None:
            return None
        elif isinstance(real_return_value,list) and len(real_return_value) == 1:
            return real_return_value[0]
        else:
            return real_return_value
    return new_func

class IBKR_API(ApiCalls):
    def __init__(self, host, port, client_id:int=0, message_timeout:int=2):
        # Each application connected to the bridge must have a unique identifier
        self.client_id              = client_id

        # Governs how long to wait for a response from the Bridge
        self.message_timeout        = message_timeout

        # Stores any message that was skipped during processing (which is a byproduct of hiding the asynchronous design)
        self.unprocessed_messages   = []

        super().__init__()
        super().connect(host, port, client_id)

    def _process_response(self, inbound_message_name, end_on_codes=[]):
        """

        :param inbound_message_name: String or list of strings.
               The last element of the list is considered the flag to trigger the end of receiving data.
        :param end_on_codes: Informational Codes that should be used to flag the end of receiving data
        :return:
        """
        # Create a list of Inbound Messages we need to process
        if isinstance(inbound_message_name,str):
            inbound_messages = [inbound_message_name]
        elif isinstance(inbound_message_name,list):
            inbound_messages = inbound_message_name


        # Generate a list of message ids
        inbound_message_ids = []
        for name in inbound_messages:
            inbound_message_ids.append(Messages.inbound[name])

        message_parser    = MessageParser()
        info_message_id   = Messages.inbound['info_message']
        data_received     = False
        all_data          = []

        request_start = datetime.datetime.now()
        while not data_received:
            messages = self.conn.receive_messages()
            for msg in messages:
                if msg['id'] in inbound_message_ids:
                    func            = getattr(message_parser, msg['action'])
                    data            = func(msg['fields'])
                    all_data.append(data)
                    if msg['id'] == inbound_message_ids[-1]:
                        data_received   = True
                elif msg['id'] == info_message_id:
                    func    = getattr(message_parser, msg['action'])
                    data    = func(msg['fields'])
                    info    = data[2]

                    # Log any message received
                    logger.info("{0}:{1}".format(info['code'],info['text']))

                    # See if we need to consider this code end of processing
                    if info['code'] in end_on_codes:
                        data_received = True
                else:
                    logger.debug("Message #{0} - '{1}' added to unprocessed messages".format(msg['id'], msg['action']))
                    self.unprocessed_messages.append(msg)

            # We may not be connected to the bridge, if no data received after the message timeout threshold break
            current_time = datetime.datetime.now()
            if (current_time - request_start).total_seconds() > self.message_timeout:
                break

        # If there is no data return None instead
        # If there is only one result, send it back without the unnecessary list
        if len(all_data) == 0:
            all_data = None
        elif len(all_data) == 1:
            all_data = all_data[0]

        return all_data

    #################
    ### API Calls ###
    #################
    def calculate_implied_volatility(self,
                                     contract               : Contract,
                                     option_price           : float,
                                     underlying_price       : float,
                                     implied_vol_options    : list):
        """
        Make the calculate_implied_volatility function


        :param contract: Option Contract which we want to get the Implied Volatility For
        :param option_price: Current Option Price
        :param underlying_price: Underlying Price
        :param implied_vol_options:
        :return:
        """

        # Make the Underlying API Call
        request_id = self.get_local_request_id()
        super().calculate_implied_volatility(request_id, contract, option_price, underlying_price, implied_vol_options)

        # Process the response from the bridge
        data = self._process_response('tick_option_computation')
        return data

    def calculate_option_price(self,
                               contract             : Contract,
                               volatility           : float,
                               underlying_price     : float,
                               option_price_options : list):
        """Call this function to calculate option price and greek values
        for a supplied volatility and underlying price.

        request_id:int -    The ticker ID.
        contract:Contract - Describes the contract.
        volatility:double - The volatility.
        underlying_price:double - Price of the underlying."""
        # Make the Underlying API Call
        request_id = self.get_local_request_id()
        super().calculate_option_price(request_id, contract, volatility, underlying_price, option_price_options)

        # Process the Response from the Bridge
        data = self._process_response('')
        return data

    def cancel_account_summary(self, request_id: int):
        """Cancels the request for Account Window Summary tab data.

        request_id:int - The ID of the data request being canceled."""
        # Process the response from the bridge
        super().cancel_account_summary(request_id)
        data = self._process_response('cancel_account_summary')
        return data

    def cancel_account_updates_multi(self, request_id: int):
        super().cancel_account_updates_multi(request_id)
        # Process the response from the bridge
        super().cancel_account_updates_multi()
        data = self._process_response('cancel_accounts_multi')
        return data

    def cancel_calculate_implied_volatility(self, request_id: int):
        """Call this function to cancel a request to calculate
        volatility for a supplied option price and underlying price.

        request_id:int - The request ID.  """
        super().cancel_calculate_implied_volatility(request_id)
        # Process the response from the bridge
        data = self._process_response('cancel_calculate_implied_volatility')
        return data

    def cancel_calculate_option_price(self, request_id: int):
        """Call this function to cancel a request to calculate the option
        price and greek values for a supplied volatility and underlying price.

        request_id:int - The request ID.  """
        super().cancel_calculate_option_price(request_id)
        # Process the response from the bridge
        data = self._process_response('cancel_calculate_option_price')
        return data

    def cancel_fundamental_data(self, request_id: int):
        """Call this function to stop receiving fundamental data.

        request_id:int - The ID of the data request."""
        super().cancel_fundamental_data(request_id)
        # Process the response from the bridge
        data = self._process_response('cancel_fundamental_data')
        return data

    def cancel_head_time_stamp(self, request_id: int):
        super().cancel_head_time_stamp(request_id)
        # Process the response from the bridge
        data = self._process_response('cancel_head_time_stamp')
        return data

    def cancel_histogram_data(self, request_id: int):
        """
        Cancels a prior request to stream histogram data.

        :param request_id: The request identifier from the call to request_histogram_data to be cancelled
        :return:
        """
        super().cancel_histogram_data(request_id)
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def cancel_historical_data(self, request_id: int):
        """Used if an internet disconnect has occurred or the results of a query
        are otherwise delayed and the application is no longer interested in receiving
        the data.

        request_id:int - The ticker ID. Must be a unique value."""
        super().cancel_historical_data(request_id)
        # Process the response from the bridge
        data = self._process_response('cancel_historical_data')
        return data

    def cancel_market_data(self, request_id: int):
        """After calling this function, market data for the specified id
        will stop flowing.

        request_id: int - The ID that was specified in the call to
            reqMktData(). """
        # Process the response from the bridge
        super().cancel_market_data(request_id)
        data = self._process_response('cancel_market_data')
        return data

    def cancel_market_depth(self, request_id: int, is_smart_depth: bool):
        """
        Cancels previous calls to request_market_depth (so that data will stop being received)

        :param request_id: Request ID of the initial call to request_market_depth
        :param is_smart_depth:
        :return:
        """

        # Process the response from the bridge
        super().cancel_market_depth(request_id, is_smart_depth)
        data = self._process_response('cancel_market_depth')
        return data


    def cancel_order(self, order_id: int):
        """
        Makes the cancel_order API call and waits for a response from the Bridge
        :param order_id: Order Id from the call to place_order
        :return:
        """
        # Make the underlying API call
        super().cancel_order(order_id)

        # Process the response from the bridge
        data = self._process_response('cancel_order')
        return data

    def cancel_pnl(self, request_id: int):
        """

        :param request_id:
        :return:
        """
        super().cancel_pnl(request_id)

        # Process the response from the bridge
        data = self._process_response('cancel_pnl')
        return data

    def cancel_pnl_single(self, request_id: int):
        """

        :param request_id: Request ID of the initial call to request_pnl_single
        :return:
        """

        super().cancel_pnl_single(request_id)

        # Process the response from the bridge
        data = self._process_response('cancel_pnl_single')
        return data

    def cancel_positions(self):
        """Cancels real-time position updates."""
        # Process the response from the bridge
        super().cancel_positions()
        data = self._process_response('cancel_positions')
        return data

    def cancel_positions_multi(self, request_id: int):
        # Process the response from the bridge
        super().cancel_positions_multi(request_id)
        data = self._process_response('cancel_positions_multi')
        return data

    def cancel_scanner_subscription(self, request_id: int):
        """
        Cancels a scanner subscription (so no further inbound messages will be provided)

        request_id:int - The Request ID of the previous call to be cancelled"""
        super().cancel_scanner_subscription(request_id)
        # Process the response from the bridge
        data = self._process_response('cancel_scanner_subscription')
        return data

    def cancel_tick_by_tick_data(self, request_id: int):
        """

        :param request_id: Request ID of the initial call to request_tick_by_tick_data
        :return:
        """
        super().cancel_tick_by_tick_data(request_id)

        # Process the response from the bridge
        data = self._process_response('cancel_tick_by_tick_data')
        return data

    def exercise_options(self, request_id: int, contract: Contract,
                         exercise_action: int, exercise_quantity: int,
                         account: str, override: int):
        """
        Exercise an existing option position
        
        :param request_id: Unique Identifier for the this request 
        :param contract: Option to be exercised (TODO: Switch to Option model later)
        :param exercise_action: Specifies if you want the option to lapse or be exercised (1 - exercise, 2 - lapse)
        :param exercise_quantity: The quanity to be exercised 
        :param account: 
        :param override: Specifies whether your setting will override the system's natural action. 
                         For example, if your action is "exercise" and the option is not in-the-money, 
                         by natural action the option would not exercise. If you have override set to "yes" the 
                         natural action would be overridden and the out-of-the money option would be exercised.
                         (0 - don't override, 1 - override) 
        :return: 
        """
        # Make the underlying API call
        request_id = self.get_local_request_id()
        super().exercise_options(request_id, contract, exercise_action, exercise_quantity, account, override)

        # Process the response from the bridge
        data = self._process_response('')
        return data

    def replace_financial_advisor(self, financial_advisor_data: int, xml_data: str):
        """
        Replaces the Financial Advisor Configuration Information from the API.
        (This can also be done manually in TWS itself)

        :param financial_advisor_data: The type of Financial Advisor configuration data being requested.
                                       (1 = GROUPS , 2 = PROFILE , 3 = ACCOUNT ALIASES)
        :param xml_data: The XML string containing the new FA configuration information.
        :return:
        """

        super().replace_financial_advisor(financial_advisor_data, xml_data)

        # Process the response from the bridge
        data = self._process_response('replace_financial_advisor')
        return data

    def request_account_updates(self, subscribe: bool, account_code: str):
        """Call this function to start getting account values, portfolio,
        and last update time information via EWrapper.updateAccountValue(),
        EWrapperi.updatePortfolio() and Wrapper.updateAccountTime().

        subscribe:bool - If set to TRUE, the client will start receiving account
            and Portfoliolio updates. If set to FALSE, the client will stop
            receiving this information.
        account_code:str -The account code for which to receive account and
            portfolio updates."""
        super().request_account_updates()
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_family_codes(self):
        # Process the response from the bridge
        super().request_family_codes()
        data = self._process_response('family_codes')
        return data

    def request_market_data(self,
                            contract            : Contract  ,
                            generic_tick_list   : str       ,
                            snapshot            : bool      ,
                            regulatory_snapshot : bool      ,
                            market_data_options : list):
        """
        Creates a subscription
        
        Related Links
        -------------
        https://interactivebrokers.github.io/tws-api/tick_types.html


        :param contract: Contract for which market data is being requested
        :param generic_tick_list: A comma separated string of ticks or an actual list of integers
                                  Prefixing w/ 'mdoff' indicates that top mkt data shouldn't tick.
                                  You can specify the news source by postfixing w/ ':<source>.
                                  Example: "mdoff,292:FLY+BRF"
        :param snapshot: If true, get the data once and e
        :param regulatory_snapshot: With the US Value Snapshot Bundle for stocks, regulatory snapshots are available for 0.01 USD each.
        :param market_data_options: ???? A mystery that IB only knows (They note, "use default value XYZ")
        :return:
        """


        """Call this function to request market data. The market data
                will be returned by the tickPrice and tickSize events.

                snapshot:bool - Check to return a single snapshot of Market data and
                    have the market data subscription cancel. Do not enter any
                    genericTicklist values if you use snapshots. """

        # Process the response from the bridge
        request_id = self.get_local_request_id()
        super().request_market_data(request_id, contract, generic_tick_list, snapshot, regulatory_snapshot, market_data_options)
        messages = ['tick_price','tick_size']
        data = self._process_response('tick_option_computation')
        return data

    def request_matching_symbols(self, pattern: str):
        # Make the underlying API call
        request_id = self.get_local_request_id()
        super().request_matching_symbols(request_id,pattern)

        # Process the response from the bridge
        data = self._process_response('symbol_samples')
        return data


    @drop_message_id_and_request_id
    def request_option_chains(self,
                              underlying: Contract,
                              exchange=""):
        """
        Convenience function for request_security_definition_option_parameters
        :param underlying:
        :param exchange:
        :return:
        """
        # Get a
        request_id = self.get_local_request_id()

        # Check if we have a valid contract id, if not attempt to get it
        if underlying.id == 0:
            print("Get Contract Data")
            #underlying2 = self.request_contract_data(underlying)
            #print(underlying2)

        super().request_security_definition_option_parameters(request_id, underlying.symbol, exchange,
                                                              underlying.security_type, underlying.id)
        messages_to_process = ['security_definition_option_parameter','security_definition_option_parameter_end']
        data = self._process_response(messages_to_process)

        return data

    def request_security_definition_option_parameters(self,
                                                      underlying_symbol     : str,
                                                      exchange              : str,
                                                      underlying_sec_type   : str,
                                                      underlying_contract_id: int):

        # Process the response from the bridge
        request_id = self.get_local_request_id()
        super().request_security_definition_option_parameters(request_id, underlying_symbol, exchange,
                                                              underlying_sec_type, underlying_contract_id)
        data = self._process_response('security_definition_option_parameter')
        return data

    def request_positions(self):
        """
        Requests real-time position data for all accounts.
        """
        # Make the actual api call
        super().request_positions()

        # Process relevant response messages
        messages_to_process = ['position_data','position_end']
        raw_position_data   = self._process_response(messages_to_process)

        # Strip out the message_ids and request_ids
        position_data = []
        for raw_data in raw_position_data:
            if raw_data[2]:
                position_data.append(raw_data[2])
        return position_data

    @drop_message_id_and_request_id
    def request_smart_components(self,
                                 bbo_exchange: str):
        """
        Provides a list of the exchanges that comprise the 'SMART' exchange

        :param bbo_exchange:
        :return:
        """
        # Make the API call to the bridge
        request_id = self.get_local_request_id()
        super().request_smart_components(request_id, bbo_exchange)

        # Process the response from the bridge
        data = self._process_response('smart_components')

        return data

    @drop_message_id_and_request_id
    def request_scanner_parameters(self):
        """
        Requests an XML string that describes all possible scanner queries.

        :return:
        """

        # Make the api call
        super().request_scanner_parameters()

        # Process the response from the bridge
        data = self._process_response('scanner_parameters')

        return data

    def request_scanner_subscription(self,
                                     scanner: Scanner,
                                     scanner_options: list):
        """

        :param scanner: Criteria to scan the market
        :param scanner_options:
        :return:
        """

        """request_id:int - The ticker ID. Must be a unique value.
        scannerSubscription:ScannerSubscription - This structure contains
            possible parameters used to filter results.
        scanner_options:list - For internal use only. <-- Thanks IB!
            Use default value XYZ."""
        request_id = self.get_local_request_id()

        scanner_filter_options = "" # I believe this is an attribute internal to IB, for now it is not exposed
        super().request_scanner_subscription(request_id, scanner, scanner_options, scanner_filter_options)
        # Process the response from the bridge
        data = self._process_response('scanner_data')
        return data

    def request_soft_dollar_tiers(self, request_id: int):
        """Requests pre-defined Soft Dollar Tiers. This is only supported for
        registered professional advisors and hedge and mutual funds who have
        configured Soft Dollar Tiers in Account Management."""
        # Process the response from the bridge
        data = self._process_response('soft_dollar_tiers')
        return data

    # Not alphabetic
    def place_order(self, order_id: int, contract: Contract, order: Order):
        """Call this function to place an order. The order status will
        be returned by the orderStatus event.

        order_id:int - The order id. You must specify a unique value. When the
            order START_APItus returns, it will be identified by this tag.
            This tag is also used when canceling the order.
        contract:Contract - This structure contains a description of the
            contract which is being traded.
        order:Order - This structure contains the details of tradedhe order.
            Note: Each client MUST connect with a unique clientId."""
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_account_updates_multi(self,
                                      account: str,
                                      model_code: str,
                                      ledger_and_nlv: bool):
        """
        Calls request_account_updates_multi and waits for a response

        :param account:
        :param model_code:
        :param ledger_and_nlv:
        :return:
        """
        """Requests account updates for account and/or model."""

        request_id = self.get_local_request_id()
        super().request_account_updates_multi(request_id, account, model_code, ledger_and_nlv)
        # Process the response from the bridge
        data = self._process_response('account_updates_multi')
        return data

    def request_account_summary(self, request_id: int, group_name: str, tags: str):
        """
        Request the bridge to return the same data that appears in the TWS Account Window Summary Tab.
        Note:   This request is designed for an FA managed account but can be used for any multi-account structure.

        :param request_id: Integer to uniquely identify this request to the Bridge
        :param group_name:
        :param tags:
        :return:
        """




        """Call this method to request and keep up to date the data that appears
        on the TWS Account Window Summary tab. The data is returned by
        accountSummary().

        request_id:int - The ID of the data request. Ensures that responses are matched
            to requests If several requests are in process.
        group_name:str - Set to All to returnrn account summary data for all
            accounts, or set to a specific Advisor Account Group name that has
            already been created in TWS Global Configuration.
        tags:str - A comma-separated list of account tags.  Available tags are:
            accountountType
            NetLiquidation,
            TotalCashValue - Total cash including futures pnl
            SettledCash - For cash accounts, this is the same as
            TotalCashValue
            AccruedCash - Net accrued interest
            BuyingPower - The maximum amount of marginable US stocks the
                account can buy
            EquityWithLoanValue - Cash + stocks + bonds + mutual funds
            PreviousDayEquityWithLoanValue,
            GrossPositionValue - The sum of the absolute value of all stock
                and equity option positions
            RegTEquity,
            RegTMargin,
            SMA - Special Memorandum Account
            InitMarginReq,
            MaintMarginReq,
            AvailableFunds,
            ExcessLiquidity,
            Cushion - Excess liquidity as a percentage of net liquidation value
            FullInitMarginReq,
            FullMaintMarginReq,
            FullAvailableFunds,
            FullExcessLiquidity,
            LookAheadNextChange - Time when look-ahead values take effect
            LookAheadInitMarginReq,
            LookAheadMaintMarginReq,
            LookAheadAvailableFunds,
            LookAheadExcessLiquidity,
            HighestSeverity - A measure of how close the account is to liquidation
            DayTradesRemaining - The Number of Open/Close trades a user
                could put on before Pattern Day Trading is detected. A value of "-1"
                means that the user can put on unlimited day trades.
            Leverage - GrossPositionValue / NetLiquidation
            $LEDGER - Single flag to relay all cash balance tags*, only in base
                currency.
            $LEDGER:CURRENCY - Single flag to relay all cash balance tags*, only in
                the specified currency.
            $LEDGER:ALL - Single flag to relay all cash balance tags* in all
            currencies.
            """

        # Process the response from the bridge
        super().request_account_summary(request_id, group_name, tags)
        data = self._process_response('')
        return data

    @drop_message_id_and_request_id
    def request_all_open_orders(self):
        """
        Returns all open orders regardless of whether they were created in the API or TWS directly

        Note:  No association is made between the returned orders and the requesting client.
        """
        # Process the response from the bridge
        super().request_all_open_orders()
        messages_to_process = ['open_orders','open_orders_end']
        data = self._process_response(messages_to_process)
        return data

    def request_auto_open_orders(self, auto_bind: bool):
        """Call this function to request that newly created TWS orders
        be implicitly associated with the client. When a new TWS order is
        created, the order will be associated with the client, and fed back
        through the openOrder() and orderStatus() functions on the EWrapper.

        Note:  This request can only be made from a client with clientId of 0.

        auto_bind: If set to TRUE, newly created TWS orders will be implicitly
        associated with the client. If set to FALSE, no association will be
        made.

        """
        super().request_auto_open_orders()
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_current_time(self):
        """
        Asks the current system time on the server side.

        :return timestamp:
        """
        # Make the actual request
        super().request_current_time()

        # Receive the response
        message = self.conn.receive_messages()[0]

        # Call the message parser to get extract the data
        action_func = getattr(self.message_parser, message['action'])
        (request_id, timestamp) = action_func(message)

        return timestamp

    def request_executions(self, 
                           client_id        = "" , 
                           account_code     = "" , 
                           time             = "" ,
                           symbol           = "" , 
                           security_type    = "" , 
                           exchange         = "" , 
                           side             = ""
                           ):
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
        # Generate Request ID
        request_id = self.get_local_request_id()

        # Make the underlying API Call
        super().request_executions(request_id, client_id, account_code, time, symbol, security_type, exchange, side)

        # Process the response from the bridge
        messages_to_process = ['execution_data','execution_data_end']
        full_execution_data = self._process_response(messages_to_process)

        # Strip out the message_ids and request_ids
        execution_data = []
        for raw_data in full_execution_data:
            if raw_data[2]:
                execution_data.append(raw_data[2])
        return execution_data

    def request_global_cancel(self):
        """
        Use this function to cancel all open orders globally.
        It cancels both API and TWS open orders.

        If the order was created in TWS, it also gets canceled. If the order
        was initiated in the API, it also gets canceled."""
        # Process the response from the bridge
        data = self._process_response('request_global_cancel')
        return data

    # Note that formatData parameter affects intraday bars only
    # 1-day bars always return with date in YYYYMMDD format
    @drop_message_id_and_request_id
    def request_head_time_stamp(self,
                                contract        : Contract,
                                what_to_show    : str,
                                only_use_rth         : int=0,
                                format_date     : int=1
                                ):
        """
        Get the earliest time stamp available for the given contract/type of data

        :param contract: Contract we want to get earliest time stamp for
        :param what_to_show: string or ``Show`` enum value
        :param only_use_rth:
        :param format_date:
        :return:
        """
        request_id = self.get_local_request_id()
        super().request_head_time_stamp(request_id, contract, what_to_show, only_use_rth, format_date)
        # Process the response from the bridge
        data = self._process_response('head_time_stamp')
        return data

    def request_historical_news(self,
                                contract_id             : int,
                                provider_codes           : str,
                                start_date_time         : str,
                                end_date_time           : str,
                                total_results           : int,
                                historical_news_options : list):



        # Make the underlying API call
        request_id = self.get_local_request_id()
        super().request_historical_news(request_id, contract_id, provider_codes, start_date_time,
                                        end_date_time, total_results, historical_news_options)

        # Process the response from the bridge
        data = self._process_response('request_historical_news')
        return data

    def request_historical_ticks(self, request_id: int, contract: Contract, start_date_time: str,
                                 end_date_time: str, number_of_ticks: int, what_to_show: str, only_use_rth: int,
                                 ignore_size: bool, miscOptions: list):
        """
        Calls request_historical_ticks and then waits for data or a relevant error

        :param request_id:
        :param contract:
        :param start_date_time:
        :param end_date_time:
        :param number_of_ticks:
        :param what_to_show:
        :param only_use_rth:
        :param ignore_size:
        :param miscOptions:
        :return:
        """

        # Make the underlying API Call
        request_id = self.get_local_request_id()
        super().request_historical_ticks(request_id, contract, start_date_time, end_date_time, number_of_ticks,
                                         what_to_show, only_use_rth, ignore_size, miscOptions)

        # Process the response from the bridge
        data = self._process_response('request_historical_ticks')
        return data

    def request_managed_accounts(self):
        """Call this function to request the list of managed accounts. The list
        will be returned by the managedAccounts() function on the EWrapper.

        Note:  This request can only be made when connected to a FA managed account."""
        # Process the response from the bridge
        data = self._process_response('request_managed_accounts')
        return data

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

        super().request_market_data(market_data_type)

        # Process the response from the bridge
        data = self._process_response('market_data_type')
        return data

    def request_market_depth_exchanges(self):
        """

        :return:
        """
        super().request_market_depth_exchanges()

        # Process the response from the bridge
        data = self._process_response('request_market_depth_exchanges')
        return data

    @drop_message_id_and_request_id
    def request_market_rule(self, market_rule_id: int):
        """
        Request the Market Rule for the Given ID

        :param market_rule_id: Integer Identifier for the Market Rule
        :return:
        """
        # Make the underlying API Call
        super().request_market_rule(market_rule_id)

        # Process the Response From the Bridge
        data = self._process_response('market_rule')
        return data

    def request_news_providers(self):
        """
        Request a list of news providers.

        :return: True/False - True if message was sent, False otherwise
        """
        # Make the underlying API Call
        super().request_news_providers()

        # Process the response from the bridge
        data = self._process_response('request_news_providers')
        return data

    def request_open_orders(self):
        """Call this function to request the open orders that were
        placed from this client. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  The client with a clientId of 0 will also receive the TWS-owned
        open orders. These orders will be associated with the client and a new
        order_id will be generated. This association will persist over multiple
        API and TWS sessions.  """
        # Process the response from the bridge
        super().request_open_orders()

        messages_to_process = ['open_orders','open_orders_end']
        data = self._process_response(messages_to_process)
        return data

    def request_positions_multi(self, request_id: int, account: str, model_code: str):
        """Requests positions for account and/or model.
        Results are delivered via EWrapper.positionMulti() and
        EWrapper.positionMultiEnd() """
        # Process the response from the bridge
        data = self._process_response('request_positions_multi')
        return data

    def set_server_log_level(self, log_level: int):
        """The default detail level is ERROR. For more details, see API
        Logging."""
        # Process the response from the bridge
        data = self._process_response('set_server_log_level')
        return data

    def subscribe_to_group_events(self, request_id: int, group_id: int):
        """
        This is the display group subscription request sent by the API to TWS.

        :param request_id:
        :param group_id: int - The ID of the group, currently it is a number from 1 to 7.
        :return:
        """

        # Process the response from the bridge
        super().subscribe_to_group_events(request_id,group_id)
        data = self._process_response('subscribe_to_group_events')
        return data

    @drop_message_id_and_request_id
    def request_contract_data(self,
                              contract: Contract):
        """
        Gets all available details for the given contract.
        :param contract:
        :return:

        """
        # Generate a local request id
        request_id = self.get_local_request_id()

        # Make the underlying API Call
        super().request_contract_data(contract, request_id)

        # Process contract_data and contract_data_end response messages
        messages_to_process = ['contract_data','contract_data_end']
        data = self._process_response(messages_to_process)

        return data


    @drop_message_id_and_request_id
    def request_historical_data(self, 
                                contract            : Contract      ,
                                end_date_time       : str           ,
                                duration            : str           ,
                                bar_size_setting    : str           ,
                                what_to_show        : str           ,
                                only_use_rth        : int           ,
                                format_date         : int=1         ,
                                chart_options       : list=[]
                                ):
        """
        Request Historical Data for a given Contract with the specified parameters

        :param contract: Contract that we want historical data for
        :param end_date_time:
        :param duration:
        :param bar_size_setting: Controls how large a bar is. Legal values are defined in the `BarSize` class
        :param what_to_show: Determines what data is returned by the Bridge. Legal values are in the `Show` class
        :param only_use_rth:
        :param format_date:
        :param chart_options:
        :return:
        """
        request_id = self.get_local_request_id()

        # As we are running in a synchronized mode, this should be set to False always
        keep_up_to_date = False

        super().request_historical_data(request_id, contract,end_date_time,duration, bar_size_setting, what_to_show,
                                        only_use_rth, format_date, keep_up_to_date, chart_options)
        data = self._process_response('historical_data')
        return data

    def request_news_bulletins(self, all_messages: bool):
        """
        Calls request_news_bulletins() API and then waits for the Bridge's response
        :param all_messages: bool
        :return: 
        """
        
        super().request_news_bulletins(all_messages)
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_pnl(self,
                    account: str,
                    model_code: str):
        """
        1. Makes the request_pnl API call
        2. Waits for the response from the Bridge (Data or Info Message) and returns it

        :param account:
        :param model_code:
        :return:
        """
        # Make the underlying API call
        request_id = self.get_local_request_id()
        super().request_pnl(request_id, account, model_code)

        # Process the response from the bridge
        data = self._process_response('pnl')
        return data

    def request_pnl_single(self, request_id: int, account: str, model_code: str, contract_id: int):
        super().request_pnl_single(request_id,account,model_code, contract_id)
        # Process the response from the bridge
        data = self._process_response('pnl_single')
        return data

    def request_tick_by_tick_data(self,
                                  contract: Contract,
                                  tick_type: str,
                                  number_of_ticks: int,
                                  ignore_size: bool):
        """
        1. Makes the request_tick_by_tick_data API call
        2. Waits for the response from the Bridge (Data or Info Message) and returns it

        :param contract:
        :param tick_type:
        :param number_of_ticks:
        :param ignore_size:
        :return:
        """

        # Make the underlying API call
        request_id = self.get_local_request_id()
        super().request_tick_by_tick_data(request_id, contract, tick_type, number_of_ticks, ignore_size)

        # Process the response from the bridge
        data = self._process_response('tick_by_tick_data')
        return data

    def tws_connection_time(self):
        """Returns the time the API application made a connection to TWS."""
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_ids(self, num_ids: int):
        """Call this function to request from TWS the next valid ID that
        can be used when placing an order.  After calling this function, the
        nextValidId() event will be triggered, and the id returned is that next
        valid ID. That ID will reflect any auto binding that has occurred (which
        generates new IDs and increments the next valid ID therein).

        num_ids:int - deprecated"""
        super().request_ids(num_ids)

        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_market_depth(self,
                             contract               : Contract,
                             num_rows               : int,
                             is_smart_depth         : bool,
                             market_depth_options   : list
                             ):
        """
        Request market dept data for a given contract

        Related Inbound Messages
        update_market_depth
        update_market_depth_l2

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
        num_rows:int - Specifies the num market depth rows to display.
        is_smart_depth:bool - specifies SMART depth request
        market_depth_options:list - For internal use only. Use default value
            XYZ."""

        request_id = self.get_local_request_id()
        super().request_market_depth(request_id, contract, num_rows, is_smart_depth, market_depth_options)
        # Process the response from the bridge
        data = self._process_response('market_depth')
        return data

    def cancel_news_bulletins(self):
        """Call this function to stop receiving news bulletins."""
        super().cancel_news_bulletins()
        # Process the response from the bridge
        data = self._process_response('cancels_news_bulletins')
        return data

    def request_uestFA(self, faData: int):
        """Call this function to request FA configuration information from TWS.
        The data returns in an XML string via a "receiveFA" ActiveX event.

        faData:int - Specifies the type of Financial Advisor
            configuration data beingingg requested. Valid values include:
            1 = GROUPS
            2 = PROFILE
            3 = ACCOUNT ALIASES"""
        super().request_uestFA()
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_histogram_data(self, ticker_id: int, contract: Contract,
                               only_use_rth: bool, time_period: str):
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_real_time_bars(self, request_id: int, contract: Contract, barSize: int,
                               whatToShow: str, useRTH: bool,
                               realTimeBarsOptions: list):
        """
        Request to to begin streaming real time bar data

        :param request_id:
        :param contract:
        :param barSize:
        :param whatToShow:
        :param useRTH:
        :param realTimeBarsOptions:
        :return:
        """

        """
        request_id:int - The Id for the request. Must be a unique value. When the
            data is received, it will be identified by this Id. This is also
            used when canceling the request.
        contract:Contract - This object contains a description of the contract
            for which real time bars are being requested
        barSize:int - Currently only 5 second bars are supported, if any other
            value is used, an exception will be thrown.
        whatToShow:str - Determines the nature of the data extracted. Valid
            values include:
            TRADES
            BID
            ASK
            MIDPOINT
        useRTH:bool - Regular Trading Hours only. Valid values include:
            0 = all data available during the time span requested is returned,
                including time intervals when the market in question was
                outside of regular trading hours.
            1 = only data within the regular trading hours for the product
                requested is returned, even if the time time span falls
                partially or completely outside.
        realTimeBarOptions:list - For internal use only. Use default value XYZ."""
        super().request__real_time_bars()
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def cancel_real_time_bars(self, request_id: int):
        """Call the cancel_real_time_bars function to stop receiving real time bar results.

        request_id:int - The Id that was specified in the call to reqRealTimeBars(). """
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def request_fundamental_data(self,
                                 contract           : Contract,
                                 report_type        : str,
                                 request_options    : list):
        """Call this function to receive fundamental data for
        stocks. The appropriate market data subscription must be set up in
        Account Management before you can receive this data.
        Fundamental data will be returned at EWrapper.fundamentalData().

        reqFundamentalData() can handle contract_id specified in the Contract object,
        but not trading_class or multiplier. This is because reqFundamentalData()
        is used only for stocks and stocks do not have a multiplier and
        trading class.

        request_id: The ID of the data request. Ensures that responses are
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
        # Make the Request
        request_id = self.get_local_request_id()
        super().request_fundamental_data(request_id, contract, report_type, request_options)
        end_on_codes = [430]
        message_id, request_id, data = self._process_response('fundamental_data', end_on_codes)
        return data


    def request_news_article(self,
                             provider_code          : str   ,
                             article_id             : str   ,
                             news_article_options   : list):
        # Make the Underlying API Call
        request_id = self.get_local_request_id()
        super().request_news_article(request_id,provider_code, article_id, news_article_options)

        # Process the response from the bridge
        data = self._process_response('news_article')
        return data

    def query_display_groups(self):
        """
        API requests used to integrate with TWS color-grouped windows (display groups).
        TWS color-grouped windows are identified by an integer number. Currently that number ranges from 1 to 7 and are mapped to specific colors, as indicated in TWS.

        request_id:int - The unique number that will be associated with the
            response
        """
        # Generate a Request ID
        request_id = self.get_local_request_id()

        # Make the underlying API Call
        super().query_display_groups(request_id)

        # Process the response from the bridge
        data = self._process_response('display_group_list')
        return data

    def update_display_group(self, request_id: int, contract_info: str):
        """

        :param request_id: The requestId specified in subscribeToGroupEvents().
        :param contract_info: The encoded value that uniquely represents the contract in IB.
                              Possible values include:
                                    none = empty selection
                                    contractID@exchange - any non-combination contract.
                                    Examples: 8314@SMART for IBM SMART; 8314@ARCA for IBM @ARCA.
                                    combo = if any combo is selected.
        :return:
        """
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def unsubscribe_from_group_events(self, request_id: int):
        """request_id:int - The requestId specified in subscribeToGroupEvents()."""
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def verify_message(self, api_data: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def verify_and_auth_request(self, api_name: str, api_version: str,
                                opaque_is_vkey: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def verify_and_auth_message(self, api_data: str, xyzResponse: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        # Process the response from the bridge
        data = self._process_response('')
        return data

    def verify_request(self, api_name: str, api_version: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        super().verify_request(api_name, api_version)
        while True:
            messages = self.conn.receive_messages()
            time.sleep(1)