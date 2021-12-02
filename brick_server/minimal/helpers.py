def striding_windows(l, w_size):
    curr_idx = 0
    while curr_idx < len(l):
        yield l[curr_idx : curr_idx + w_size]
        curr_idx += w_size
