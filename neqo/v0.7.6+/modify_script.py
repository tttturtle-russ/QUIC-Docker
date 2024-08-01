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
# pre_content = '''
#     pub fn declare_lost(&mut self, now: Instant) -> bool {
#         if self.lost() {
#             false
#         } else {
#             self.time_declared_lost = Some(now);
#             true
#         }
#     }
# '''
# des_content = '''
#     pub fn declare_lost(&mut self, now: Instant) -> bool {
#         false
#     }
# '''

# 调用替换函数
# replace_content('/neqo/neqo-transport/src/recovery/sent.rs', pre_content, des_content)

# pre_content = '''
# pub fn pto(&mut self) -> bool {
#         if self.pto || self.lost() {
#             false
#         } else {
#             self.pto = true;
#             true
#         }
#     }
# '''
# des_content = '''
# pub fn pto(&mut self) -> bool {
#         false
#     }
# '''

# replace_content('/neqo/neqo-transport/src/recovery/sent.rs', pre_content, des_content)

pre_content = '''
    pub fn pto(&self, pn_space: PacketNumberSpace) -> Duration {
        let mut t = self.estimate() + max(4 * self.rttvar, GRANULARITY);
        if pn_space == PacketNumberSpace::ApplicationData {
            t += self.ack_delay.max();
        }
        t
    }
'''
des_content = '''
    pub fn pto(&self, _pn_space: PacketNumberSpace) -> Duration {
        Duration::from_secs(30)
    }
'''

replace_content('/neqo/neqo-transport/src/rtt.rs', pre_content, des_content)

pre_content = '''
    pub fn loss_delay(&self) -> Duration {
        // kTimeThreshold = 9/8
        // loss_delay = kTimeThreshold * max(latest_rtt, smoothed_rtt)
        // loss_delay = max(loss_delay, kGranularity)
        let rtt = max(self.latest_rtt, self.smoothed_rtt);
        max(rtt * 9 / 8, GRANULARITY)
    }
'''

des_content = '''
    pub fn loss_delay(&self) -> Duration {
        Duration::from_secs(30)
    }
'''

replace_content('/neqo/neqo-transport/src/rtt.rs', pre_content, des_content)