**If we send 50 frames in one request, do the results come back in the same order?**

**Yes.** Results come back in the same order as the frames you send.

Order has been verified for requests of up to 20 frames. Above that it is expected to hold, but it has not been verified.

So for 50 frames, either send one request and keep your own record of which frame ids went into it, or split into groups of 20 or fewer.
