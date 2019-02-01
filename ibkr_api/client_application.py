from ibkr_api.minimal_client_application    import MinimalClientApplication
from ibkr_api.base.message_parser           import MessageParser

import logging

logger = logging.getLogger(__name__)
class ClientApplication(MinimalClientApplication):
    def __init__(self, host, port, debug_mode=False):
        """
        Base class for users to extend in the creation of asynchronous event driven applications

        :param host: Host of the Bridge Connection
        :param port: Port of the Bridge Connection
        :param debug_mode: If True, warnings will be generated for non existing functions

        """
        super().__init__(host, port)


    #################################################################################
    # Functions that receive inbound messages from the Bridge Connection (TWS/IBGW) #
    #################################################################################
    def info_message(self, message_id, request_id, info):
        """
        Called when an info_message is received by the bridge.
        This function is meant to be overridden

        :param message_id:
        :param request_id:
        :param info:
        :return:
        """
        ticker_id = info['ticker_id']
        code      = info['code']
        text      = info['text']

        msg = """
        Message Id: {0} 
        Request ID: {1}
        Ticker ID : {2}
        Code      : {3}
        Text      : {4}
        """.format(message_id, request_id, ticker_id, code, text)
        logger.info(msg)

    def family_codes(self, account_data):
        account_id = account_data['account_id']
        family_code = account_data['family_code']

        msg = "Account ID: {0} Family Code: {1}".format(account_id, family_code)
        logger.info(msg)

    def managed_accounts(self,message_id, request_id, account):
        msg = "Message ID: {0}, Request ID: {1}, Account: {2}".format(message_id, request_id, account)
        logger.info(msg)


    def market_data_type(self, message_id, request_id, data):
        msg = "(Market Data Type) Message ID: {0}, Request ID: {1}, Account: {2}".format(message_id, request_id, data)
        logger.info(msg)

    def position_data(self, message_id, request_id,position_data):
        """
        Process the position_data inbound data

        :param message_id:
        :param request_id:
        :param position_data:
        :return:
        """
        pass

    def scanner_data(self, message_id, request_id, scanner_data):
        pass

    def tick_price(self, message_id, request_id, data):
        msg = "(Tick Price) Message ID: {0}, Request ID: {1}, Data: {2}".format(message_id, request_id, data)
        logger.info(msg)

    def tick_request_params(self, message_id, request_id, data):
        msg = "(Tick Request Params) Message ID: {0}, Request ID: {1}, Data: {2}".format(message_id, request_id, data)
        logger.info(msg)

    def tick_size(self, message_id, request_id, tick_data):
        msg = "(Tick Size) Message ID: {0}, Request ID: {1}, Data: {2}".format(message_id, request_id, tick_data)
        logger.info(msg)