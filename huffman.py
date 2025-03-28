from collections import defaultdict
from heapq import heappush, heappop
from os import write
from queue import PriorityQueue

import numpy
import queue

from numpy.ma.core import left_shift

from bit_array import BitArray, int_from_binary


def prob_estimate(s, m):
    n = len(s)
    p = count_symbols(s, m)
    for key in p.keys():
        p[key] /= n
    return p

def count_symbols(s, m):
    n = len(s)
    if m % 8 == 0:
        step = m // 8
        p = defaultdict(int)
        for i in range(0, n, step):
            p[int.from_bytes(s[i:i + step])] += 1
        return p


def entropy(s, m):
    p = prob_estimate(s, m)
    h = 0
    for key in p.keys():
        h -= numpy.log2(p[key]) * p[key]
    return h


def mtf(s):
    t_mtf = [chr(i) for i in range(128)]
    l = []
    new_s = ""
    for c in s:
        i = t_mtf.index(c)
        l.append(i)
        new_s += chr(i)
        t_mtf = [t_mtf[i]] + t_mtf[:i] + t_mtf[i + 1:]
    return new_s


class Node():
    def __init__(self, symbol=None, counter=None, left=None, right=None, parent=None):
        self.symbol = symbol
        self.counter = counter
        self.left = left
        self.right = right
        self.parent = parent

    def __lt__(self, other):
        return self.counter < other.counter


def package_merge(counter_table, max_code_length):
    items = [(counter_table[key], [key]) for key in counter_table.keys()]
    items.sort()
    layer = items.copy()
    for i in range(1, max_code_length):
        layer2 = items.copy()
        j = 0
        while j + 1 < len(layer):
            combined_count = layer[j][0] + layer[j + 1][0]
            combined_symbols = layer[j][1] + layer[j + 1][1]
            layer2.append((combined_count, combined_symbols))
            j += 2
        layer2.sort()
        layer = layer2
    selected = []
    total_cost = 0
    for item in layer:
        if total_cost + 0.5 <= len(counter_table) - 1:
            selected.extend(item[1])
            total_cost += 0.5
    lengths = {}
    for key in sorted(counter_table.keys()):
        lengths[key] = selected.count(key)
    lengths = dict(sorted(lengths.items(), key=lambda item: item[1]))
    return lengths


def build_huffman_tree(counter_table):
    pq = PriorityQueue()
    for symbol, count in counter_table.items():
        pq.put(Node(symbol=symbol, counter=count))
    while pq.qsize() > 1:
        left = pq.get()
        right = pq.get()
        parent = Node(counter=left.counter + right.counter, left=left, right=right)
        pq.put(parent)
    return pq.get()


def build_codebook(root, code="", codebook=None):
    if codebook is None:
        codebook = {}
    if root.symbol is not None:
        codebook[root.symbol] = code
        return codebook
    build_codebook(root.left, code + "0", codebook)
    build_codebook(root.right, code + "1", codebook)
    return codebook


def huffman(name_input_file, name_output_file, m):
    input_file = open(name_input_file, "rb")
    s = input_file.read()
    input_file.close()
    len_symbol = m // 8 if m % 8 == 0 else m
    n = len(s)
    len_over = n % len_symbol
    n //= len_symbol
    over = s[:len_over]
    s = s[len_over:]
    counter_table = count_symbols(s, m)
    max_code_length = 255
    lengths = package_merge(counter_table, max_code_length)
    codebook = length_to_codes(lengths)
    coded_message = BitArray()
    output_file = open(name_output_file, "wb")
    output_file.write(len_over.to_bytes())
    output_file.write(over)
    output_file.write(len(codebook).to_bytes(length=len_symbol, byteorder="big"))
    for symbol in lengths.keys():
        output_file.write(symbol.to_bytes(length=len_symbol, byteorder="big"))
        output_file.write(lengths[symbol].to_bytes())
    for i in range(0, n, len_symbol):
        coded_message += codebook[int_from_binary(s[i:i + len_symbol])]
    bytes_string = coded_message.to_bytearray()
    output_file.write(bytes_string)
    output_file.close()


# Получение длин кодов Хаффмана
def codes_to_length(codes):
    symbol_lengths = {}
    for item in codes.items():
        symbol = item[0]
        symbol_lengths[symbol] = len(item[1])
    return symbol_lengths

# Преобразование длин кодов Хаффмана в канонические коды
def length_to_codes(symbol_lengths):
    codes = {}
    i = 0
    prev_code, prev_length = BitArray(), 0
    for symbol, length in symbol_lengths.items():
        if i == 0:
            code = BitArray()
            for i in range(length):
                code.append0()
        else:
            code = prev_code.copy().add1()
            for i in range(length - prev_length):
                code.append0()
        codes[symbol] = code
        prev_code = code
        prev_length = length
        i += 1
    return codes


def i_ha(compressed_file_name, decompressed_file_name, m):
    len_symbol = m
    if m % 8 == 0:
        len_symbol = m // 8
    compressed_file = open(compressed_file_name, "rb")
    s = compressed_file.read()
    len_over = s[0]
    over = s[1:len_over]
    len_codebook = int_from_binary(s[1 + len_over:1 + len_over + len_symbol])
    s_symbol_to_length = s[1 + len_over + len_symbol:
                           1 + len_over + len_symbol + len_codebook * (len_symbol + 1)]
    len_over_bits = s[1 + len_over + len_symbol + len_codebook * (len_symbol + 1)]
    s = BitArray(s[len_over + len_symbol + len_codebook * (len_symbol + 1) + 2:], "b")
    s = s[:len(s) - len_over_bits]
    compressed_file.close()
    decompressed_file = open(decompressed_file_name, "wb")
    decompressed_file.write(over)
    lengths = {}
    for i in range(len_codebook):
        lengths[
            int_from_binary(s_symbol_to_length[(len_symbol + 1) * i:(len_symbol + 1) * i + len_symbol])
        ] = s_symbol_to_length[(len_symbol + 1) * i + len_symbol]
    codebook = length_to_codes(lengths)
    i_codebook = {}
    for symbol, code in codebook.items():
        i_codebook[code] = symbol
    start = 0
    end = 0
    while end < len(s):
        code = BitArray(s[start:end], "bit_arr")
        if code in i_codebook.keys():
            decompressed_file.write(i_codebook[code].to_bytes(length=len_symbol, byteorder="big"))
            start = end
        end += 1
    decompressed_file.close()


huffman("enwik7.txt", "ha.txt", 16)
i_ha("ha.txt", "i_ha.txt", 16)
# arr = "aaaaaaa"
# # print(prob_estimate(arr))
# # print(entropy(arr))
# # print(mtf(arr).encode(encoding="ascii"))
# print(huffman_algorithm(arr))
