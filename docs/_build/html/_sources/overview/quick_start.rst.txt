Quickstart Guide
================
Now that we have ibkr_api installed. Let us do some real work.
This module primarily offer you three interfaces to send and receive data.
The first interface, the IBKR_API class, is the simplest to use, as it hides much of the underlying complexity
of an asynchronous event driven api.


Request Handlers
================
Before a given api function is called. A check is performed to see if there is a corresponding "pre_<function_name>"
function. If so this function will be invoked before the API call is made. After the call is made, another check for a
"post_<function_name>" function.