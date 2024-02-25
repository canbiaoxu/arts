from math import ceil


def cut_data(data, group_size):
    return [data[group_size*(i-1): group_size*i] for i in range(1, ceil(len(data)/group_size)+1)]