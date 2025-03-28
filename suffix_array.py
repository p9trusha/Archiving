import sys

from bit_array import int_from_binary


sys.setrecursionlimit(10 ** 8)
s_index = 0
flag = False

def suffix_array(s, sorted_a, tab, n_of_rec, file):
    for i in range(len(sorted_a)):
        i_symb = (sorted_a[i] + n_of_rec) % len(s)
        tab[s[i_symb]].append(sorted_a[i])
    sorted_a = []
    for i in range(len(tab)):
        if tab[i]:
            sorted_a.append(tab[i])
            tab[i] = []
    for elem in sorted_a:
        if len(elem) == 1:
            global flag
            file.write(s[elem[0] - 1].to_bytes())
            if elem[0] == 0:
                flag = True
            global s_index
            if not flag:
                s_index += 1
        else:
            suffix_array(s, elem, tab, n_of_rec + 1, file)
    return s_index


def make_suffix_array(string, m):
    return make_suffix_array_by_induced_sorting(string)


def make_suffix_array_by_induced_sorting(string):
    type_map = build_type_map(string)
    bucket_sizes = find_bucket_sizes(string)
    print(bucket_sizes)
    guessed_suffix_array = guess_lms_sort(string, bucket_sizes, type_map)
    guessed_suffix_array = induce_sort_l(string, guessed_suffix_array, bucket_sizes, type_map)
    guessed_suffix_array = induce_sort_s(string, guessed_suffix_array, bucket_sizes, type_map)
    summary_string, summary_alfabet_size, summary_suffix_indexes = summarise_suffix_array(
        string, guessed_suffix_array, type_map)
    summary_suffix_array = make_summary_suffix_array(summary_string, summary_alfabet_size)
    result = accurate_lms_sort(
        string, bucket_sizes, summary_suffix_array, summary_suffix_indexes)
    result = induce_sort_l(string, result, bucket_sizes, type_map)
    result = induce_sort_s(string, result, bucket_sizes, type_map)
    return result

# s-type - true, l-type - false
def build_type_map(s):
    n = len(s)
    types_of_ch = [False for _ in range(n)]
    for i in range(n - 2, -1, -1):
        if (s[i] < s[i + 1] or
                (s[i] == s[i + 1] and types_of_ch[i + 1])):
            types_of_ch[i] = True
    return types_of_ch


def is_lms_char(index, type_map):
    if index == 0 or index == len(type_map):
        return False
    return type_map[index] and not type_map[index - 1]


def lms_substrings_are_equal(s, type_map, index_a, index_b):
    i = 0
    while True:
        a_is_lms = is_lms_char(i + index_a, type_map)
        b_is_lms = is_lms_char(i + index_b, type_map)
        if i > 0 and a_is_lms and b_is_lms:
            return True
        if (a_is_lms != b_is_lms or i + index_a >= len(type_map) or
                s[i + index_a] !=
                s[i + index_b]):
            return False
        i += 1


def find_bucket_sizes(string):
    tab = {}
    for i in range(len(string)):
        key = string[i]
        if key in tab:
            tab[key] += 1
        else:
            tab[key] = 1
    return tab


def find_bucket_heads(bucket_sizes):
    index = 0
    res = {}
    for key in sorted(bucket_sizes.keys()):
        res[key] = index
        index += bucket_sizes[key]
    return res


def find_bucket_tails(bucket_sizes):
    index = 0
    res = {}
    for key in sorted(bucket_sizes.keys()):
        index += bucket_sizes[key]
        res[key] = index - 1
    return res


def guess_lms_sort(string, bucket_sizes, type_map):
    n = len(string)
    guessed_suffix_array = [-1] * n
    bucket_tails = find_bucket_tails(bucket_sizes)
    for i in range(n):
        if is_lms_char(i, type_map):
            bucket_index = int_from_binary(string[i])
            guessed_suffix_array[bucket_tails[bucket_index]] = i
            bucket_tails[bucket_index] -= 1
    return guessed_suffix_array


def induce_sort_l(string, guessed_suffix_array, bucket_sizes, type_map):
    if string:
        bucket_heads = find_bucket_heads(bucket_sizes)
        n = len(string)
        j = n - 1
        bucket_index = int_from_binary(string[j])
        guessed_suffix_array[bucket_heads[bucket_index]] = j
        bucket_heads[bucket_index] += 1
        for i in range(n):
            if guessed_suffix_array[i] != -1:
                j = guessed_suffix_array[i] - 1
                if j >= 0 and not type_map[j]:
                    bucket_index = int_from_binary(string[j])
                    guessed_suffix_array[bucket_heads[bucket_index]] = j
                    bucket_heads[bucket_index] += 1
        return guessed_suffix_array
    return []


def induce_sort_s(string, guessed_suffix_array, bucket_sizes, type_map):
    if string:
        n = len(string)
        bucket_tails = find_bucket_tails(bucket_sizes)
        j = n - 1
        if type_map[j]:
            bucket_index = int_from_binary(string[j])
            guessed_suffix_array[bucket_tails[bucket_index]] = j
            bucket_tails[bucket_index] -= 1
        for i in range(n - 1, -1, -1):
            j = guessed_suffix_array[i] - 1
            if j >= 0 and type_map[j]:
                bucket_index = int_from_binary(string[j])
                guessed_suffix_array[bucket_tails[bucket_index]] = j
                bucket_tails[bucket_index] -= 1
        return guessed_suffix_array
    return []


def summarise_suffix_array(string, guessed_suffix_array, type_map):
    n = len(string)
    lms_names = [-1] * n
    current_name = 0
    last_lms_suffix_index = None
    for i in range(n):
        suffix_index = guessed_suffix_array[i]
        if is_lms_char(suffix_index, type_map):
            if not (last_lms_suffix_index is None or
                    lms_substrings_are_equal(string, type_map, last_lms_suffix_index, suffix_index)):
                current_name += 1
            last_lms_suffix_index = suffix_index
            lms_names[suffix_index] = current_name
    summary_suffix_indexes = []
    summary_string = []
    for index, name in enumerate(lms_names):
        if name != -1:
            summary_suffix_indexes.append(index)
            summary_string.append(name)
    summary_alfabet_size = current_name + 1
    return summary_string, summary_alfabet_size, summary_suffix_indexes


def make_summary_suffix_array(summary_string, summary_alfabet_size):
    n = len(summary_string)
    if len(summary_string) == 0 or len(summary_string) == summary_alfabet_size:
        summary_suffix_array = [-1] * n
        for x in range(n):
            y = summary_string[x]
            summary_suffix_array[y] = x
    else:
        summary_suffix_array = make_suffix_array_by_induced_sorting(
            summary_string)
    return summary_suffix_array


def accurate_lms_sort(string, bucket_sizes, summary_suffix_array, summary_suffix_indexes):
    suffix_indexes = [-1] * (len(string))
    summary_suffix_array = summary_suffix_array
    bucket_tails = find_bucket_tails(bucket_sizes)
    for i in range(len(summary_suffix_array) - 1, -1, -1):
        string_index = summary_suffix_indexes[summary_suffix_array[i]]
        bucket_index = int_from_binary(string[string_index])
        suffix_indexes[bucket_tails[bucket_index]] = string_index
        bucket_tails[bucket_index] -= 1
    return suffix_indexes
