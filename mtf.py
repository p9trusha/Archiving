def mtf(input_file_name, encode_file_name):
    input_file = open(input_file_name, "rb")
    s = input_file.read()
    input_file.close()
    t = [i for i in range(256)]
    encode_file = open(encode_file_name, "wb")
    for i in range(len(s)):
        index = t.index(s[i])
        encode_file.write(index.to_bytes())
        t = [t[index]] + t[:index] + t[index+1:]
    encode_file.close()

# Обратное преобразование
def i_mtf(encode_file_name, decode_file_name):
    encode_file = open(encode_file_name, "rb")
    s = encode_file.read()
    encode_file.close()
    t = [i for i in range(256)]
    S_new = ""
    decode_file = open(decode_file_name, "wb")
    for i in range(len(s)):
        index = s[i]
        decode_file.write(t[index].to_bytes())
        t = [t[index]] + t[:index] + t[index + 1:]
    decode_file.close()


mtf("files/enwik7.txt", "files/mtf.txt")
i_mtf("files/mtf.txt", "files/i_mtf.txt")