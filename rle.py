file_input = open("enwik7.txt","r",encoding="utf-8")
file_output = open("compressed_text.txt","w",encoding="utf-8")
S = file_input.read()
S = S + "$"
compressed_S = ""
prev_symb = S[0]
counter = 1
flag = False
for symb in S[1:]:
    if prev_symb == symb:
        if flag == True: 
            compressed_S += "#"
            flag = False
        counter += 1

    else:
        if counter == 1:
            if flag == False:
                compressed_S += "#"
                flag = True
            compressed_S += prev_symb
        else:
            compressed_S += chr(counter) + prev_symb
            counter = 1
    prev_symb = symb
if flag == True:
    compressed_S += "#"
file_output.write(compressed_S)
file_input.close()
file_output.close()

file_input = open("compressed_text.txt","r",encoding="utf-8")
compressed_S = file_input.read()
N = len(compressed_S)
decompressed_S = ""
i = 0
while(i < N):
    if compressed_S[i] != "#":
        decompressed_S += ord(compressed_S[i]) * compressed_S [i+1]
        i += 2
    else: 
        i += 1
        while( i < N and compressed_S[i] != "#"):
            decompressed_S += compressed_S[i]
            i += 1
        i += 1
# print(decompressed_S)

print(decompressed_S==S[:-1])
file_input.close()
