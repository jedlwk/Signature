**If we send 50 frames in one request, do the results come back in the same order?**

**Yes, order is preserved.** Output rows follow input rows. So the first result belongs to the first frame.

This is verified for requests of up to 20 frames. A request of 50 frames is expected to behave the same way, but it is above the size that has been verified so far.

If you need that certainty today, send frames in groups of 20 or fewer.
