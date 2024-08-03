import fileinput
import re
import sys

def replace_content(file_path, pre_content, des_content):
    # 将文件内容读入内存
    with open(file_path, 'r') as file:
        content = file.read()

    # 直接使用字符串替换
    content = content.replace(pre_content, des_content)
    
    # 将修改后的内容写回文件
    with open(file_path, 'w') as file:
        file.write(content)

# 精确的预内容字符串，包括所有必要的换行符和空格
pre_content = 'scheduleTimeout(callback, timeout);'

des_content = 'scheduleTimeout(callback, std::chrono::milliseconds(30000));'

replace_content('/build/mvfst/quic/api/QuicTransportBase.cpp', pre_content=pre_content, des_content=des_content)
