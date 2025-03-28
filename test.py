from bit_array import BitArray
from suffix_array import make_suffix_array
from suffix_array2 import make_suffix_array


f = open("Толстой Лев. Война и мир. Книга 1 - royallib.ru.txt", "rb")
s = f.read()[:2 * 10 ** 5]
f.close()
f = open("ru.txt", "wb")
f.write(s)
f.close()