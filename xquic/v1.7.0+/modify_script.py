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
xqc_send_ctl_set_loss_detection_timer(xqc_send_ctl_t *send_ctl)
{
'''

des_content = '''
xqc_send_ctl_set_loss_detection_timer(xqc_send_ctl_t *send_ctl)
{
    return;
'''

replace_content('/xquic/src/transport/xqc_send_ctl.c', pre_content=pre_content, des_content=des_content)

pre_content = '''
    hostname = SSL_get_servername(ssl, TLSEXT_NAMETYPE_host_name);
'''

des_content = '''
    hostname = "localhost";
'''

replace_content('/xquic/src/tls/xqc_tls.c', pre_content=pre_content, des_content=des_content)