==========================
IBKR_API Client Quickstart
==========================
IBKR_API provides an interface that hides the inherent complexity of an event driven asynchronous
This page has several snippets for common tasks that you may want to do with this API. All the samples below
assume that the code from the Initial Setup block have already been executed, otherwise the code shown should be self
contained.

Initial Setup
-------------
.. code-block:: python

    from ibkr_api.api import IBKR_API
    from ibkr_api.classes.contracts.contract import Contract
    from ibkr_api.classes.stocks.dow30 import Dow30
    from historical_data_types import HistoricalDataType as HDT

    host = "127.0.0.1"
    port =
    ibkr = IBKR_API(host, port)

===================
Working With Orders
===================
Placing an Order
----------------
There are many various types of orders that can be placed and as such we will allow Interactive Brokers documentation
to explain every option. (Even I as the developer of this API do not know all permutations at this point). The main endpoint
to use is `place_order` . The order id simply must be a unique integer or a duplicate id error will be generated.


Placing a Limit Order
---------------------
The sample below shows a limit order being placed to purchase 1 share of Bank of America Stock.

.. code-block:: python
   order_id = 60
   contract = Stock('BAC')
   contract.currency = "USD"
   contract.exchange = "SMART"

   total_quantity = 1
   limit_price = 26.5
   order = LimitOrder(OrderAction.BUY.value, contract, total_quantity, limit_price)
   ibkr.place_order(order_id, order)

Get all open orders
-------------------
Now that we know how to place an order. The next logical step is to check on that order.
This can be done with a call to `request_open_orders` which will return a list of `Order` objects.

.. code-block:: python
   open_orders = ibkr.request_all_open_orders()
   for open_order in open_orders:
    print(open_order)


===================
Other Functionality
===================
Get all linked accounts (aka 'Family Codes')
--------------------------------------------
.. code-block:: python

    family_codes = ibkr.request_family_codes()
    for code in family_codes:
        desc = "{0} - {1}".format(code['account_id'],code['family_code'])
        print(desc)

Find All Contracts that Match 'TSLA'
------------------------------------
.. code-block:: python

    request_id, contracts = ibkr.request_matching_symbols('TSLA')
    for c in contracts:
        print(c)
        for deriv_sec_type in c.derivative_security_types:
            print(deriv_sec_type)

Display Account Positions
-------------------------
.. code-block:: python

    position_data = ibkr.request_positions()
    for data in position_data:
        c = data['contract']
        desc = "{0:<10} {1:<10} {2:>20} {3:>30}".format(data['account'], c.local_symbol, data['position'], data['average_cost'])
        print(desc)

Get the option chains for all Dow 30 Stocks
-------------------------------------------
.. code-block:: python

   dow30 = Dow30()
   for stk in dow30.stocks():
       stk = ibkr.request_contract_data(stk)
       option_chains = ibkr.request_option_chains(stk)
       for opt_chain in option_chains:
           print(opt_chain)


Get the Last Year of Daily Prices for XOM
-----------------------------------------
.. code-block:: python

    dow30 = Dow30()
    # contract = Contract(symbol="XOM", security_type="STK") - Another way to get a contract
    contract = dow30.XOM()
    duration = "1 Y"
    (message_id, request_id, bar_data) = ibkr.request_historical_data(contract, '', duration, "1 day", HDT.TRADES.value, 1, 1, False, [])
    print("XOM Daily Closes")
    for bar in bar_data:
        print("{0}: {1}".format(bar.date, bar.close))
