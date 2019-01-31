=====================
IBKR_API Architecture
=====================
The IBKR_API is NOT some wrapper on top of the existing twsapi python API, but rather a complete redesign of the codebase.
The new codebase was written with the following ideas in mind. One, a 'design by contract' approach was used, where each
portion of the system has clearly defined responsibilities. The other governing principle was to keep the code 'DRY'.

Directory Structure
-------------------
The table below describes various important directories within this API and their intended purpose

+-----------------------+--------------------------------------------------------------------------------------------------------------------+
| Directory             | Description                                                                                                        |
+=======================+====================================================================================================================+
| base                  | The core application internals. Unless you are developing for the API this code this code won't be called directly |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+
|classes/contracts      | Various types of Contract objects such as Stock, Option, Put, Call, etc                                            |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+
| classes/enum          | Various Enum and IntEnum classes that hold all legal values for whatever specific parameter they represent         |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+
| classes/orders        | Objects that represent various types of orders that can be placed such as Limit , Discretionary, etc               |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+
| classes/stocks        | Dow 30, S&P 500, etc (should/will probably be renamed to indexes...)                                               |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+
| api.py                | IBKR_API interface. Use this if you are looking for a simple synchronized interface                                |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+
| client_application.py | ClientApplication Interface. Use this if you are looking for a standard asynchronous event driven approach         |
+-----------------------+--------------------------------------------------------------------------------------------------------------------+


Interfaces
----------
There are three primary interfaces to use. For basic usage the `IBKR_API` class is your best bet. This class hides the
complexity of the underlying asynchronous interface provided by the application Bridge (TWS or the IB Gateway) and gives
you a straight forward way to query data.

For those users looking to implement real time algorithmic trading systems  the *ClientApplication* class is the right
place to start. This class provides an interface similar to what is provided by the official API, minus the artificial
complexity.



