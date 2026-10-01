**Order is preserved.** Output rows follow input rows. They are laid out as your copied fields first and the model output last.

**Status codes.** A 400 names the file that did not match. A 404 means the experiment id is wrong.

**Two rules on this route.** The filename in `rows` has to match the uploaded filename, or you get a 400 naming the file. And `scoreMediaRequest` has to carry `fields`, `rows` and the media fields list.

So keep groups small. Keep your own record of which frame ids went into which request.
