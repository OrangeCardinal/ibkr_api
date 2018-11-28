"""
Copyright (C) 2018 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""
import time

# TODO: Update the message below
"""
TODO: 
The main class to use from API user's point of view.
It takes care of almost everything:
- implementing the requests
- creating the answer Message Router
- creating the connection to TWS/IBGW
The user just needs to override EWrapper methods to receive the answers.
"""

import logging
import socket

from base.message_parser import MessageParser
from base.constants import *

from base.bridge_connection import BridgeConnection
from base.errors import CONNECT_FAIL, NOT_CONNECTED, UPDATE_TWS, Errors
from base.message import OUT

from classes.bar_size import BarSize
from classes.contracts.contract import Contract
from classes.order import Order
from classes.scanner import ScannerSubscription

#from utils import (current_fn_name)

logger = logging.getLogger(__name__)


class ApiCalls(object):

    def __init__(self, response_handler=None, request_handler=None):
        self.application_state = "Detached from Bridge"
        self.conn = None  # Connection between this application and the bridge
        self.host = None  # Bridge's Host
        self.port = None  # Bridge's Port
        self.optional_capabilities = ""  # Hell if I know, IBKR's documentation has nothing...
        self.request_id = 0  # Unique Identifier for the request
        self.server_version_ = None

        self.message_parser = MessageParser()  # Converts from message data to object(s)
        self.request_handler = request_handler  # Functions if exist are called before and/or after api calls
        self.response_handler = response_handler  # API Responses Functions provided by the end user

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

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_CALC_IMPLIED_VOLAT:
            self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support calculateImpliedVolatility req.")
            return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class:
                self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support trading_class parameter in calculateImpliedVolatility.")
                return

        message_version = 3
        fields = []
        # send req mkt data msg
        fields = [OUT.REQ_CALC_IMPLIED_VOLAT, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, contract.last_trade_date_or_contract_month, contract.strike,
                  contract.right, contract.multiplier, contract.exchange, contract.primary_exchange,
                  contract.currency, contract.local_symbol]

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields.append(contract.trading_class)

        fields.extend([option_price, underlying_price])

        if self.server_version() >= MIN_SERVER_VER_LINKING:
            implVolOptStr = ""
            tag_values_count = len(implVolOptions) if implVolOptions else 0
            if implVolOptions:
                for implVolOpt in implVolOptions:
                    implVolOptStr += str(implVolOpt)
            fields.extend([tag_values_count, implVolOptStr])

        self.conn.send_message(fields)

    def calculate_option_price(self, request_id: int, contract: Contract,
                               volatility: float, underlying_price: float,
                               optPrcOptions: list):
        """Call this function to calculate option price and greek values
        for a supplied volatility and underlying price.

        request_id:int -    The ticker ID.
        contract:Contract - Describes the contract.
        volatility:double - The volatility.
        underlying_price:double - Price of the underlying."""

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_CALC_IMPLIED_VOLAT:
            self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support calculateImpliedVolatility req.")
            return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class:
                self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support trading_class parameter in calculateImpliedVolatility.")
                return

        message_version = 3

        # send req mkt data msg
        fields = [OUT.REQ_CALC_OPTION_PRICE, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, contract.last_trade_date_or_contract_month, contract.strike,
                  contract.right, contract.multiplier, contract.exchange, contract.currency, contract.local_symbol]

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields.extend([contract.trading_class, volatility, underlying_price])

        if self.server_version() >= MIN_SERVER_VER_LINKING:
            option_price_options = ""
            tag_values_count = len(optPrcOptions) if optPrcOptions else 0
            if optPrcOptions:
                for implVolOpt in optPrcOptions:
                    option_price_options += str(implVolOpt)
            fields.extend([tag_values_count, optPrcOptions])

        self.conn.send_message(fields)

    def cancel_account_summary(self, request_id: int):
        """Cancels the request for Account Window Summary tab data.

        request_id:int - The ID of the data request being canceled."""

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.CANCEL_ACCOUNT_SUMMARY, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_account_updates_multi(self, request_id: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_MODELS_SUPPORT:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support cancel account updates multi request.")
            return

        message_version = 1
        fields = [OUT.CANCEL_ACCOUNT_UPDATES_MULTI, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_calculate_implied_volatility(self, request_id: int):
        """Call this function to cancel a request to calculate
        volatility for a supplied option price and underlying price.

        request_id:int - The request ID.  """

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_CALC_IMPLIED_VOLAT:
            self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support calculateImpliedVolatility req.")
            return

        message_version = 1
        fields = [OUT.CANCEL_CALC_IMPLIED_VOLAT, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_calculate_option_price(self, request_id: int):
        """Call this function to cancel a request to calculate the option
        price and greek values for a supplied volatility and underlying price.

        request_id:int - The request ID.  """

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_CALC_IMPLIED_VOLAT:
            self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support calculateImpliedVolatility req.")
            return

        message_version = 1
        fields = [OUT.CANCEL_CALC_OPTION_PRICE, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_fundamental_data(self, request_id: int):
        """Call this function to stop receiving fundamental data.

        request_id:int - The ID of the data request."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_FUNDAMENTAL_DATA:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support fundamental data request.")
            return

        message_version = 1
        fields = [OUT.CANCEL_FUNDAMENTAL_DATA, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_market_data(self, request_id: int):
        """After calling this function, market data for the specified id
        will stop flowing.

        request_id: int - The ID that was specified in the call to
            reqMktData(). """

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        # send req mkt data msg
        message_version = 2
        fields = [OUT.CANCEL_MKT_DATA, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_market_depth(self, request_id: int, isSmartDepth: bool):
        """After calling this function, market depth data for the specified id
        will stop flowing.

        request_id:int - The ID that was specified in the call to
            reqMktDepth().
        isSmartDepth:bool - specifies SMART depth request"""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_SMART_DEPTH and isSmartDepth:
            self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support SMART depth cancel.")
            return

        message_version = 1

        # send cancel mkt depth msg
        fields = [OUT.CANCEL_MKT_DEPTH, message_version, request_id]

        if self.server_version() >= MIN_SERVER_VER_SMART_DEPTH:
            fields.append(isSmartDepth)

        self.conn.send_message(fields)

    def cancel_order(self, order_id: int):
        """Call this function to cancel an order.

        order_id:int - The order ID that was specified previously in the call
            to placeOrder()"""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.CANCEL_ORDER, message_version, order_id]
        self.conn.send_message(fields)

    def cancel_positions(self):
        """Cancels real-time position updates."""

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_POSITIONS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support positions request.")
            return

        message_version = 1
        fields = [OUT.CANCEL_POSITIONS, message_version]
        self.conn.send_message(fields)

    def cancel_positions_multi(self, request_id: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_MODELS_SUPPORT:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support cancel positions multi request.")
            return

        message_version = 1
        fields = [OUT.CANCEL_POSITIONS_MULTI, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_pnl(self, request_id: int):
        """

        :param request_id:
        :return:
        """
        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_PNL:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support PnL request.")
            return

        fields = [OUT.CANCEL_PNL, request_id]
        self.conn.send_message(fields)

    def cancel_pnl_single(self, request_id: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_PNL:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support PnL request.")
            return

        fields = [OUT.CANCEL_PNL_SINGLE, request_id]
        self.conn.send_message(fields)

    def cancel_real_time_bars(self, request_id: int):
        """Call the cancelRealTimeBars() function to stop receiving real time bar results.

        request_id:int - The Id that was specified in the call to reqRealTimeBars(). """

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        # send req mkt data msg
        message_version = 1
        fields = [OUT.CANCEL_REAL_TIME_BARS, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_scanner_subscription(self, request_id: int):
        """request_id:int - The ticker ID. Must be a unique value."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.CANCEL_SCANNER_SUBSCRIPTION, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_tick_by_tick_data(self, request_id: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_TICK_BY_TICK:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support tick-by-tick data requests.")
            return

        fields = [OUT.CANCEL_TICK_BY_TICK_DATA, request_id]
        self.conn.send_message(fields)

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

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class:
                self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support id, multiplier, trading_class parameter in exerciseOptions.")
                return

        insert_offset = 0
        message_version = 2

        fields = [OUT.EXERCISE_OPTIONS, message_version, request_id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange,
                  contract.currency, contract.local_symbol, exercize_action, exercize_quantity, account, override]

        # send contract fields
        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            insert_offset += 1
            fields.insert(3, contract.id)

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            insert_position = 12 + insert_offset
            insert_offset += 1
            fields.insert(insert_position, contract.trading_class)

        self.conn.send_message(fields)

    def place_order(self, order_id: int, contract: Contract, order: Order):
        """Call this function to place an order. The order status will
        be returned by the orderStatus event.

        order_id:int - The order id. You must specify a unique value. When the
            order START_APItus returns, it will be identified by this tag.
            This tag is also used when canceling the order.
        contract:Contract - This structure contains a description of the
            contract which is being traded.
        order:Order - This structure contains the details of tradedhe order.
            Note: Each client MUST connect with a unique client_id."""

        if not self.conn.is_connected():
            self.response_handler.error(order_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_DELTA_NEUTRAL:
            if contract.deltaNeutralContract:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support delta-neutral orders.")
                return

        if self.server_version() < MIN_SERVER_VER_SCALE_ORDERS2:
            if order.scaleSubsLevelSize != UNSET_INTEGER:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support Subsequent Level Size for Scale orders.")
                return

        if self.server_version() < MIN_SERVER_VER_ALGO_ORDERS:
            if order.algoStrategy:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support algo orders.")
                return

        if self.server_version() < MIN_SERVER_VER_NOT_HELD:
            if order.notHeld:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support notHeld parameter.")
                return

        if self.server_version() < MIN_SERVER_VER_SEC_ID_TYPE:
            if contract.security_id_type or contract.security_id:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support security_id_type and security_id parameters.")
                return

        if self.server_version() < MIN_SERVER_VER_PLACE_ORDER_CONID:
            if contract.id and contract.id > 0:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg("contract.id"))
                return

        if self.server_version() < MIN_SERVER_VER_SSHORTX:
            if order.exemptCode != -1:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg('exemptCode'))
                return

        if self.server_version() < MIN_SERVER_VER_SSHORTX:
            if contract.comboLegs:
                for comboLeg in contract.comboLegs:
                    if comboLeg.exemptCode != -1:
                        self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                                    "  It does not support exemptCode parameter.")
                        return

        if self.server_version() < MIN_SERVER_VER_HEDGE_ORDERS:
            if order.hedgeType:
                self.response_handler.error(order_id, UPDATE_TWS.code(),
                                            UPDATE_TWS.msg(extra="  It does not support hedge orders."))
                return

        if self.server_version() < MIN_SERVER_VER_OPT_OUT_SMART_ROUTING:
            if order.optOutSmartRouting:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg("optOutSmartRouting"))
                return

        if self.server_version() < MIN_SERVER_VER_DELTA_NEUTRAL_CONID:
            if order.deltaNeutralConId > 0 \
                    or order.deltaNeutralSettlingFirm \
                    or order.deltaNeutralClearingAccount \
                    or order.deltaNeutralClearingIntent:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support deltaNeutral parameters: ConId, SettlingFirm, ClearingAccount, ClearingIntent.")
                return

        if self.server_version() < MIN_SERVER_VER_DELTA_NEUTRAL_OPEN_CLOSE:
            if order.deltaNeutralOpenClose \
                    or order.deltaNeutralShortSale \
                    or order.deltaNeutralShortSaleSlot > 0 \
                    or order.deltaNeutralDesignatedLocation:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support deltaNeutral parameters: OpenClose, ShortSale, ShortSaleSlot, DesignatedLocation.")
                return

        if self.server_version() < MIN_SERVER_VER_SCALE_ORDERS3:
            if order.scalePriceIncrement > 0 and order.scalePriceIncrement != UNSET_DOUBLE:
                if order.scalePriceAdjustValue != UNSET_DOUBLE \
                        or order.scalePriceAdjustInterval != UNSET_INTEGER \
                        or order.scaleProfitOffset != UNSET_DOUBLE \
                        or order.scaleAutoReset \
                        or order.scaleInitPosition != UNSET_INTEGER \
                        or order.scaleInitFillQty != UNSET_INTEGER \
                        or order.scaleRandomPercent:
                    self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                                "  It does not support Scale order parameters: PriceAdjustValue, PriceAdjustInterval, " +
                                                "ProfitOffset, AutoReset, InitPosition, InitFillQty and RandomPercent")
                    return

        if self.server_version() < MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE and contract.security_type == "BAG":
            if order.orderComboLegs:
                for orderComboLeg in order.orderComboLegs:
                    if orderComboLeg.price != UNSET_DOUBLE:
                        self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                                    "  It does not support per-leg prices for order combo legs.")
                        return

        if self.server_version() < MIN_SERVER_VER_TRAILING_PERCENT:
            if order.trailingPercent != UNSET_DOUBLE:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support trailing percent parameter")
                return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support trading_class parameter in placeOrder.")
                return

        if self.server_version() < MIN_SERVER_VER_SCALE_TABLE:
            if order.scaleTable or order.activeStartTime or order.activeStopTime:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support scaleTable, activeStartTime and activeStopTime parameters")
                return

        if self.server_version() < MIN_SERVER_VER_ALGO_ID:
            if order.algoId:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support algoId parameter")
                return

        if self.server_version() < MIN_SERVER_VER_ORDER_SOLICITED:
            if order.solicited:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support order solicited parameter.")
                return

        if self.server_version() < MIN_SERVER_VER_MODELS_SUPPORT:
            if order.model_code:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support model code parameter.")
                return

        if self.server_version() < MIN_SERVER_VER_EXT_OPERATOR:
            if order.extOperator:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support ext operator parameter")
                return

        if self.server_version() < MIN_SERVER_VER_SOFT_DOLLAR_TIER:
            if order.softDollarTier.name or order.softDollarTier.val:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            " It does not support soft dollar tier")
                return

        if self.server_version() < MIN_SERVER_VER_CASH_QTY:
            if order.cashQty:
                self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            " It does not support cash quantity parameter")
                return

        if self.server_version() < MIN_SERVER_VER_DECISION_MAKER and (
                order.mifid2DecisionMaker != "" or order.mifid2DecisionAlgo != ""):
            self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support MIFID II decision maker parameters")
            return

        if self.server_version() < MIN_SERVER_VER_MIFID_EXECUTION and (
                order.mifid2ExecutionTrader != "" or order.mifid2ExecutionAlgo != ""):
            self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support MIFID II execution parameters")
            return

        if self.server_version() < MIN_SERVER_VER_AUTO_PRICE_FOR_HEDGE and order.dontUseAutoPriceForHedge:
            self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support dontUseAutoPriceForHedge parameter")
            return

        if self.server_version() < MIN_SERVER_VER_ORDER_CONTAINER and order.isOmsContainer:
            self.response_handler.error(order_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support oms container parameter")
            return

        # Create the list of fields to send, then send the message

        fields = [OUT.PLACE_ORDER]

        if self.server_version() < MIN_SERVER_VER_ORDER_CONTAINER:
            message_version = 27 if (self.server_version() < MIN_SERVER_VER_NOT_HELD) else 45
            fields.append(message_version)

        fields.append(order_id)

        # send contract fields
        if self.server_version() >= MIN_SERVER_VER_PLACE_ORDER_CONID:
            fields.append(contract.id)

        fields += [contract.symbol,
                   contract.security_type,
                   contract.last_trade_date_or_contract_month,
                   contract.strike,
                   contract.right,
                   contract.multiplier,  # srv v15 and above
                   contract.exchange,
                   contract.primary_exchange,  # srv v14 and above
                   contract.currency,
                   contract.local_symbol]  # srv v2 and above

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields.append(contract.trading_class)

        if self.server_version() >= MIN_SERVER_VER_SEC_ID_TYPE:
            fields += [contract.security_id_type, contract.security_id]

        # send main order fields
        fields.append(order.action)

        if self.server_version() >= MIN_SERVER_VER_FRACTIONAL_POSITIONS:
            fields.append(order.totalQuantity)
        else:
            fields.append(int(order.totalQuantity))

        fields.append(order.orderType)
        if self.server_version() < MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE:
            fields.append(
                order.lmtPrice if order.lmtPrice != UNSET_DOUBLE else 0)
        else:
            fields.append(self.conn.make_field_handle_empty(order.lmtPrice))
        if self.server_version() < MIN_SERVER_VER_TRAILING_PERCENT:
            fields.append(
                order.auxPrice if order.auxPrice != UNSET_DOUBLE else 0)
        else:
            fields.append(self.conn.make_field_handle_empty(order.auxPrice))

            # send extended order fields
            fields += [order.tif,
                       order.ocaGroup,
                       order.account,
                       order.openClose,
                       order.origin,
                       order.orderRef,
                       order.transmit,
                       order.parentId,  # srv v4 and above
                       order.blockOrder,  # srv v5 and above
                       order.sweepToFill,  # srv v5 and above
                       order.displaySize,  # srv v5 and above
                       order.triggerMethod,  # srv v5 and above
                       order.outsideRth,  # srv v5 and above
                       order.hidden]  # srv v7 and above

        # Send combo legs for BAG requests (srv v8 and above)
        if contract.security_type == "BAG":
            comboLegsCount = len(contract.comboLegs) if contract.comboLegs else 0
            fields.append(comboLegsCount)
            if comboLegsCount > 0:
                for comboLeg in contract.comboLegs:
                    assert comboLeg
                    fields += [comboLeg.conId,
                               comboLeg.ratio,
                               comboLeg.action,
                               comboLeg.exchange,
                               comboLeg.openClose,
                               comboLeg.shortSaleSlot,  # srv v35 and above
                               comboLeg.designatedLocation]  # srv v35 and above
                    if self.server_version() >= MIN_SERVER_VER_SSHORTX_OLD:
                        fields.append(comboLeg.exemptCode)

        # Send order combo legs for BAG requests
        if self.server_version() >= MIN_SERVER_VER_ORDER_COMBO_LEGS_PRICE and contract.security_type == "BAG":
            orderComboLegsCount = len(order.orderComboLegs) if order.orderComboLegs else 0
            fields.append(orderComboLegsCount)

            if orderComboLegsCount:
                for orderComboLeg in order.orderComboLegs:
                    assert orderComboLeg
                    fields.append(self.conn.make_field_handle_empty(orderComboLeg.price))

        if self.server_version() >= MIN_SERVER_VER_SMART_COMBO_ROUTING_PARAMS and contract.security_type == "BAG":
            smartComboRoutingParamsCount = len(order.smartComboRoutingParams) if order.smartComboRoutingParams else 0
            fields.append(smartComboRoutingParamsCount)
            if smartComboRoutingParamsCount > 0:
                for tagValue in order.smartComboRoutingParams:
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
        fields += ["",  # srv v9 and above

                   order.discretionaryAmt,  # srv v10 and above
                   order.goodAfterTime,  # srv v11 and above
                   order.goodTillDate,  # srv v12 and above

                   order.faGroup,  # srv v13 and above
                   order.faMethod,  # srv v13 and above
                   order.faPercentage,  # srv v13 and above
                   order.faProfile]  # srv v13 and above

        if self.server_version() >= MIN_SERVER_VER_MODELS_SUPPORT:
            fields.append(order.model_code)

        # institutional short saleslot data (srv v18 and above)
        fields += [order.shortSaleSlot,  # 0 for retail, 1 or 2 for institutions
                   order.designatedLocation]  # populate only when shortSaleSlot = 2.
        if self.server_version() >= MIN_SERVER_VER_SSHORTX_OLD:
            fields.append(order.exemptCode)

        # srv v19 and above fields
        fields.append(order.ocaType)

        fields += [order.rule80A,
                   order.settlingFirm,
                   order.allOrNone,
                   self.conn.make_field_handle_empty(order.minQty),
                   self.conn.make_field_handle_empty(order.percentOffset),
                   order.eTradeOnly,
                   order.firmQuoteOnly,
                   self.conn.make_field_handle_empty(order.nbboPriceCap),
                   order.auctionStrategy,
                   # AUCTION_MATCH, AUCTION_IMPROVEMENT, AUCTION_TRANSPARENT
                   self.conn.make_field_handle_empty(order.startingPrice),
                   self.conn.make_field_handle_empty(order.stockRefPrice),
                   self.conn.make_field_handle_empty(order.delta),
                   self.conn.make_field_handle_empty(order.stockRangeLower),
                   self.conn.make_field_handle_empty(order.stockRangeUpper),

                   order.overridePercentageConstraints,  # srv v22 and above

                   # Volatility orders (srv v26 and above)
                   self.conn.make_field_handle_empty(order.volatility),
                   self.conn.make_field_handle_empty(order.volatilityType),
                   order.deltaNeutralOrderType,  # srv v28 and above
                   self.conn.make_field_handle_empty(order.deltaNeutralAuxPrice)]  # srv v28 and above

        if self.server_version() >= MIN_SERVER_VER_DELTA_NEUTRAL_CONID and order.deltaNeutralOrderType:
            fields += [order.deltaNeutralConId, order.deltaNeutralSettlingFirm, order.deltaNeutralClearingAccount,
                       order.deltaNeutralClearingIntent]

        if self.server_version() >= MIN_SERVER_VER_DELTA_NEUTRAL_OPEN_CLOSE and order.deltaNeutralOrderType:
            fields += [order.deltaNeutralOpenClose,
                       order.deltaNeutralShortSale,
                       order.deltaNeutralShortSaleSlot,
                       order.deltaNeutralDesignatedLocation]

        fields += [order.continuousUpdate,
                   self.conn.make_field_handle_empty(order.referencePriceType),
                   self.conn.make_field_handle_empty(order.trailStopPrice)]  # srv v30 and above

        if self.server_version() >= MIN_SERVER_VER_TRAILING_PERCENT:
            fields.append(self.conn.make_field_handle_empty(order.trailingPercent))

        # SCALE orders
        if self.server_version() >= MIN_SERVER_VER_SCALE_ORDERS2:
            fields += [self.conn.make_field_handle_empty(order.scaleInitLevelSize),
                       self.conn.make_field_handle_empty(order.scaleSubsLevelSize)]
        else:
            # srv v35 and above)
            fields += ["",  # for not supported scaleNumComponents
                       self.conn.make_field_handle_empty(order.scaleInitLevelSize)]  # for scaleComponentSize

        fields.append(self.conn.make_field_handle_empty(order.scalePriceIncrement))

        if self.server_version() >= MIN_SERVER_VER_SCALE_ORDERS3 \
                and order.scalePriceIncrement != UNSET_DOUBLE \
                and order.scalePriceIncrement > 0.0:
            fields += [self.conn.make_field_handle_empty(order.scalePriceAdjustValue),
                       self.conn.make_field_handle_empty(order.scalePriceAdjustInterval),
                       self.conn.make_field_handle_empty(order.scaleProfitOffset),
                       order.scaleAutoReset,
                       self.conn.make_field_handle_empty(order.scaleInitPosition),
                       self.conn.make_field_handle_empty(order.scaleInitFillQty),
                       order.scaleRandomPercent]

        if self.server_version() >= MIN_SERVER_VER_SCALE_TABLE:
            fields += [order.scaleTable, order.activeStartTime, order.activeStopTime]

        # HEDGE orders
        if self.server_version() >= MIN_SERVER_VER_HEDGE_ORDERS:
            fields.append(order.hedgeType)
            if order.hedgeType:
                fields.append(order.hedgeParam)

        if self.server_version() >= MIN_SERVER_VER_OPT_OUT_SMART_ROUTING:
            fields.append(order.optOutSmartRouting)

        if self.server_version() >= MIN_SERVER_VER_PTA_ORDERS:
            fields += [order.clearingAccount, order.clearingIntent]

        if self.server_version() >= MIN_SERVER_VER_NOT_HELD:
            fields.append(order.notHeld)

        if self.server_version() >= MIN_SERVER_VER_DELTA_NEUTRAL:
            if contract.deltaNeutralContract:
                fields += [True,
                           contract.deltaNeutralContract.conId,
                           contract.deltaNeutralContract.delta,
                           contract.deltaNeutralContract.price]
            else:
                fields.append(False)

        if self.server_version() >= MIN_SERVER_VER_ALGO_ORDERS:
            fields.append(order.algoStrategy)
            if order.algoStrategy:
                algoParamsCount = len(order.algoParams) if order.algoParams else 0
                fields.append(algoParamsCount)
                if algoParamsCount > 0:
                    for algoParam in order.algoParams:
                        fields += [algoParam.tag, algoParam.value]

        if self.server_version() >= MIN_SERVER_VER_ALGO_ID:
            fields.append(order.algoId)

        fields.append(order.whatIf)  # srv v36 and above

        # send miscOptions parameter
        if self.server_version() >= MIN_SERVER_VER_LINKING:
            miscOptionsStr = ""
            if order.orderMiscOptions:
                for tagValue in order.orderMiscOptions:
                    miscOptionsStr += str(tagValue)
            fields.append(miscOptionsStr)

        if self.server_version() >= MIN_SERVER_VER_ORDER_SOLICITED:
            fields.append(order.solicited)

        if self.server_version() >= MIN_SERVER_VER_RANDOMIZE_SIZE_AND_PRICE:
            fields.extend([order.randomizeSize, order.randomizePrice])

        if self.server_version() >= MIN_SERVER_VER_PEGGED_TO_BENCHMARK:
            if order.orderType == "PEG BENCH":
                fields.extend([order.referenceContractId, order.isPeggedChangeAmountDecrease, order.peggedChangeAmount,
                               order.referenceChangeAmount, order.referenceExchangeId])

            fields.append(len(order.conditions))

            if len(order.conditions) > 0:
                for cond in order.conditions:
                    fields.append(cond.type())
                    # TODO: make sure I ported logic in whatever happens 1 line below
                    # fields += cond.self.conn.make_message()

                fields.extend([order.conditionsIgnoreRth, order.conditionsCancelOrder])

            fields.extend([order.adjustedOrderType, order.triggerPrice, order.lmtPriceOffset, order.adjustedStopPrice,
                           order.adjustedTrailingAmount, order.adjustableTrailingUnit])

        if self.server_version() >= MIN_SERVER_VER_EXT_OPERATOR:
            fields.append(order.extOperator)

        if self.server_version() >= MIN_SERVER_VER_SOFT_DOLLAR_TIER:
            fields.extend([order.softDollarTier.name, order.softDollarTier.val])

        if self.server_version() >= MIN_SERVER_VER_CASH_QTY:
            fields.append(order.cashQty)

        if self.server_version() >= MIN_SERVER_VER_DECISION_MAKER:
            fields.append(order.mifid2DecisionMaker)
            fields.append(order.mifid2DecisionAlgo)

        if self.server_version() >= MIN_SERVER_VER_MIFID_EXECUTION:
            fields.append(order.mifid2ExecutionTrader)
            fields.append(order.mifid2ExecutionAlgo)

        if self.server_version() >= MIN_SERVER_VER_AUTO_PRICE_FOR_HEDGE:
            fields.append(order.dontUseAutoPriceForHedge)

        if self.server_version() >= MIN_SERVER_VER_ORDER_CONTAINER:
            fields.append(order.isOmsContainer)

        self.conn.send_message(fields)

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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REPLACE_FA, message_version, faData, cxml]
        self.conn.send_message(fields)

    def request_account_updates(self, subscribe: bool, account_code: str):
        """Call this function to start getting account values, portfolio,
        and last update time information via EWrapper.updateAccountValue(),
        EWrapperi.updatePortfolio() and Wrapper.updateAccountTime().

        subscribe:bool - If set to TRUE, the client will start receiving account
            and Portfoliolio updates. If set to FALSE, the client will stop
            receiving this information.
        account_code:str -The account code for which to receive account and
            portfolio updates."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 2

        fields = [OUT.REQ_ACCT_DATA, message_version, subscribe, account_code]
        self.conn.send_message(fields)

    def request_account_updates_multi(self, request_id: int, account: str, model_code: str,
                                      ledgerAndNLV: bool):
        """Requests account updates for account and/or model."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_MODELS_SUPPORT:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support account updates multi request.")
            return

        message_version = 1
        fields = [OUT.REQ_ACCOUNT_UPDATES_MULTI, message_version, request_id, account, model_code, ledgerAndNLV]
        self.conn.send_message(fields)

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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_ACCOUNT_SUMMARY, message_version, request_id, group_name, tags]
        self.conn.send_message(fields)

    def request_all_open_orders(self):
        """Call this function to request the open orders placed from all
        clients and also from TWS. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  No association is made between the returned orders and the
        requesting client."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_ALL_OPEN_ORDERS, message_version]
        self.conn.send_message(fields)

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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_AUTO_OPEN_ORDERS, message_version, auto_bind]
        message_sent = self.conn.send_message(fields)
        return message_sent

    def request_contract_details(self, contract: Contract, request_id=None):
        """Call this function to download all details for a particular
        underlying. The contract details will be received via the contractDetails()
        function on the EWrapper.

        request_id:int - The ID of the data request. Ensures that responses are
            make_fieldatched to requests if several requests are in process.
        contract:Contract - The summary description of the contract being looked
            up."""

        if request_id is None:
           request_id = self.get_local_request_id()

        # send req mkt data msg
        message_version = 8
        fields = [OUT.REQ_CONTRACT_DATA, message_version, request_id, contract.id, contract.symbol,
                  contract.security_type, contract.last_trade_date_or_contract_month,contract.strike, contract.right,
                  contract.multiplier,contract.exchange, contract.primary_exchange]

        # Format the exchange field as required
        if (contract.primary_exchange and (contract.exchange == "BEST" or contract.exchange == "SMART")):
            field = contract.exchange + ":" + contract.primary_exchange
        else:
            field = contract.exchange
        fields.append(field)

        fields += [contract.currency, contract.local_symbol,contract.trading_class,contract.include_expired,
                   contract.security_id_type, contract.security_id]

        self._send_message(fields)
        return request_id

    def request_current_time(self):
        """Asks the current system time on the server side.

        Related Response Messages
        IN.CURRENT_TIME
        """
        message_version = 1
        fields = [OUT.REQ_CURRENT_TIME, message_version]
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
        fields = [ OUT.REQ_EXECUTIONS, message_version, request_id, client_id, account_code, time,
                   symbol, security_type, exchange, side]
        self._send_message(fields)

    def request_global_cancel(self):
        """Use this function to cancel all open orders globally. It
        cancels both API and TWS open orders.

        If the order was created in TWS, it also gets canceled. If the order
        was initiated in the API, it also gets canceled."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_GLOBAL_CANCEL, message_version]
        self.conn.send_message(fields)

    # Note that formatData parameter affects intraday bars only
    # 1-day bars always return with date in YYYYMMDD format
    def request_head_time_stamp(self, request_id: int, contract: Contract,
                                whatToShow: str, useRTH: int, formatDate: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_HEAD_TIMESTAMP:
            self.response_handler.error(request_id, UPDATE_TWS.code(),
                                        UPDATE_TWS.msg() + "  It does not support head time stamp requests.")
            return

        fields = [OUT.REQ_HEAD_TIMESTAMP, request_id, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class,
                  contract.include_expired, useRTH, whatToShow, formatDate]
        self.conn.send_message(fields)

    def request_historical_news(self, request_id: int, conId: int, providerCodes: str,
                                startDateTime: str, end_date_time: str, totalResults: int, historicalNewsOptions: list):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_HISTORICAL_NEWS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support historical news request.")
            return

        fields = [OUT.REQ_HISTORICAL_NEWS, request_id, conId, providerCodes, startDateTime, end_date_time, totalResults]

        # send historicalNewsOptions parameter
        if self.server_version() >= MIN_SERVER_VER_NEWS_QUERY_ORIGINS:
            func_options = ""
            if historicalNewsOptions:
                for tagValue in historicalNewsOptions:
                    func_options += str(tagValue)
            fields.appned(func_options)

        self.conn.send_message(fields)

    def request_historical_ticks(self, request_id: int, contract: Contract, startDateTime: str,
                                 end_date_time: str, number_of_ticks: int, whatToShow: str, useRth: int,
                                 ignoreSize: bool, miscOptions: list):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_HISTORICAL_TICKS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support historical ticks requests..")
            return

        miscOptionsString = ""
        if miscOptions:
            for tagValue in miscOptions:
                miscOptionsString += str(tagValue)

        fields = [OUT.REQ_HISTORICAL_TICKS, request_id, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class,
                  contract.include_expired, startDateTime, end_date_time, number_of_ticks, whatToShow, useRth,
                  ignoreSize, miscOptionsString]
        self.conn.send_message(fields)

    def request_managed_accounts(self):
        """Call this function to request the list of managed accounts. The list
        will be returned by the managedAccounts() function on the EWrapper.

        Note:  This request can only be made when connected to a FA managed account."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_MANAGED_ACCTS, message_version]
        self.conn.send_message(fields)

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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_MARKET_DATA_TYPE:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(),
                                        UPDATE_TWS.msg() + "  It does not support market data type requests.")
            return

        message_version = 1

        # send req mkt data msg
        fields = [OUT.REQ_MARKET_DATA_TYPE, message_version, market_data_type]
        self.conn.send_message(fields)

    def request_market_depth_exhanges(self):
        """

        :return:
        """

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_MKT_DEPTH_EXCHANGES:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support market depth exchanges request.")
            return

        fields = [OUT.REQ_MKT_DEPTH_EXCHANGES]
        self.conn.send_message(fields)

    def request_market_rule(self, market_rule_id: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_MARKET_RULES:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support market rule requests.")
            return

        fields = [OUT.REQ_MARKET_RULE, market_rule_id]
        self.conn.send_message(fields)

    def request_news_providers(self):
        """
        Request a list of news providers.

        :return: True/False - True if message was sent, False otherwise
        """

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_NEWS_PROVIDERS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support news providers request.")
            return

        fields = [OUT.REQ_NEWS_PROVIDERS]
        message_sent = self.conn.send_message(fields)
        return message_sent

    def request_open_orders(self):
        """Call this function to request the open orders that were
        placed from this client. Each open order will be fed back through the
        openOrder() and orderStatus() functions on the EWrapper.

        Note:  The client with a client_id of 0 will also receive the TWS-owned
        open orders. These orders will be associated with the client and a new
        order_id will be generated. This association will persist over multiple
        API and TWS sessions.  """

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_OPEN_ORDERS, message_version]
        self.conn.send_message(fields)

    def request_positions(self):
        """Requests real-time position data for all accounts."""

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_POSITIONS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support positions request.")
            return

        message_version = 1
        fields = [OUT.REQ_POSITIONS, message_version]
        self.conn.send_message(fields)

    def request_positions_multi(self, request_id: int, account: str, model_code: str):
        """Requests positions for account and/or model.
        Results are delivered via EWrapper.positionMulti() and
        EWrapper.positionMultiEnd() """

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_MODELS_SUPPORT:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support positions multi request.")
            return

        message_version = 1
        fields = [OUT.REQ_POSITIONS_MULTI, message_version, request_id, account, model_code]
        self.conn.send_message(fields)

    def request_smart_components(self, request_id: int, bboExchange: str):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_SMART_COMPONENTS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support smart components request.")
            return

        fields = [OUT.REQ_SMART_COMPONENTS, request_id, bboExchange]
        self.conn.send_message(fields)

    def set_server_log_level(self, logLevel: int):
        """The default detail level is ERROR. For more details, see API
        Logging."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(),
                                        NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.SET_SERVER_LOGLEVEL, message_version, logLevel]
        self.conn.send_message(fields)

    def start_api(self):
        """  Initiates the message exchange between the client application and
        the TWS/IB Gateway. """

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 2
        fields = [OUT.START_API, message_version, self.client_id]

        if self.server_version() >= MIN_SERVER_VER_OPTIONAL_CAPABILITIES:
            fields.append(self.optional_capabilities)

        self.conn.send_message(fields)

    def subscribe_to_group_events(self, request_id: int, groupId: int):
        """request_id:int - The unique number associated with the notification.
        groupId:int - The ID of the group, currently it is a number from 1 to 7.
            This is the display group subscription request sent by the API to TWS."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support subscribeToGroupEvents request.")
            return

        message_version = 1
        fields = [OUT.SUBSCRIBE_TO_GROUP_EVENTS, message_version, request_id, groupId]
        self.conn.send_message(fields)

    # Not Alphabetically\\
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
        self.application_state = "Establishing Connection to Bridge (TWS/IBGW)"
        self.host = host
        self.port = port
        self.client_id = client_id
        logger.info("Connecting to %s:%d w/ id:%d", self.host, self.port, self.client_id)
        self.conn = BridgeConnection(self.host, self.port)

        try:
            self.conn.connect()

            v100prefix = "API\0"
            v100version = "v%d..%d" % (MIN_CLIENT_VER, MAX_CLIENT_VER)

            msg = self.conn.make_msg(v100version)
            logger.debug("msg %s", msg)
            msg2 = str.encode(v100prefix, 'ascii') + msg
            logger.debug("msg2 %s", msg2)
            self.conn.send_message(msg2)

            message = self.conn.receive_messages()[0]
            (server_version, conn_time) = self.conn.read_fields(message['text'])

            self.connection_time = conn_time
            logger.info("Connection Time: {0}".format(self.connection_time))

            self.server_version_ = int(server_version)
            logger.info("Server Version: {0}".format(self.server_version_))

            # logger.info("sent start_api")
            self.start_api()

            if self.response_handler:
                self.response_handler.connectAck()

        except socket.error:
            logging.error(socket.error)
            if self.response_handler:
                self.response_handler.error(NO_VALID_ID, CONNECT_FAIL.code(), CONNECT_FAIL.msg())
            logger.info("could not connect")
            self.conn.disconnect()
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)



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

        # Get the request id for this work
        #request_id = self.conn.generate_request_id()

        # Create Message
        request_id = 29
        fields = [OUT.REQ_HISTORICAL_DATA, request_id, contract.id, contract.symbol, contract.security_type,
                    contract.last_trade_date_or_contract_month,
                    contract.strike, contract.right, contract.multiplier, contract.exchange,
                    contract.primary_exchange, contract.currency, contract.local_symbol, contract.trading_class,
                    contract.include_expired,end_date_time, bar_size_setting, duration, use_rth, what_to_show, format_date]


       # Send combo legs for BAG requests
        if contract.security_type == "BAG":
            fields.append(len(contract.comboLegs))
            for comboLeg in contract.comboLegs:
                fields.append(comboLeg.contract_id)
                fields.append(comboLeg.ratio)
                fields.append(comboLeg.action)
                fields.append(comboLeg.exchange)


        fields.append(keep_up_to_date)
        # send chartOptions parameter
        chart_options_str = ""
        if chart_options:
            for tagValue in chart_options:
                chart_options_str += str(tagValue)
        fields.append(chart_options_str)

        # Send the Message
        self._send_message(fields)


    def request_news_bulletins(self, allMsgs: bool):
        """Call this function to start receiving news bulletins. Each bulletin
        will be returned by the updateNewsBulletin() event.

        allMsgs:bool - If set to TRUE, returns all the existing bulletins for
        the currencyent day and any new ones. If set to FALSE, will only
        return new bulletins. """

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_NEWS_BULLETINS, message_version, allMsgs]
        self.conn.send_message(fields)

    def request_pnl(self, request_id: int, account: str, model_code: str):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_PNL:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support PnL request.")
            return

        fields = [OUT.REQ_PNL, request_id, account, model_code]
        self.conn.send_message(fields)

    def request_pnl_single(self, request_id: int, account: str, model_code: str, contract_id: int):

        self.log_request(current_fn_name(), vars())

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_PNL:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support PnL request.")
            return

        fields = [OUT.REQ_PNL_SINGLE, request_id, account, model_code, contract_id]
        self.conn.send_message(fields)

    def request_tick_by_tick_data(self, request_id: int, contract: Contract, tick_type: str,
                                  number_of_ticks: int, ignoreSize: bool):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_TICK_BY_TICK:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support tick-by-tick data requests.")
            return

        if self.server_version() < MIN_SERVER_VER_TICK_BY_TICK_IGNORE_SIZE:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support ignoreSize and number_of_ticks parameters "
                                        "in tick-by-tick data requests.")
            return

        fields = [OUT.REQ_TICK_BY_TICK_DATA, request_id, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class, tick_type
                  ]
        if self.server_version() >= MIN_SERVER_VER_TICK_BY_TICK_IGNORE_SIZE:
            fields.append(number_of_ticks)
            fields.append(ignoreSize)

        self.conn.send_message(fields)

    def server_version(self):
        """Returns the version of the TWS instance to which the API
        application is connected."""

        return self.server_version_

    def verify_request(self, apiName: str, api_version: str):
        """
        Allows for an application to request what the correct message should be for a given api/version.
        """


        #if not self.extraAuth:
        #    self.response_handler.error(NO_VALID_ID, BAD_MESSAGE.code(), BAD_MESSAGE.msg() +
        #                                "  Intent to authenticate needs to be expressed during initial connect request.")
        #    return

        message_version = 1
        fields = [OUT.VERIFY_REQUEST, message_version, apiName, api_version]
        self._send_message(fields)

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

        if not self.conn.is_connected():
            self.response_handler.error(request_id, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_DELTA_NEUTRAL:
            if contract.deltaNeutralContract:
                self.response_handler.error(request_id, UPDATE_TWS.code(),
                                            UPDATE_TWS.msg() + "  It does not support delta-neutral orders.")
                return

        if self.server_version() < MIN_SERVER_VER_REQ_MKT_DATA_CONID:
            if contract.id > 0:
                self.response_handler.error(request_id, UPDATE_TWS.code(),
                                            UPDATE_TWS.msg() + "  It does not support id parameter.")
                return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class:
                self.response_handler.error(request_id, UPDATE_TWS.code(),
                                            UPDATE_TWS.msg() + "  It does not support trading_class parameter in reqMktData.")
                return

        message_version = 11

        # send req mkt data msg
        insert_offset = 0
        fields = [OUT.REQ_MKT_DATA, message_version, request_id, contract.symbol, contract.security_type,
                          contract.last_trade_date_or_contract_month,
                          contract.strike, contract.right, contract.multiplier, contract.exchange,
                          contract.primary_exchange,
                          contract.currency, contract.local_symbol]

        # Send Contract Fields
        if self.server_version() >= MIN_SERVER_VER_REQ_MKT_DATA_CONID:
            fields.insert(3, contract.id)
            insert_offset += 1

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields.append(contract.trading_class)
            insert_offset += 1

        # Send combo legs for BAG requests (srv v8 and above)
        if contract.security_type == "BAG":
            combo_leg_count = len(contract.comboLegs) if contract.comboLegs else 0
            fields.append(combo_leg_count)
            for comboLeg in contract.comboLegs:
                fields.append(comboLeg.conId)
                fields.append(comboLeg.ratio)
                fields.append(comboLeg.action)
                fields.append(comboLeg.exchange)

        # Send Delta Neutral Contract Fields
        if self.server_version() >= MIN_SERVER_VER_DELTA_NEUTRAL:
            if contract.deltaNeutralContract:
                fields.append(True)
                fields.append(contract.deltaNeutralContract.conId)
                fields.append(contract.deltaNeutralContract.delta)
                fields.append(contract.deltaNeutralContract.price)
            else:
                fields.append(False)

        fields.append(generic_tick_list)
        fields.append(snapshot)

        if self.server_version() >= MIN_SERVER_VER_REQ_SMART_COMPONENTS:
            fields.append(regulatory_snapshot)

        # send mktDataOptions parameter
        # TODO: Clarify if the code is beneficial
        # if self.server_version() >= MIN_SERVER_VER_LINKING:
        #    # current doc says this part if for "internal use only" -> won't support it
        #    if mktDataOptions:
        #        raise NotImplementedError("not supported")
        #    mktDataOptionsStr = ""
        #    fields += [mktDataOptionsStr), ]

        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    def twsConnectionTime(self):
        """Returns the time the API application made a connection to TWS."""

        return self.connection_time

    def request_ids(self, numIds: int):
        """Call this function to request from TWS the next valid ID that
        can be used when placing an order.  After calling this function, the
        nextValidId() event will be triggered, and the id returned is that next
        valid ID. That ID will reflect any autobinding that has occurred (which
        generates new IDs and increments the next valid ID therein).

        numIds:int - deprecated"""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_IDS, message_version, numIds]
        self.conn.send_message(fields)

    def request_MktDepth(self, request_id: int, contract: Contract,
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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class or contract.id > 0:
                self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                            "  It does not support id and trading_class parameters in reqMktDepth.")
                return

        if self.server_version() < MIN_SERVER_VER_SMART_DEPTH and isSmartDepth:
            self.response_handler.error(request_id, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support SMART depth request.")
            return

        message_version = 5

        # send req mkt depth msg
        fields = [OUT.REQ_MKT_DEPTH, message_version, request_id]

        # send contract fields
        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields += [contract.id, ]
        fields += [contract.symbol,
                   contract.security_type,
                   contract.last_trade_date_or_contract_month,
                   contract.strike,
                   contract.right,
                   contract.multiplier,  # srv v15 and above
                   contract.exchange,
                   contract.currency,
                   contract.local_symbol]

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields += [contract.trading_class, ]

        fields += [numRows, ]  # srv v19 and above

        if self.server_version() >= MIN_SERVER_VER_SMART_DEPTH:
            fields += [isSmartDepth, ]

        # send mktDepthOptions parameter
        if self.server_version() >= MIN_SERVER_VER_LINKING:
            # current doc says this part if for "internal use only" -> won't support it
            if mktDepthOptions:
                raise NotImplementedError("not supported")
            mktDataOptionsStr = ""
            fields += [mktDataOptionsStr, ]

        self.conn.send_message(fields)

    def cancel_news_bulletins(self):
        """Call this function to stop receiving news bulletins."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.CANCEL_NEWS_BULLETINS, message_version]
        self.conn.send_message(fields)

    def request_uestFA(self, faData: int):
        """Call this function to request FA configuration information from TWS.
        The data returns in an XML string via a "receiveFA" ActiveX event.

        faData:int - Specifies the type of Financial Advisor
            configuration data beingingg requested. Valid values include:
            1 = GROUPS
            2 = PROFILE
            3 = ACCOUNT ALIASES"""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1

        fields = [OUT.REQ_FA, message_version, int(faData)]
        self.conn.send_message(fields)

    def cancel_historical_data(self, request_id: int):
        """Used if an internet disconnect has occurred or the results of a query
        are otherwise delayed and the application is no longer interested in receiving
        the data.

        request_id:int - The ticker ID. Must be a unique value."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.CANCEL_HISTORICAL_DATA, message_version, request_id]
        self.conn.send_message(fields)

    def cancel_head_time_stamp(self, request_id: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_CANCEL_HEADTIMESTAMP:
            self.response_handler.error(request_id, UPDATE_TWS.code(),
                                        UPDATE_TWS.msg() + "  It does not support head time stamp requests.")
            return

        fields = [OUT.CANCEL_HEAD_TIMESTAMP, request_id]
        self.conn.send_message(fields)

    def request_HistogramData(self, tickerId: int, contract: Contract,
                              useRTH: bool, timePeriod: str):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_HISTOGRAM:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support histogram requests..")
            return

        fields = [OUT.REQ_HISTOGRAM_DATA, tickerId, contract.id, contract.symbol, contract.security_type,
                  contract.last_trade_date_or_contract_month, contract.strike, contract.right, contract.multiplier,
                  contract.exchange, contract.primary_exchange, contract.currency, contract.local_symbol,
                  contract.trading_class, contract.include_expired, useRTH,
                  timePeriod]
        self.conn.send_message(fields)

    def cancelHistogramData(self, tickerId: int):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_HISTOGRAM:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support histogram requests..")
            return

        fields = [OUT.CANCEL_HISTOGRAM_DATA, tickerId]
        self.conn.send_message(fields)

    def request_scanner_parameters(self):
        """Requests an XML string that describes all possible scanner queries."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        message_version = 1
        fields = [OUT.REQ_SCANNER_PARAMETERS, message_version]
        self.conn.send_message(fields)

    def request_scanner_subscription(self, request_id: int,
                                     subscription: ScannerSubscription,
                                     scannerSubscriptionOptions: list,
                                     scannerSubscriptionFilterOptions: list):
        """request_id:int - The ticker ID. Must be a unique value.
        scannerSubscription:ScannerSubscription - This structure contains
            possible parameters used to filter results.
        scannerSubscriptionOptions:list - For internal use only.
            Use default value XYZ."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_SCANNER_GENERIC_OPTS and scannerSubscriptionFilterOptions is not None:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        " It does not support API scanner subscription generic filter options")
            return

        message_version = 4

        fields = [OUT.REQ_SCANNER_SUBSCRIPTION]

        if self.server_version() < MIN_SERVER_VER_SCANNER_GENERIC_OPTS:
            fields.append(message_version)

        fields += [request_id,
                   self.conn.make_field_handle_empty(subscription.numberOfRows),
                   subscription.instrument,
                   subscription.locationCode,
                   subscription.scanCode,
                   self.conn.make_field_handle_empty(subscription.abovePrice),
                   self.conn.make_field_handle_empty(subscription.belowPrice),
                   self.conn.make_field_handle_empty(subscription.aboveVolume),
                   self.conn.make_field_handle_empty(subscription.marketCapAbove),
                   self.conn.make_field_handle_empty(subscription.marketCapBelow),
                   subscription.moodyRatingAbove,
                   subscription.moodyRatingBelow,
                   subscription.spRatingAbove,
                   subscription.spRatingBelow,
                   subscription.maturityDateAbove,
                   subscription.maturityDateBelow,
                   self.conn.make_field_handle_empty(subscription.couponRateAbove),
                   self.conn.make_field_handle_empty(subscription.couponRateBelow),
                   subscription.excludeConvertible,
                   self.conn.make_field_handle_empty(subscription.averageOptionVolumeAbove),  # srv v25 and above
                   subscription.scannerSettingPairs,  # srv v25 and above
                   subscription.stockTypeFilter]  # srv v27 and above

        # send scannerSubscriptionFilterOptions parameter
        if self.server_version() >= MIN_SERVER_VER_SCANNER_GENERIC_OPTS:
            scannerSubscriptionFilterOptionsStr = ""
            if scannerSubscriptionFilterOptions:
                for tagValueOpt in scannerSubscriptionFilterOptions:
                    scannerSubscriptionFilterOptionsStr += str(tagValueOpt)
            fields += [scannerSubscriptionFilterOptionsStr]

        # send scannerSubscriptionOptions parameter
        if self.server_version() >= MIN_SERVER_VER_LINKING:
            scannerSubscriptionOptionsStr = ""
            if scannerSubscriptionOptions:
                for tagValueOpt in scannerSubscriptionOptions:
                    scannerSubscriptionOptionsStr += str(tagValueOpt)
            fields += [scannerSubscriptionOptionsStr, ]

        self.conn.send_message(fields)

    #########################################################################
    ################## Real Time Bars
    #########################################################################

    def request_RealTimeBars(self, request_id: int, contract: Contract, barSize: int,
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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_TRADING_CLASS:
            if contract.trading_class:
                self.response_handler.error(request_id, UPDATE_TWS.code(),
                                            UPDATE_TWS.msg() + "  It does not support id and trading_class parameter in reqRealTimeBars.")
                return

        message_version = 3

        fields = [OUT.REQ_REAL_TIME_BARS, message_version, request_id]

        # send contract fields
        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields.append(contract.id)

        fields.extend([contract.symbol, contract.security_type, contract.last_trade_date_or_contract_month,
                       contract.strike, contract.right, contract.multiplier, contract.exchange,
                       contract.primary_exchange,
                       contract.currency, contract.local_symbol])

        if self.server_version() >= MIN_SERVER_VER_TRADING_CLASS:
            fields += [contract.trading_class, ]

        fields += [barSize, whatToShow, useRTH]

        # send realTimeBarsOptions parameter
        if self.server_version() >= MIN_SERVER_VER_LINKING:
            realTimeBarsOptionsStr = ""
            if realTimeBarsOptions:
                for tagValueOpt in realTimeBarsOptions:
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

        # Create the message body
        message_version = 2
        fields = [OUT.REQ_FUNDAMENTAL_DATA, message_version, request_id, contract.id, contract.symbol,
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

    def request_news_article(self, request_id: int, providerCode: str, articleId: str, newsArticleOptions: list):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_NEWS_ARTICLE:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support news article request.")
            return

        fields = []

        fields += [OUT.REQ_NEWS_ARTICLE, request_id, providerCode, articleId]

        # send newsArticleOptions parameter
        if self.server_version() >= MIN_SERVER_VER_NEWS_QUERY_ORIGINS:
            newsArticleOptionsStr = ""
            if newsArticleOptions:
                for tagValue in newsArticleOptions:
                    newsArticleOptionsStr += str(tagValue)

            fields.append(newsArticleOptionsStr)

        self.conn.send_message(fields)

    #########################################################################
    ################## Display Groups
    #########################################################################

    def query_display_groups(self, request_id: int):
        """API requests used to integrate with TWS color-grouped windows (display groups).
        TWS color-grouped windows are identified by an integer number. Currently that number ranges from 1 to 7 and are mapped to specific colors, as indicated in TWS.

        request_id:int - The unique number that will be associated with the
            response """

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support query_display_groups request.")
            return

        message_version = 1
        fields = [OUT.QUERY_DISPLAY_GROUPS, message_version, request_id]
        self.conn.send_message(fields)

    def updateDisplayGroup(self, request_id: int, contractInfo: str):
        """request_id:int - The requestId specified in subscribeToGroupEvents().
        contractInfo:str - The encoded value that uniquely represents the
            contract in IB. Possible values include:

            none = empty selection
            contractID@exchange - any non-combination contract.
                Examples: 8314@SMART for IBM SMART; 8314@ARCA for IBM @ARCA.
            combo = if any combo is selected."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support updateDisplayGroup request.")
            return

        message_version = 1
        fields = [OUT.UPDATE_DISPLAY_GROUP, message_version, request_id, contractInfo]
        self.conn.send_message(fields)

    def unsubscribeFromGroupEvents(self, request_id: int):
        """request_id:int - The requestId specified in subscribeToGroupEvents()."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support unsubscribeFromGroupEvents request.")
            return

        message_version = 1

        fields = [OUT.UNSUBSCRIBE_FROM_GROUP_EVENTS, message_version, request_id]
        self.conn.send_message(fields)

    def verify_message(self, api_data: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support verification request.")
            return

        message_version = 1
        fields = [OUT.VERIFY_MESSAGE, message_version, api_data]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    def verify_and_auth_request(self, api_name: str, api_version: str,
                                opaqueIsvKey: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support verification request.")
            return

        if not self.extraAuth:
            self.response_handler.error(NO_VALID_ID, BAD_MESSAGE.code(), BAD_MESSAGE.msg() +
                                        "  Intent to authenticate needs to be expressed during initial connect request.")
            return

        message_version = 1
        fields = [OUT.VERIFY_AND_AUTH_REQUEST, message_version, api_name, api_version, opaqueIsvKey]
        self.conn.send_message(fields)

    def verify_and_auth_message(self, api_data: str, xyzResponse: str):
        """For IB's internal purpose. Allows to provide means of verification
        between the TWS and third party programs."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_LINKING:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support verification request.")
            return

        message_version = 1
        fields = [OUT.VERIFY_AND_AUTH_MESSAGE, message_version, api_data, xyzResponse]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

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

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_SEC_DEF_OPT_PARAMS_REQ:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support security definition option request.")
            return

        fields = [OUT.REQ_SEC_DEF_OPT_PARAMS, request_id, underlying_symbol,
                  futFopExchange, underlyingSecType, underlyingConId]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    def request_soft_dollar_tiers(self, request_id: int):
        """Requests pre-defined Soft Dollar Tiers. This is only supported for
        registered professional advisors and hedge and mutual funds who have
        configured Soft Dollar Tiers in Account Management."""

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        fields = [OUT.REQ_SOFT_DOLLAR_TIERS, request_id]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    def request_family_codes(self):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_FAMILY_CODES:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support family codes request.")
            return

        fields = [OUT.REQ_FAMILY_CODES]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)

    def request_matching_symbols(self, request_id: int, pattern: str):

        if not self.conn.is_connected():
            self.response_handler.error(NO_VALID_ID, NOT_CONNECTED.code(), NOT_CONNECTED.msg())
            return

        if self.server_version() < MIN_SERVER_VER_REQ_MATCHING_SYMBOLS:
            self.response_handler.error(NO_VALID_ID, UPDATE_TWS.code(), UPDATE_TWS.msg() +
                                        "  It does not support matching symbols request.")
            return

        # Create and send the Message
        fields = [OUT.REQ_MATCHING_SYMBOLS, request_id, pattern]
        message = self.conn.make_message(fields)
        self.conn.send_message(message)