**Q: If we send 50 frames in one request, do the results come back in the same order?**

Yes. Results are returned in the same order as the frames you send, so the first result matches the first frame, and so on.

One note on testing: we have confirmed this behavior, but our own tests have only gone up to 20 frames per request. We have not tested 50. We expect the same ordering to hold, but we can't yet say we have verified it at that size.

If you plan to send 50 frames, we suggest including a frame ID with each one and matching results by ID instead of by position. If you'd like, we can also run a 50-frame test and share the outcome.
