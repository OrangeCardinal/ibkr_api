"""
Copyright (C) 2018 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""

# TODO: Update the message below
""" 
IBKR_API is the simplest interface available. 
The Bridge returns data in an asynchronus manner and on top of that one request for many requests results in several
messages of varying message types. TWS_API hides all this complexity from the end user and allows for easy tasks to be 
automated. For more advanced usage please see the ClientApplication and MultiClientApplication classes. 

The main class to use from API user's point of view.
It takes care of almost everything:
- implementing the requests
- creating the answer Message Router
- creating the connection to TWS/IBGW
The user just needs to override EWrapper methods to receive the answers.
"""

import time

from base.api_calls import ApiCalls
from classes.contracts.contract import Contract
from classes.order import Order
from classes.scanner import ScannerSubscription


class IBKR_API(ApiCalls):
    def __init__(self, host, port):
        client_id = 0

        super().__init__()
        super().connect(host, port, client_id)

    def calculate_implied_volatility(self, request_id: int, contract: Contract,
                                     option_price: float, underlying_price: float,
                                     implVolOptions: list):
        """Call this function to calculate volatility for a supplied
        option price and underlying price. Result will be delivered
        via EWrapper.tickOptionComputation()

        request_id:int -  The request id.
        contract:Contract -  Describes the contract.
        option_price:double - The price of the option.
        underlying_price:double - Price of the underlying."""
        pass

    def calculate_option_price(self, request_id: int, contract: Contract,
                               volatility: float, underlying_price: float,
                               optPrcOptions: list):
        """Call this function to calculate option price and greek values
        for a supplied volatility and underlying price.

        request_id:int -    The ticker ID.
        contract:Contract - Describes the contract.
        volatility:double - The volatility.
        underlying_price:double - Price of the underlying."""

    pass

    def cancel_account_summary(self, request_id: int):
        """Cancels the request for Account Window Summary tab data.

        request_id:int - The ID of the data request being canceled."""
        pass

    def cancel_account_updates_multi(self, request_id: int):
        pass

    def cancel_calculate_implied_volatility(self, request_id: int):
        """Call this function to cancel a request to calculate
        volatility for a supplied option price and underlying price.

        request_id:int - The request ID.  """
        pass

    def cancel_calculate_option_price(self, request_id: int):
        """Call this function to cancel a request to calculate the option
        price and greek values for a supplied volatility and underlying price.

        request_id:int - The request ID.  """
        pass

    def cancel_fundamental_data(self, request_id: int):
        """Call this function to stop receiving fundamental data.

        request_id:int - The ID of the data request."""
        pass

    def cancel_historical_data(self, request_id: int):
        """Used if an internet disconnect has occurred or the results of a query
        are otherwise delayed and the application is no longer interested in receiving
        the data.

        request_id:int - The ticker ID. Must be a unique value."""
        pass

    def cancel_head_time_stamp(self, request_id: int):
        pass

    def cancel_market_data(self, request_id: int):
        """After calling this function, market data for the specified id
        will stop flowing.

        request_id: int - The ID that was specified in the call to
            reqMktData(). """
        pass

    def cancel_market_depth(self, request_id: int, isSmartDepth: bool):
        """After calling this function, market depth data for the specified id
        will stop flowing.

        request_id:int - The ID that was specified in the call to
            reqMktDepth().
        isSmartDepth:bool - specifies SMART depth request"""
        pass

    def cancel_order(self, order_id: int):
        """Call this function to cancel an order.

        order_id:int - The order ID that was specified previously in the call
            to placeOrder()"""
        pass

    def cancel_positions(self):
        """Cancels real-time position updates."""
        pass

    def cancel_positions_multi(self, request_id: int):
        pass

    def cancel_pnl(self, request_id: int):
        """

        :param request_id:
        :return:
        """
        pass

    def cancel_pnl_single(self, request_id: int):
        pass

    def cancel_scanner_subscription(self, request_id: int):
        """request_id:int - The ticker ID. Must be a unique value."""
        pass

    def cancel_tick_by_tick_data(self, request_id: int):
        pass

    def exercise_options(self, request_id: int, contract: Contract,
                         exercize_action: int, exercize_quantity: int,
                         account: str, override: int):
        """request_id:int - The ticker id. multipleust be a unique value.
        contract:Contract - This structure contains a description of the
            contract to be exercised
        exercize_action:int - Specifies whether you want the option to lapse
            or be exercised.
            Values are 1 = exercise, 2 = lapse.
        exercize_quantity:int - The quantity you want to exercise.
        account:str - destination account
        override:int - Specifies whether your setting will override the system's
            natural action. For example, if your action is "exercise" and the
            option is not in-the-money, by natural action the option would not
            exercise. If you have override set to "yes" the natural action would
             be overridden and the out-of-the money option would be exercised.
            Values are: 0 = no, 1 = yes."""
        pass

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
        pass

    def replace_financial_advisor(self, faData: int, cxml: str):
        """Call this function to modify FA configuration information from the
        API. Note that this can also be done manually in TWS itself.

        faData:int - Specifies the type of Financial Advisor
            configuration data beingingg requested. Valid values include:
            1 = GROUPS
            2 = PROFILE
            3 = ACCOUNT ALIASES
        cxml: str - The XML string containing the new FA configuration
            information.  """
        pass

    def request_account_updates(self, subscribe: bool, account_code: str):
        """Call this function to start getting account values, portfolio,
        and last update time information via EWrapper.updateAccountValue(),
        EWrapperi.updatePortfolio() and Wrapper.updateAccountTime().

        subscribe:bool - If set to TRUE, the client will start receiving account
            and Portfoliolio updates. If set to FALSE, the client will stop
            receiving this information.
        account_code:str -The account code for which to receive account and
            portfolio updates."""
        pass

    def request_account_updates_multi(self, request_id: int, account: str, model_code: str,
                                      ledgerAndNLV: bool):
        """Requests account updates for account and/or model."""

        pass

    def request_account_summary(self, request_id: int, group_name: str, tags: str):
        """Call this method to request and keep up to date the data that appears
        on the TWS Account Window Summary tab. The data is returned by
        accountSummary().

        Note:   This request is designed for an FA managed account but can be
        used for any multi-account structure.

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
            currencies."""

        pass

    def request_all_open_orders(self):
        """Call this function to request the open orders placed from all
        clients and also from TWS. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  No association is made between the returned orders and the
        requesting client."""
        pass

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
        pass

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

        super().request_executions(request_id, client_id, account_code, time, symbol, security_type, exchange, side)
        pass

    def request_global_cancel(self):
        """Use this function to cancel all open orders globally. It
        cancels both API and TWS open orders.

        If the order was created in TWS, it also gets canceled. If the order
        was initiated in the API, it also gets canceled."""
        pass

    # Note that formatData parameter affects intraday bars only
    # 1-day bars always return with date in YYYYMMDD format
    def request_head_time_stamp(self, request_id: int, contract: Contract,
                                whatToShow: str, useRTH: int, formatDate: int):
        pass

    def request_historical_news(self, request_id: int, conId: int, providerCodes: str,
                                startDateTime: str, end_date_time: str, totalResults: int, historicalNewsOptions: list):
        pass

    def request_historical_ticks(self, request_id: int, contract: Contract, startDateTime: str,
                                 end_date_time: str, number_of_ticks: int, whatToShow: str, useRth: int,
                                 ignoreSize: bool, miscOptions: list):
        pass

    def request_managed_accounts(self):
        """Call this function to request the list of managed accounts. The list
        will be returned by the managedAccounts() function on the EWrapper.

        Note:  This request can only be made when connected to a FA managed account."""
        pass

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
        pass

    def request_market_depth_exhanges(self):
        """

        :return:
        """
        pass

    def request_market_rule(self, market_rule_id: int):
        pass

    def request_news_providers(self):
        """
        Request a list of news providers.

        :return: True/False - True if message was sent, False otherwise
        """
        pass

    def request_open_orders(self):
        """Call this function to request the open orders that were
        placed from this client. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  The client with a clientId of 0 will also receive the TWS-owned
        open orders. These orders will be associated with the client and a new
        order_id will be generated. This association will persist over multiple
        API and TWS sessions.  """
        pass

    def request_positions(self):
        """Requests real-time position data for all accounts."""
        pass

    def request_positions_multi(self, request_id: int, account: str, model_code: str):
        """Requests positions for account and/or model.
        Results are delivered via EWrapper.positionMulti() and
        EWrapper.positionMultiEnd() """
        pass

    def request_smart_components(self, request_id: int, bboExchange: str):
        pass

    def set_server_log_level(self, logLevel: int):
        """The default detail level is ERROR. For more details, see API
        Logging."""
        pass

    def start_api(self):
        """  Initiates the message exchange between the client application and
        the TWS/IB Gateway. """
        pass

    def subscribe_to_group_events(self, request_id: int, groupId: int):
        """request_id:int - The unique number associated with the notification.
        groupId:int - The ID of the group, currently it is a number from 1 to 7.
            This is the display group subscription request sent by the API to TWS."""
        pass

    #################
    ### API Calls ###
    #################
    def request_contract_details(self, contract: Contract):
        """

        :param contract:
        :return:
        """
        #"""Call this function to download all details for a particular
        #underlying. The contract details will be received via the contractDetails()
        #function on the EWrapper.

        #request_id:int - The ID of the data request. Ensures that responses are
        #    make_fieldatched to requests if several requests are in process.
        #contract:Contract - The summary description of the contract being looked
        #    up."""
        super().request_contract_details(contract)
        # Receive the response
        while True:
            message = self.conn.receive_messages()
            print(message)
            time.sleep(1)

        # Call the message parser to get extract the data
        action_func = getattr(self.message_parser, message['action'])
        #(request_id, timestamp) = action_func(message)
        #pass

    def request_historical_data(self, contract: Contract, end_date_time: str,
                                duration: str, bar_size_setting: str, what_to_show: str,
                                use_rth: int, format_date: int, keep_up_to_date: bool, chart_options: list):
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
        barSizeSetting:str - Specifies the size of the bars that will be returned (within IB/TWS listimits).
            Valid values include:
            1 sec
            5 secs
            15 secs
            30 secs
            1 min
            2 mins
            3 mins
            5 mins
            15 mins
            30 mins
            1 hour
            1 day
        whatToShow:str - Determines the nature of data beinging extracted. Valid values include:

            TRADES
            MIDPOINT
            BID
            ASK
            BID_ASK
            HISTORICAL_VOLATILITY
            OPTION_IMPLIED_VOLATILITY
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
        chartOptions:list - For internal use only. Use default value XYZ. """
        super().request_historical_data(contract,end_date_time,duration, bar_size_setting, what_to_show, use_rth,
                                        format_date, keep_up_to_date, chart_options)
        while True:
            messages = self.conn.receive_messages()
            print(messages)
            time.sleep(2)

    def request_news_bulletins(self, allMsgs: bool):
        """Call this function to start receiving news bulletins. Each bulletin
        will be returned by the updateNewsBulletin() event.

        allMsgs:bool - If set to TRUE, returns all the existing bulletins for
        the currencyent day and any new ones. If set to FALSE, will only
        return new bulletins. """
        pass

    def request_pnl(self, request_id: int, account: str, model_code: str):
        pass

    def request_pnl_single(self, request_id: int, account: str, model_code: str, contract_id: int):
        pass

    def request_tick_by_tick_data(self, request_id: int, contract: Contract, tick_type: str,
                                  number_of_ticks: int, ignoreSize: bool):
        pass

    def request_market_data(self, request_id: int, contract: Contract, generic_tick_list: str,
                            snapshot: bool, regulatory_snapshot: bool, market_data_options: list):
        """Call this function to request market data. The market data
                will be returned by the tickPrice and tickSize events.

                request_id: int - The ticker id. Must be a unique value. When the
                    market data returns, it will be identified by this tag. This is
                    also used when canceling the market data.
                contract:Contract - This structure contains a description of the
                    Contractt for which market data is being requested.
                genericTickList:str - A commma delimited list of generic tick types.
                    Tick types can be found in the Generic Tick Types page.
                    Prefixing w/ 'mdoff' indicates that top mkt data shouldn't tick.
                    You can specify the news source by postfixing w/ ':<source>.
                    Example: "mdoff,292:FLY+BRF"
                snapshot:bool - Check to return a single snapshot of Market data and
                    have the market data subscription cancel. Do not enter any
                    genericTicklist values if you use snapshots.
                regulatorySnapshot: bool - With the US Value Snapshot Bundle for stocks,
                    regulatory snapshots are available for 0.01 USD each.
                mktDataOptions:list - For internal use only.
                    Use default value XYZ. """
        pass

    def twsConnectionTime(self):
        """Returns the time the API application made a connection to TWS."""
        pass

    def request_ids(self, numIds: int):
        """Call this function to request from TWS the next valid ID that
        can be used when placing an order.  After calling this function, the
        nextValidId() event will be triggered, and the id returned is that next
        valid ID. That ID will reflect any autobinding that has occurred (which
        generates new IDs and increments the next valid ID therein).

        numIds:int - deprecated"""
        pass

    def request_market_depth(self, request_id: int, contract: Contract,
                             numRows: int, isSmartDepth: bool, mktDepthOptions: list):
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
        numRows:int - Specifies the numRowsumber of market depth rows to display.
        isSmartDepth:bool - specifies SMART depth request
        mktDepthOptions:list - For internal use only. Use default value
            XYZ."""

        pass

    def cancel_news_bulletins(self):
        """Call this function to stop receiving news bulletins."""
        pass

    def request_uestFA(self, faData: int):
        """Call this function to request FA configuration information from TWS.
        The data returns in an XML string via a "receiveFA" ActiveX event.

        faData:int - Specifies the type of Financial Advisor
            configuration data beingingg requested. Valid values include:
            1 = GROUPS
            2 = PROFILE
            3 = ACCOUNT ALIASES"""
        pass

    def request_histogram_data(self, tickerId: int, contract: Contract,
                               useRTH: bool, timePeriod: str):
        pass

    def cancel_histogram_data(self, tickerId: int):
        pass

    def request_scanner_parameters(self):
        """Requests an XML string that describes all possible scanner queries."""
        pass

    def request_scanner_subscription(self, request_id: int,
                                     subscription: ScannerSubscription,
                                     scannerSubscriptionOptions: list,
                                     scannerSubscriptionFilterOptions: list):
        """request_id:int - The ticker ID. Must be a unique value.
        scannerSubscription:ScannerSubscription - This structure contains
            possible parameters used to filter results.
        scannerSubscriptionOptions:list - For internal use only.
            Use default value XYZ."""
        pass

    def request_real_time_bars(self, request_id: int, contract: Contract, barSize: int,
                               whatToShow: str, useRTH: bool,
                               realTimeBarsOptions: list):
        """Call the reqRealTimeBars() function to start receiving real time bar
        results through the realtimeBar() EWrapper function.

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
        pass

    def cancelRealTimeBars(self, request_id: int):
        """Call the cancelRealTimeBars() function to stop receiving real time bar results.

        request_id:int - The Id that was specified in the call to reqRealTimeBars(). """
        pass

    def request_fundamental_data(self, contract: Contract,
                                 report_type: str, request_options: list):
        """Call this function to receive fundamental data for
        stocks. The appropriate market data subscription must be set up in
        Account Management before you can receive this data.
        Fundamental data will be returned at EWrapper.fundamentalData().

        reqFundamentalData() can handle contract_id specified in the Contract object,
        but not trading_class or multiplier. This is because reqFundamentalData()
        is used only for stocks and stocks do not have a multiplier and
        trading class.

        request_id:tickerId - The ID of the data request. Ensures that responses are
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
        time.sleep(5)
        messages = self.conn.receive_messages()
        print(messages)

    def request_NewsArticle(self, request_id: int, providerCode: str, articleId: str, newsArticleOptions: list):
        pass

    def queryDisplayGroups(self, request_id: int):
        """API requests used to integrate with TWS color-grouped windows (display groups).
        TWS color-grouped windows are identified by an integer number. Currently that number ranges from 1 to 7 and are mapped to specific colors, as indicated in TWS.

        request_id:int - The unique number that will be associated with the
            response """
        pass

    def updateDisplayGroup(self, request_id: int, contractInfo: str):
        """request_id:int - The requestId specified in subscribeToGroupEvents().
        contractInfo:str - The encoded value that uniquely represents the
            contract in IB. Possible values include:

            none = empty selection
            contractID@exchange - any non-combination contract.
                Examples: 8314@SMART for IBM SMART; 8314@ARCA for IBM @ARCA.
            combo = if any combo is selected."""
        pass

    def unsubscribeFromGroupEvents(self, request_id: int):
        """request_id:int - The requestId specified in subscribeToGroupEvents()."""
        pass

    def verify_message(self, api_data: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        pass

    def verify_and_auth_request(self, api_name: str, api_version: str,
                                opaqueIsvKey: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        pass

    def verify_and_auth_message(self, api_data: str, xyzResponse: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        pass

    def verify_request(self, api_name: str, api_version: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""
        super().verify_request(api_name, api_version)
        while True:
            messages = self.conn.receive_messages()
            print(messages)
            time.sleep(1)


    def request_sec_def_opt_params(self, request_id: int, underlying_symbol: str,
                                   futFopExchange: str, underlyingSecType: str,
                                   underlyingConId: int):
        """Requests security definition option parameters for viewing a
        contract's option chain request_id the ID chosen for the request
        underlying_symbol futFopExchange The exchange on which the returned
        options are trading. Can be set to the empty string "" for all
        exchanges. underlyingSecType The type of the underlying security,
        i.e. STK underlyingConId the contract ID of the underlying security.
        Response comes via EWrapper.securityDefinitionOptionParameter()"""
        pass

    def request_soft_dollar_tiers(self, request_id: int):
        """Requests pre-defined Soft Dollar Tiers. This is only supported for
        registered professional advisors and hedge and mutual funds who have
        configured Soft Dollar Tiers in Account Management."""
        pass

    def request_family_codes(self):
        pass

    def request_matching_symbols(self, request_id: int, pattern: str):
        pass