from file_manager import FileManager
import sys
import os

tmp = FileManager()

def parseCommand(command):
    tmp_array = command.split()
    return tmp_array

ans_list = tmp.createDirectory("JJJ")
# ans_list = parseCommand(ans)
# print(ans_list)


complete_file_dic = {}
complete_file_dic[ans_list[2]] = (ans_list[3], ans_list[0])


lt2 = tmp.generateLookupTable(complete_file_dic)
tmp.changeDirectory("JJJ", lt2)

print("encrypted current directory is: "+ os.getcwd())
print("full path: " + ans_list[1])
print("current encrypted directory is: " + ans_list[0])
print("decrypting directory..." + tmp.decryptDirectory(ans_list[0], ans_list[3]))
print("fake directory is: " + tmp.relative_path)



file_ans_list = tmp.createFile('1.txt')
# file_ans_list = parseCommand(file_ans)
print("file ans list is: ")
print(file_ans_list)

print("decrypted file contents: "+ tmp.DecryptFile(file_ans_list[0], file_ans_list[3]))
print("decrypted file name: " + tmp.DecryptFileName(file_ans_list[0], file_ans_list[3]))
# lookupTable = {}
complete_file_dic[file_ans_list[2]] = (file_ans_list[3], file_ans_list[0])
# print(lookupTable[file_ans_list[0]])
# print("lookupTable")
# print(lookupTable)
tmp.addFileContentsWrapper('1.txt', complete_file_dic, 'Im John')
print("display file contents: " + tmp.displayFileContents('1.txt',complete_file_dic))

# new_lookupTable = {}
# new_lookupTable[file_ans_list[1]] = file_ans_list[2]
buffer = tmp.listDir(complete_file_dic)
print("list operation: ")
for ele in buffer:
    print(ele)

new_list = tmp.renameFile_public("1.txt", complete_file_dic, "2.txt")
# complete_file_dic = new_list[4]
print("new complete_file_dic")
print(complete_file_dic)
# old_key = complete_file_dic["1.txt"][0]
# complete_file_dic[new_list[2]] = complete_file_dic.pop(new_list[3], (old_key, new_list[0]))
print("display file contents: " + tmp.displayFileContents("2.txt",complete_file_dic))

buffer = tmp.listDir(complete_file_dic)
print("list operation: ")
for ele in buffer:
    print(ele)

lt2 = tmp.generateLookupTable(complete_file_dic)
tmp.changeDirectory("../", lt2)

print("real directory is: " + tmp.current_path)

print("fake directory is: " + tmp.relative_path)

ans1, ans2 = tmp.generateIntegrityCode("/Users/jz/Desktop/ECE422/new/Secure-File-System/client/hash_test.txt")
print(ans1, ans2)

print(tmp.verifyIntegrityCode("/Users/jz/Desktop/ECE422/new/Secure-File-System/client/hash_test.txt", ans1, ans2))

# Jason needs 
# client sends relative path
# keep track current directory in file manager class
# filename encrypted, encrypted abosulte path include the file name