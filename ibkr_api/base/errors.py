"""
Copyright (C) 2018 Interactive Brokers LLC. All rights reserved. This code is subject to the terms
and conditions of the IB API Non-Commercial License or the IB API Commercial License, as applicable.
"""

"""
This is the interface that will need to be overloaded by the customer so
that his/her code can receive info from the TWS/IBGW.
"""

class Errors(object):
    def already_connected(self):
        code    = 501
        message = "Application attempted to connect, while already connected"
        return code, message

    @staticmethod
    def connect_fail():
        code = 502
        message = "Couldn't connect to TWS. Confirm that \"Enable ActiveX and Socket EClients\" is enabled"
        message += "and connection port is the same as \"Socket Port\" on the TWS "
        message += "\"Edit->Global Configuration...->API->Settings\" menu.\n"
        message += "Live Trading ports: TWS: 7496; IB Gateway: 4001.\n"
        message += "Simulated Trading ports for new installations of version 954.1 or newer:  TWS: 7497; IB Gateway: 4002\n"

        return {'code':code , 'message':message }



class CodeMsgPair:
    def __init__(self, code, msg):
        self.errorCode = code
        self.errorMsg = msg

    def code(self):
        return self.errorCode

    def msg(self, field=None, extra=None):
        msg = self.errorMsg
        if field:
            msg += " The parameter '{0}' is not supported.".format(field)

        if extra:
            msg += extra
        return msg


ALREADY_CONNECTED = CodeMsgPair(501, "Already connected.")
CONNECT_FAIL = CodeMsgPair(502,
                           """Couldn't connect to TWS. Confirm that \"Enable ActiveX and Socket EClients\" 
                           is enabled and connection port is the same as \"Socket Port\" on the 
                           TWS \"Edit->Global Configuration...->API->Settings\" menu. Live Trading ports: 
                           TWS: 7496; IB Gateway: 4001. Simulated Trading ports for new installations 
                           of version 954.1 or newer:  TWS: 7497; IB Gateway: 4002""")
UPDATE_TWS = CodeMsgPair(503, "The TWS is out of date and must be upgraded.")
NOT_CONNECTED = CodeMsgPair(504, "Not connected")
UNKNOWN_ID = CodeMsgPair(505, "Fatal Error: Unknown message id.")
UNSUPPORTED_VERSION = CodeMsgPair(506, "Unsupported version")
BAD_LENGTH = CodeMsgPair(507, "Bad message length")
BAD_MESSAGE = CodeMsgPair(508, "Bad message")
SOCKET_EXCEPTION = CodeMsgPair(509, "Exception caught while reading socket - ")
FAIL_CREATE_SOCK = CodeMsgPair(520, "Failed to create socket")
SSL_FAIL = CodeMsgPair(530, "SSL specific error: ")

