==================
Client Application
==================
To help get you started browse some representative usages of the API


How to Create a Market Scanner Subscription
-------------------------------------------
First create a Scanner object. This will contain the primary criteria to scan the market by.
Once we configure the scanner object, all we need to do is call request_scanner_subscription to start receiving data

.. code-block:: python

    scanner = Scanner()
    scanner.instrument      = "STK"
    scanner.location_code   = "STK.US.MAJOR"
    scanner.scan_code       = "HOT_BY_VOLUME"
    request_id = self.get_local_request_id()
    self.request_scanner_subscription(request_id, scanner, None, None)

The Bridge will periodically continue to refresh this information, so if the data is no longer required. It can be
stopped by calling cancel_scanner_subscription with the same request id that was supplied to the initial request.


.. code-block:: python

    self.cancel_scanner_subscription(request_id)
