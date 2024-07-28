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
static void __attribute__((nonnull))
update_rtt(struct q_conn * const c, uint_t ack_del)
{
    // see UpdateRtt() pseudo code
    if (unlikely(c->rec.cur.srtt == 0)) {
        c->rec.cur.min_rtt = c->rec.cur.srtt = c->rec.cur.latest_rtt;
        c->rec.cur.rttvar = c->rec.cur.latest_rtt / 2;
        return;
    }

    c->rec.cur.min_rtt = MIN(c->rec.cur.min_rtt, c->rec.cur.latest_rtt);
    ack_del = MIN(ack_del, c->tp_peer.max_ack_del) * NS_PER_MS;

    const uint_t adj_rtt = c->rec.cur.latest_rtt > c->rec.cur.min_rtt + ack_del
                               ? c->rec.cur.latest_rtt - ack_del
                               : c->rec.cur.latest_rtt;

    c->rec.cur.rttvar = 3 * c->rec.cur.rttvar / 4 +
                        (uint_t)
#if HAVE_64BIT
                                llabs
#else
                                labs
#endif
                            ((dint_t)c->rec.cur.srtt - (dint_t)adj_rtt) /
                            4;
    c->rec.cur.srtt = (7 * c->rec.cur.srtt / 8) + adj_rtt / 8;

#ifndef NO_QINFO
    const float latest_rtt = (float)c->rec.cur.latest_rtt / US_PER_S;
    c->i.min_rtt = MIN(c->i.min_rtt, latest_rtt);
    c->i.max_rtt = MAX(c->i.max_rtt, latest_rtt);
#endif
}
'''

des_content = '''
static void __attribute__((nonnull))
update_rtt(struct q_conn * const c, uint_t ack_del)
{
    // 将所有RTT相关的统计值设置为30秒（30,000,000微秒）
    uint_t fixed_rtt = 30000000;  // 30秒转换为微秒

    c->rec.cur.min_rtt = fixed_rtt;
    c->rec.cur.srtt = fixed_rtt;
    c->rec.cur.latest_rtt = fixed_rtt;
    c->rec.cur.rttvar = 0;  // 由于RTT被固定，其变异可以设为0

#ifndef NO_QINFO
    float fixed_rtt_sec = 30.0;  // 固定RTT值，以秒为单位
    c->i.min_rtt = fixed_rtt_sec;
    c->i.max_rtt = fixed_rtt_sec;
#endif

    // 忽略原有的RTT更新逻辑，直接返回
    return;
}
'''

replace_content('/src/lib/src/recovery.c', pre_content=pre_content, des_content=des_content)


pre_content='''
    const timeout_t dur =
        3 * (c->rec.cur.srtt == 0 ? c->rec.initial_rtt : c->rec.cur.srtt) *
            NS_PER_US +
        4 * c->rec.cur.rttvar * NS_PER_US;
'''

des_content='''
    const timeout_t dur = 30000000000; // 30 seconds in nanoseconds
'''

replace_content('/src/lib/src/conn.c', pre_content=pre_content, des_content=des_content)