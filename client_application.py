from base.api_calls import ApiCalls
from base.message_parser import MessageParser
import logging
import time


logger = logging.getLogger(__name__)
class ClientApplication(ApiCalls):
    def __init__(self, host, port, response_handler='default', request_handler='default'):
        """

        :param host: Host of the Bridge Connection
        :param port: Port of the Bridge Connection
        :param response_handler: User Supplied Response Handler
        :param request_handler:
        """
        self.still_running     = False # Controls when the event loop
        self.messages_received = []    # List of all messages received (not sure if needed)
        self.keyboard_input    = []    # Keyboard Input
        self.message_parser    = MessageParser()

    def act(self):
        """
        Action if any your application should do at the end of each event loop
        :return:
        """
        raise NotImplementedError

    def on_start(self):
        """
        Initial actions that your application will do on startup.
        :return:
        """
        raise NotImplementedError



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

        self.on_start()

        while self.still_running:
            messages = self.conn.receive_messages()
            for message in messages:
                    # Call the correct function in the message parser to parse and return the data
                    func = getattr(self.message_parser, message['action'])
                    data = func(message['fields'])

                    # Call the response handler as needed
                    #TODO: Figure out if we care about the return value here
                    func = getattr(self.response_handler, message['action'])
                    func(data)


            # Invoke any user defined behaviour at this point.
            self.act()
            time.sleep(2)

        logger.info("Application is now shut down.")
        return 0

    def stop(self):
        """
        Stops the primary event loop
        :return:
        """
        logger.info("Application is now shutting down.")
        self.still_running = False