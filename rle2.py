file_input = open("cipher.txt", "r", encoding="utf-8")
file_output = open("compressed_text.txt", "w", encoding="utf-8")
S = file_input.read()
print(S)
S = S + "$"
compressed_S = ""
#print(S)
prev_symb = S[0]
counter = 1
flag = False
start_i, end_i = 1, 1
sub_s = ""
for i in range(1, len(S)):
    if i % 100000 == 0:
        print(i)
    symb = S[i]
    if prev_symb == symb:
        if flag:
            compressed_S += chr(128 + i - start_i - 1) + sub_s
            sub_s = ""
            flag = False
        if counter == 127:
            compressed_S += chr(counter) + prev_symb
            counter = 0
        counter += 1

    else:
        if counter == 1:
            sub_s += prev_symb
            if not flag:
                start_i = i - 1
                flag = True
            elif i - start_i == 127:
                compressed_S += chr(128 + i - start_i) + sub_s
                flag = False
                sub_s = ""
        else:
            print(counter)
            compressed_S += chr(counter) + prev_symb
            counter = 1
    prev_symb = symb
if flag:
    compressed_S += chr(128 + len(S) - start_i - 1) + sub_s
file_output.write(compressed_S)
file_input.close()
file_output.close()
file_input = open("compressed_text.txt", "r", encoding="utf-8")
compressed_S = file_input.read()
N = len(compressed_S)
decompressed_S = ""
i = 0
print(ord(compressed_S[0]))
while i < N:
    if ord(compressed_S[i]) < 128:
        decompressed_S += ord(compressed_S[i]) * compressed_S[i + 1]
        i += 2
    else:
        decompressed_S += compressed_S[i + 1:i + 1 + ord(compressed_S[i]) - 128]
        i += ord(compressed_S[i]) - 128 + 1
print(decompressed_S)
for i in range(len(decompressed_S)):
    if S[i] != decompressed_S[i]:
        print(i)
print(decompressed_S == S[:-1])
file_input.close()
