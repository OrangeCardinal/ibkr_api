=====================
IBKR_API Architecture
=====================
The IBKR_API is NOT some wrapper on top of the existing twsapi python API, but rather a complete redesign of the codebase.
The new codebase was written with the following ideas in mind. One, a 'design by contract' approach was used, where each
portion of the system has

Directory Structure
-------------------
+-----------+---------------------------------------------------------------------------------------------------------+
| Directory | Description                                                                                             |
+===========+=========================================================================================================+
| base/      | The core application internals. Unless you are developing for the API this code this code won't be used |
+-----------+---------------------------------------------------------------------------------------------------------+
|classes/contracts  | Various types of Contract objects such as Stock, Option, Put, Call, etc                         |
+-----------+---------------------------------------------------------------------------------------------------------+

There are three primary interfaces to use. For basic usage the *IBKR_API* class is your best bet. This class hides the
complexity of the underlying asynchronous interface provided by the application Bridge (TWS or the IB Gateway) and gives
you a straight forward way to query data.

For those users looking to implement real time algorithmic trading systems  the *ClientApplication* class is the right
place to start. This class provides an interface similar to what is provided by the official API, minus the artificial
complexity.



