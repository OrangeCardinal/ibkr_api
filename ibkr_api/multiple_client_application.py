from ibkr_api.base.api_calls import ApiCalls
from ibkr_api.base import MessageParser
import logging
import time


logger = logging.getLogger(__name__)
class MultipleClientApplication(ApiCalls):
    def __init__(self, host, port):
        """

        :param host: Host of the Bridge Connection
        :param port: Port of the Bridge Connection
        :param response_handler: User Supplied Response Handler
        :param request_handler:
        """
        self.still_running      = True  # Controls when the event loop
        self.messages_received  = []    # List of all messages received (not sure if needed)
        self.keyboard_input     = []    # Keyboard Input
        self.message_parser     = MessageParser()
        self.client_id          = 0
        self.debug_mode         = True

        super().__init__()
        super().connect(host, port, self.client_id)

    def register(self):
        """
        Action if any your application should do at the end of each event loop
        :return:
        """
        raise NotImplementedError


    def info_message(self, message_id, request_id, info):
        print(info)

    def initialize(self):
        """
        Called one time before the main event processing loop is entered.
        :return:
        """
        raise NotImplementedError

    def managed_accounts(self,message_id, request_id, account):
        print(request_id)
        print(account)

    # TODO: Handle keyboard input in a non blocking manner
    def run(self):
        """
        Primary event loop of the application
        :return:
        """
        #timeStart = time.time()
        #timeOut = 20

        # keyboard_reader = KeyboardReader()
        # keyboard_reader.start()

        self.initialize()

        while self.still_running:
            messages = self.conn.receive_messages()
            for message in messages:
                    # Call the correct function in the message parser to parse and return the data
                    logging.debug("{0} message received".format(message['action']))
                    func = getattr(self.message_parser, message['action'])
                    data = func(message['fields'])

                    # Call the response handler as needed
                    # If we are in development also send a warning that a handler doesnt exist
                    if hasattr(self, message['action']):
                        func = getattr(self, message['action'])
                        func(*data)
                    elif self.debug_mode:
                        logger.warning("The function '{0}' does not exist.".format(message['action']))

            # Invoke any user defined behaviour at this point.
            self.act()
            time.sleep(1)

        logger.info("Application has been shut down.")
        return 0

    def stop(self):
        """
        Stops the primary event loop, allowing the application to
        :return:
        """
        logger.info("Shutdown requested")
        self.still_running = False