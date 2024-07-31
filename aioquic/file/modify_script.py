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
pre_content = '''
    def _detect_loss(self, space: QuicPacketSpace, now: float) -> None:'''

des_content = '''
    def _detect_loss(self, space: QuicPacketSpace, now: float) -> None:
        return'''

# 调用替换函数
replace_content('/aioquic/src/aioquic/quic/recovery.py', pre_content, des_content)

pre_content = '''
        # re-arm timer
'''

des_content = '''
        # re-arm timer
        return
'''

replace_content('/aioquic/src/aioquic/asyncio/protocol.py', pre_content, des_content)

pre_content = '''
    async def ping(self) -> None:
'''

des_content = '''
    async def ping(self) -> None:
        return
'''

replace_content('/aioquic/src/aioquic/asyncio/protocol.py', pre_content, des_content)