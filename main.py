from math import ceil

from bwt import bwt, better_i_bwt, bwt2
from ha import entropy
from lz import lzss
from mtf import mtf
from rle_b import rle, i_rle
from time import time


def bwt_mtf():
    for i in range(7):
        bwt("files/enwik7.txt", "files/bwt.txt", 8, block_size_power=i)
        mtf("files/bwt.txt", "files/bwt+mtf.txt")
        file = open("files/bwt+mtf.txt", "rb")
        print(entropy(file.read(), 8))
        file.close()



if __name__ == "__main__":
    # bwt_mtf()
    for i in range(1, 19):
        lzss("files/enwik7.txt", "files/lzss.txt", i)
        input_file = open("files/enwik7.txt", "rb")
        compressed_file = open("files/lzss.txt", "rb")
        print(i, 2 ** 17 / len(compressed_file.read()))
        input_file.close()
        compressed_file.close()
# n = 1
# st_time = time()
# m = 8
#
# bwt("files/enwik7.txt", "files/bwt.txt", m, block_size_power=1)
# better_i_bwt("files/bwt.txt", "files/i_bwt.txt")
# print(open("files/enwik7.txt", "rb").read()[:10 ** n] == open("files/i_bwt.txt", "rb").read()[:10 ** n])
# print(time() - st_time)

