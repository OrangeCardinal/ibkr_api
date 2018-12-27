How do I exit my application?
=============================
At the end of each event loop iteration. A call is made to your classes act() function. When your application wants to
quit out, all you need to do is call the stop() function. This will set the still_running flag to false, and will then
exit normally.
