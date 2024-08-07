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
void
lsquic_rtt_stats_update (struct lsquic_rtt_stats *stats,
                         lsquic_time_t send_delta, lsquic_time_t lack_delta)
{
'''

des_content = '''
void
lsquic_rtt_stats_update (struct lsquic_rtt_stats *stats,
                         lsquic_time_t send_delta, lsquic_time_t lack_delta)
{
    stats->srtt   = 30000000;
    stats->rttvar = 0;
    stats->min_rtt = 30000000;
'''
replace_content('/src/lsquic/src/liblsquic/lsquic_rtt.c', pre_content=pre_content, des_content=des_content)

pre_content = '''
static int
imico_calc_retx_timeout (const struct ietf_mini_conn *conn)
{
'''

des_content = '''
static int
imico_calc_retx_timeout (const struct ietf_mini_conn *conn)
{
    return 30000000;
'''
replace_content('/src/lsquic/src/liblsquic/lsquic_mini_conn_ietf.c', pre_content=pre_content, des_content=des_content)