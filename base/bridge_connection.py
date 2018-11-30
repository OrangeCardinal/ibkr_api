"""
Copyright (C) 2018 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""


"""
Bridge Connection between a client application and the bridge (TWS/IBGW)

Responsible For
1. Managing the socket between the app and the bridge
2. Properly creating low level messages for the bridge
3. Reading the bridge's responses and process/route them accordingly 
"""


import logging
import socket
import struct
import threading



from base.constants import DISCONNECTED, UNKNOWN, CONNECTED, message_id_response_map
from base.errors import FAIL_CREATE_SOCK, Errors
from base.messages import Messages
import sys

#TODO: support SSL !!

logger = logging.getLogger(__name__)


class BridgeConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.status = UNKNOWN
        self.request_id = -1

        self.lock = threading.Lock()


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
            raise e

        self.socket.settimeout(1)   #non-blocking

    def disconnect(self):
        self.lock.acquire()
        try:
            logger.debug("Closing socket connection to bridge (TWS/IBGW)")
            self.socket.close()
            self.socket = None
            self.status = DISCONNECTED
            logger.debug("disconnected")
        finally:
            self.lock.release()


    def is_connected(self):
        return ((self.socket is not None) and (self.status == CONNECTED))

    def generate_request_id(self):
        self.request_id += 1
        return self.request_id

    ###########################
    # Field Level abstraction #
    ###########################


    ###########################
    # Message Level Functions #
    ###########################
    def make_msg(self, text) -> bytes:
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
            logger.error("receive_message attempted while not connected.")
            return b""


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
        except Exception as e:
            logger.error(e)
            logger.error("Exception raised from receive_message %s", sys.exc_info())


        # Split the socket data into messages that can be passed back
        while socket_data != b"":
            (size, message, remaining_data) = self.read_message(socket_data)
            fields = Messages.parse_message(message)
            if not parse_message:
                messages.append(fields)
            else:
                function_name = Messages.get_inbound_action(fields[0])
                msg = {'size':size, 'text':message, 'fields':fields, 'id':fields[0], 'action':function_name, 'fields':fields}
                messages.append(msg)
            socket_data = remaining_data

        return messages

    def send_message(self, msg, make_msg=False):
        """
        Sends a message to the bridge
        :param msg:
        :return:
        """
        self.lock.acquire()

        # Make sure we are connected before attempting to send data
        if not self.is_connected():
            logger.debug("Attempting to send data with a closed connection. No data sent.")
            self.lock.release()
            return 0

        # Check if we received a list of fields, if so convert it to a proper message
        if isinstance(msg, list):
            msg = self.make_message(msg)

        # Send data, and release the lock
        #try:
        if make_msg:
            msg = self.make_msg(msg)
        nSent = self.socket.send(msg)
        logger.debug("Message Sent: {0}".format(msg))
        #except Exception as e:
        #    logger.error(e)
        #finally:
        self.lock.release()

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

    def make_field_handle_empty(self, val) -> str:

        if val is None:
            raise ValueError("Cannot send None to TWS")

        if UNSET_INTEGER == val or UNSET_DOUBLE == val:
            val = ""

        return self.make_field(val)

    def read_message(self, buf: bytes) -> tuple:
        """ first the size prefix and then the corresponding msg payload """
        if len(buf) < 4:
            return (0, "", buf)
        size = struct.unpack("!I", buf[0:4])[0]
        logger.debug("read_message: size: %d", size)
        if len(buf) - 4 >= size:
            text = struct.unpack("!%ds" % size, buf[4:4 + size])[0]
            return size, text, buf[4 + size:]
        else:
            return (size, "", buf)
