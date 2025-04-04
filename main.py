from math import ceil
from PIL import Image

import numpy as np

from bit_array import int_from_binary, BitArray
from bwt import bwt, better_i_bwt, bwt2
from ha import entropy, ha, i_ha, count_symbols, length_to_codes, package_merge
from lz import lzss, lzw, i_lzw
from mtf import mtf, i_mtf
from rle_b import rle, i_rle
from time import time


def png_to_raw(image_path, output_path):
    image = Image.open(image_path)
    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        # Удаляем альфа-канал
        image = image.convert('RGB')

    raw_pixels = np.array(image)
    raw_data = raw_pixels.tobytes()

    with open(output_path, 'wb') as f:
        f.write(raw_data)

def bwt_mtf(input_file_name, compressed_file_name, m):
    bwt_file_name = input_file_name[:-4] + "_bwt" + input_file_name[-4:]
    bwt(input_file_name, bwt_file_name, m)
    mtf(bwt_file_name, compressed_file_name, m)


def i_bwt_mtf(compressed_file_name, decompressed_file_name):
    i_mtf_file_name = compressed_file_name[:-4] + "_i_mtf" + compressed_file_name[-4:]
    i_mtf(compressed_file_name, i_mtf_file_name)
    better_i_bwt(i_mtf_file_name, decompressed_file_name)


def bwt_rle(input_file_name, compressed_file_name, m):
    bwt_file_name = input_file_name[:-4] + "_bwt" + input_file_name[-4:]
    bwt(input_file_name, bwt_file_name, m)
    rle(bwt_file_name, compressed_file_name, m)


def i_bwt_rle(compressed_file_name, decompressed_file_name):
    i_rle_file_name = compressed_file_name[:-4] + "_i_rle" + compressed_file_name[-4:]
    i_rle(compressed_file_name, i_rle_file_name)
    better_i_bwt(i_rle_file_name, decompressed_file_name)


def bwt_mtf_ha(input_file_name, compressed_file_name, m):
    bwt_mtf_file_name = input_file_name[:-4] + "_bwt_mtf" + input_file_name[-4:]
    bwt_mtf(input_file_name, bwt_mtf_file_name, m)
    ha(bwt_mtf_file_name, compressed_file_name, m)


def i_bwt_mtf_ha(compressed_file_name, decompressed_file_name):
    i_ha_file_name = compressed_file_name[:-4] + "_i_ha" + compressed_file_name[-4:]
    i_ha(compressed_file_name, i_ha_file_name)
    i_bwt_mtf(i_ha_file_name, decompressed_file_name)


def bwt_mtf_rle_ha(input_file_name, compressed_file_name, m):
    bwt_mtf_file_name = input_file_name[:-4] + "_bwt_mtf" + input_file_name[-4:]
    bwt_mtf(input_file_name, bwt_mtf_file_name, m)
    bwt_mtf_rle_file_name = bwt_mtf_file_name[:-4] + "_bwt_mtf" + bwt_mtf_file_name[-4:]
    rle(bwt_mtf_file_name, bwt_mtf_rle_file_name, m)
    ha(bwt_mtf_rle_file_name, compressed_file_name, m)


def i_bwt_mtf_rle_ha(compressed_file_name, decompressed_file_name):
    i_ha_file_name = compressed_file_name[:-4] + "_i_ha" + compressed_file_name[-4:]
    i_ha(compressed_file_name, i_ha_file_name)
    i_rle_ha_file_name = i_ha_file_name[:-4] + "_i_rle" + i_ha_file_name[-4:]
    i_rle(i_ha_file_name, i_rle_ha_file_name)
    i_bwt_mtf(i_rle_ha_file_name, decompressed_file_name)


def lzw_ha(input_file_name, compressed_file_name, max_size_dct_power):
    lzw_file_name = input_file_name[:-4] + "_lzw" + input_file_name[-4:]
    lzw(input_file_name, lzw_file_name, max_size_dct_power)
    lzw_file = open(lzw_file_name, "rb")
    m = lzw_file.read()[0]
    lzw_file.close()
    ha(lzw_file_name, compressed_file_name, m)


def i_lzw_ha(compressed_file_name, decompressed_file_name):
    i_ha_file_name = compressed_file_name[:-4] + "_i_ha" + compressed_file_name[-4:]
    i_ha(compressed_file_name, i_ha_file_name)
    i_lzw(i_ha_file_name, decompressed_file_name)


def lzss_ha(input_file_name, compressed_file_name, buffer_size_power=12):
    lzss_file_name = input_file_name[:-4] + "_lzw" + input_file_name[-4:]
    lzss(input_file_name, lzss_file_name, buffer_size_power)
    lzss_file = open(lzss_file_name, "rb")
    buffer_size_power = int_from_binary(lzss_file.read(1))
    string_size_power = int_from_binary(lzss_file.read(1))
    n_over_bits = int_from_binary(lzss_file.read(1))
    s = lzss_file.read()
    s = BitArray(s, 'b')[:len(s) * 8 - n_over_bits]
    first_bits = BitArray()
    symbols = bytearray()
    shifts = BitArray()
    lengths = BitArray()
    i = 0
    while i < len(s):
        if not s[i]:
            i += 1
            first_bits.append0()
            symbols += s[i:i + 8].to_bytearray(without_amount_of_extra_bits=True)
            i += 8
        else:
            i += 1
            first_bits.append1()
            shifts += s[i:i + buffer_size_power]
            i += buffer_size_power
            lengths += s[i:i + string_size_power]
            i += string_size_power
    symbols_counter_table = count_symbols(bytes(symbols), 1)
    symbols_lengths = package_merge(symbols_counter_table, 256)
    symbols_codebook = length_to_codes(symbols_lengths)
    shifts_counter_table = count_symbols(shifts, buffer_size_power)
    shifts_lengths = package_merge(shifts_counter_table, 256)
    shifts_codebook = length_to_codes(shifts_lengths)
    lengths_counter_table = count_symbols(lengths, string_size_power)
    lengths_lengths = package_merge(lengths_counter_table, 256)
    lengths_codebook = length_to_codes(lengths_lengths)
    compressed_file = open(compressed_file_name, "wb")
    compressed_file.write(buffer_size_power.to_bytes())
    compressed_file.write(string_size_power.to_bytes())
    compressed_file.write((len(symbols_codebook) - 1).to_bytes())
    for symbol in symbols_lengths.keys():
        compressed_file.write(symbol.to_bytes(length=1, byteorder="big"))
        compressed_file.write(symbols_lengths[symbol].to_bytes())
    coded_message = BitArray(len(shifts_codebook) - 1, "int", buffer_size_power)
    for symbol in shifts_lengths.keys():
        coded_message += BitArray(symbol, "int", length=buffer_size_power)
        coded_message += BitArray(shifts_lengths[symbol], "int", 8)
    coded_message += BitArray(len(lengths_codebook) - 1, "int", string_size_power)
    for symbol in lengths_lengths.keys():
        coded_message += BitArray(symbol, "int", length=string_size_power)
        coded_message += BitArray(lengths_lengths[symbol], "int", 8)
    i0 = i1 = 0
    for i in range(len(first_bits)):
        if first_bits[i]:
            coded_message.append1()
            coded_message += shifts_codebook[int_from_binary(shifts[i1 * buffer_size_power:
                                                                    (i1 + 1) * buffer_size_power])]
            coded_message += lengths_codebook[int_from_binary(lengths[i1 * string_size_power:
                                                                      (i1 + 1) * string_size_power])]
            i1 += 1
        else:
            coded_message.append0()
            coded_message += BitArray(symbols[i0], "int", 8)
            i0 += 1
    compressed_file.write(coded_message.to_bytearray())
    compressed_file.close()


def i_lzss_ha(compressed_file_name, decompressed_file_name):
    i_ha_file_name = compressed_file_name[:-4] + "_i_ha" + compressed_file_name[-4:]
    compressed_file = open(compressed_file_name, "rb")
    buffer_size_power = int_from_binary(compressed_file.read(1))
    string_size_power = int_from_binary(compressed_file.read(1))
    len_symbols_codebook = int_from_binary(compressed_file.read(1)) + 1
    symbols_symbol_to_length = compressed_file.read(len_symbols_codebook * 2)
    len_over_bits = int.from_bytes(compressed_file.read(1))
    s = BitArray(compressed_file.read(), "b")
    s = s[:len(s) - len_over_bits]
    i = 0
    len_shifts_codebook = int_from_binary(s[:buffer_size_power])
    i += buffer_size_power
    shifts_symbol_to_length = s[i:i + len_shifts_codebook * (buffer_size_power + 8)]
    i += len_shifts_codebook * (buffer_size_power + 8)
    len_lengths = s[i:i + len_shifts_codebook * (buffer_size_power + 8)]
    i_lzw(i_ha_file_name, decompressed_file_name)


if __name__ == "__main__":
    # bwt_mtf()
    # png_to_raw("files/image.png","files/image.raw")
    # png_to_raw("files/grey.png", "files/grey.raw")
    # png_to_raw("files/black.png", "files/black.raw")
    # "files/cipher.txt",
    files = ["files/cipher.txt", "files/enwik7.txt", "files/ru.txt", "files/bsdtar.exe",
             "files/image.raw", "files/grey.raw", "files/black.raw"]
    print(files)
    files = files
    m = 8
    for file in files:
        compressed_file_name = file[:-4] + "_lzss_ha" + file[-4:]
        lzss_ha(file, compressed_file_name)
        len1 = len(open(file, "rb").read())
        len2 = len(open(compressed_file_name, "rb").read())
        print(len2, round(len1 / len2, 3))
        # i_ha(compressed_file_name, file[:-4] + "_i_ha" + file[-4:])
        # print(open(file, "rb").read() == open(file[:-4] + "_i_ha" + file[-4:], "rb").read())
    # for i in range(1, 19):
    #     lzss("files/enwik7.txt", "files/lzss.txt", i)
    #     input_file = open("files/enwik7.txt", "rb")
    #     compressed_file = open("files/lzss.txt", "rb")
    #     print(i, 2 ** 17 / len(compressed_file.read()))
    #     input_file.close()
    #     compressed_file.close()
# n = 1
# st_time = time()
# m = 8
#
# bwt("files/enwik7.txt", "files/bwt.txt", m, block_size_power=1)
# better_i_bwt("files/bwt.txt", "files/i_bwt.txt")
# print(open("files/enwik7.txt", "rb").read()[:10 ** n] == open("files/i_bwt.txt", "rb").read()[:10 ** n])
# print(time() - st_time)

