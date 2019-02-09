"""
Copyright (C) 2018 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""


"""
Bridge Connection between a client application and the bridge (TWS/IBGW)

:Responsible For:
1. Managing the socket between the app and the bridge
2. Properly creating low level messages for the bridge
3. Reading the bridge's responses and process/route them accordingly 
"""


import logging
import socket
import struct

from ibkr_api.base.constants    import DISCONNECTED, UNKNOWN, CONNECTED
from ibkr_api.base.errors       import FAIL_CREATE_SOCK, Errors
from ibkr_api.base.messages     import Messages

logger = logging.getLogger(__name__)

class BridgeConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.status = UNKNOWN
        self.request_id = -1

    def connect(self):
        self.status = CONNECTED

        # Create the socket itself
        try:
            self.socket = socket.socket()
        except socket.error:
            logger.error(FAIL_CREATE_SOCK.msg())
            self.status = DISCONNECTED


        # Bind to the specified host and port
        try:
            self.socket.connect((self.host, self.port))
        except socket.error as e:
            logger.error(Errors.connect_fail()['message'])
            self.status = DISCONNECTED

        self.socket.settimeout(1)   # Non-blocking mode (We won't wait for data on recv() calls

    def disconnect(self):
        logger.debug("Closing socket connection to the api bridge (TWS/IB Gateway)")
        self.socket.close()
        self.socket = None
        self.status = DISCONNECTED


    def is_connected(self):
        return ((self.socket is not None) and (self.status == CONNECTED))

    def generate_request_id(self):
        self.request_id += 1
        return self.request_id


    ###########################
    # Message Level Functions #
    ###########################
    @staticmethod
    def make_msg(text) -> bytes:
        """ adds the length prefix """
        msg = struct.pack("!I%ds" % len(text), len(text), str.encode(text))
        return msg

    def receive_messages(self, parse_message=True):
        """
        Read all data from the socket
        Parse the socket data into messages
        :param parse_message: False -> returns un-formatted data True -> returns msg dictionaries
        :return: messages:list All messages in the socket
        """
        """
        1. Receives any data available from the socket
        2. Split the received data into messages

        :return: messages:list
        """
        messages = []
        # Check that we are connected
        if not self.is_connected():
            logger.debug("receive_message attempted while not connected.")
            return messages


        # Read data from the socket
        socket_data = b""
        cont = True

        try:
            while cont and self.socket is not None:
                buffer = self.socket.recv(4096)
                socket_data += buffer
                logger.debug("Message Length: %d, Message:||%s||", len(buffer), buffer)

                if len(buffer) < 4096:
                    cont = False
        except Exception:
            pass


        # Split the socket data into messages that can be passed back
        while socket_data != b"":
            (size, message, remaining_data) = self.read_message(socket_data)
            fields = Messages.parse_message(message)
            if not parse_message:
                messages.append(fields)
            else:
                function_name = Messages.get_inbound_action(fields[0])
                msg = {'size':size, 'text':message, 'fields':fields, 'id':fields[0], 'action':function_name}
                messages.append(msg)
            socket_data = remaining_data

        return messages

    def send_message(self, msg, make_msg=False):
        """
        Sends a message to the bridge
        :param msg:
        :return:
        """

        # Check if we received a list of fields, if so convert it to a proper message
        if isinstance(msg, list):
            msg = self.make_message(msg)

        # Send data
        #try:
        if make_msg:
            msg = self.make_msg(msg)
        nSent = self.socket.send(msg)
        logger.debug("Message Sent: {0}".format(msg))

        return nSent

    #############################################################################
    # Functions related to low level message creation between our application   #
    # and the bridge (TWS/IBGW)                                                 #
    #############################################################################
    def make_message(self, values:list):
        """
        will replace make_msg in a few minutes
        :param values:
        :return:
        """
        message = ""
        for val in values:
            message += self.make_field(val)

        message = struct.pack("!I%ds" % len(message), len(message), str.encode(message))
        return message

    def make_field(self, val) -> str:
        """ adds the NULL string terminator """

        if val is None:
            raise ValueError("Cannot send None to TWS")

        # bool type is encoded as int
        if type(val) is bool:
            val = int(val)

        field = str(val) + '\0'
        return field


    def read_message(self, buf: bytes) -> tuple:
        """ first the size prefix and then the corresponding msg payload """

        if len(buf) < 4:
            return 0, "", buf

        size = struct.unpack("!I", buf[0:4])[0]

        if len(buf) - 4 >= size:
            text = struct.unpack("!%ds" % size, buf[4:4 + size])[0]
            return size, text, buf[4 + size:]
        else:
            return size, "", buf
