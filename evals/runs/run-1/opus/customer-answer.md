**If we send 50 frames in one request, do the results come back in the same order?**

**Yes, order is preserved.** Output rows follow input rows. The first result belongs to the first frame, the second to the second, and so on.

This is verified for requests of up to 20 frames. We expect 50 frames to behave the same way, but that size has not been verified yet.

So for now, groups of 20 frames or fewer are the safe size. Keep your own record of which frame ids went into which request, so every result can be matched back to its frame.
