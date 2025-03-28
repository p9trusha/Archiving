from bwt import bwt, better_ibwt, bwt2
from rle_b import rle, i_rle
from time import time




n = 5
st_time = time()
m = 8
s_index = bwt("enwik7.txt", "bwt_text.txt", m)
rle("bwt_text.txt", "compressed_text.txt", m)
i_rle("compressed_text.txt", "decode_bwt.txt", m)
better_ibwt(s_index, "decode_bwt.txt", "decode_text.txt", m)
print(open("bwt_text.txt", "rb").read() == open("decode_bwt.txt", "rb").read())
print(open("enwik7.txt", "rb").read()[:10 ** n] == open("decode_text.txt", "rb").read()[:10 ** n])
print(time() - st_time)

