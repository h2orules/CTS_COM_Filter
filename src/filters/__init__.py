def run_filter_chain(line, source, filters):
    """
    Run a line through an ordered filter chain.

    Each filter whose matches() returns True gets to transform the line via
    process_line(). If any filter returns None the line is dropped and None is
    returned immediately (no further filters run).

    Returns the (possibly transformed) bytes to forward, or None to drop.
    """
    result = line
    for f in filters:
        if f.matches(result):
            result = f.process_line(result, source)
            if result is None:
                return None
    return result
