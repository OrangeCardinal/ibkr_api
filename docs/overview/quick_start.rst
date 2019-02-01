=================
Quick Start Guide
=================
Now that we have ibkr_api installed. Let us do some real work.

Let's start working with the data
---------------------------------

Creating Your Application
-------------------------
1. Create your own application class
2. Implement your initialize action
    a. Read any configuration information
    b. Connect to your application's database
    c. Get the initial valid order id
    d. Get the initial valid request id (next_valid_id



=====
F.A.Q
=====

How do I exit my application?
-----------------------------
At the end of each event loop iteration. A call is made to your classes act() function. When your application wants to
quit out, all you need to do is call the stop() function. This will set the still_running flag to false, and will then
exit normally.
