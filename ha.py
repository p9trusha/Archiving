from collections import defaultdict
from math import ceil
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
    step = m
    p = defaultdict(int)
    for i in range(0, n, step):
        p[int_from_binary(s[i:i + step])] += 1
    return p


def entropy(s, m):
    p = prob_estimate(s, m)
    h = 0
    for key in p.keys():
        h -= numpy.log2(p[key]) * p[key]
    return h


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
    if len(counter_table) <= 2:
        lengths = dict()
        for key in counter_table.keys():
            lengths[key] = 1
        return lengths
    else:
        max_code_length = max(max_code_length, len(counter_table) - 1)
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
            if layer == layer2[:(len(counter_table) - 1) * 2]:
                break
            layer = layer2[:(len(counter_table) - 1) * 2]
        lengths = defaultdict(int)
        for i in range((len(counter_table) - 1) * 2):
            for key in layer[i][1]:
                lengths[key] += 1
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


def ha(name_input_file, name_output_file, m):
    input_file = open(name_input_file, "rb")
    s = input_file.read()
    input_file.close()
    if m % 8 == 0:
        len_symbol = m // 8
    else:
        len_symbol = m
        s = BitArray(s, "b")
    len_over = len(s) % len_symbol
    over = s[:len_over]
    s = s[len_over:]
    n = len(s) // len_symbol
    counter_table = count_symbols(s, len_symbol)
    max_code_length = 255
    lengths = package_merge(counter_table, max_code_length)
    codebook = length_to_codes(lengths)
    coded_message = BitArray()
    output_file = open(name_output_file, "wb")
    output_file.write(m.to_bytes())
    output_file.write(len_over.to_bytes())
    if m % 8 == 0:
        output_file.write(over)
        output_file.write((len(codebook) - 1).to_bytes(length=len_symbol, byteorder="big"))
    else:
        output_file.write(over.to_bytearray())
        coded_message = BitArray(len(codebook) - 1, "int", len_symbol)
    for symbol in lengths.keys():
        if m % 8 == 0:
            output_file.write(symbol.to_bytes(length=len_symbol, byteorder="big"))
            output_file.write(lengths[symbol].to_bytes())
        else:
            coded_message += BitArray(symbol, "int", length=len_symbol)
            coded_message += BitArray(lengths[symbol], "int", 8)
    for i in range(0, n):
        coded_message += codebook[int_from_binary(s[i * len_symbol:(i + 1) * len_symbol])]
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


def i_ha(compressed_file_name, decompressed_file_name):
    compressed_file = open(compressed_file_name, "rb")
    m = int_from_binary(compressed_file.read(1))
    len_symbol = m
    if m % 8 == 0:
        len_symbol = m // 8
    len_over = int.from_bytes(compressed_file.read(1))
    if m % 8 == 0:
        over = compressed_file.read(len_over)
    else:
        over = compressed_file.read(1 + ceil(len_over / 8))
        over = BitArray(over, 'b')[len(over) * 8 - len_over:]
    if m % 8 == 0:
        len_codebook = int_from_binary(compressed_file.read(len_symbol)) + 1
        s_symbol_to_length = compressed_file.read(len_codebook * (len_symbol + 1))
        len_over_bits = int.from_bytes(compressed_file.read(1))
        s = BitArray(compressed_file.read(), "b")
        s = s[:len(s) - len_over_bits]
    else:
        s = BitArray(compressed_file.read(), "b")
        len_over_bits, s = int_from_binary(s[:8]), s[8:]
        len_codebook, s = int_from_binary(s[:len_symbol]) + 1, s[len_symbol:]
        s_symbol_to_length = s[:len_codebook * (len_symbol + 8)]
        s = s[len_codebook * (len_symbol + 8):]
        s = s[:len(s) - len_over_bits]
    compressed_file.close()
    decompressed_file = open(decompressed_file_name, "wb")
    if m % 8 == 0:
        decompressed_s = bytearray()
    else:
        decompressed_s = BitArray()
    decompressed_s += over
    lengths = {}
    for i in range(len_codebook):
        if m % 8 == 0:
            lengths[
                int_from_binary(s_symbol_to_length[(len_symbol + 1) * i:
                                                   (len_symbol + 1) * i + len_symbol])
            ] = s_symbol_to_length[(len_symbol + 1) * i + len_symbol]
        else:
            lengths[
                int_from_binary(s_symbol_to_length[(len_symbol + 8) * i:
                                                   (len_symbol + 8) * i + len_symbol])
            ] = int_from_binary(s_symbol_to_length[(len_symbol + 8) * i + len_symbol:
                                                   (len_symbol + 8) * i + len_symbol + 8])
    codebook = length_to_codes(lengths)
    i_codebook = {}
    for symbol, code in codebook.items():
        i_codebook[code] = symbol
    start = 0
    end = 0
    while end <= len(s):
        code = BitArray(s[start:end], "bit_arr")
        if code in i_codebook.keys():
            if m % 8 == 0:
                decompressed_s += i_codebook[code].to_bytes(length=len_symbol, byteorder="big")
            else:
                decompressed_s += BitArray(i_codebook[code], "int", len_symbol)
            start = end
        end += 1
    if m % 8 != 0:
        decompressed_s = decompressed_s.to_bytearray(without_amount_of_extra_bits=True)
    decompressed_file.write(decompressed_s)
    decompressed_file.close()
