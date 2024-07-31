import fileinput
import re
import sys

def replace_content(file_path):
    # 将文件内容读入内存
    with open(file_path, 'r') as file:
        content = file.read()

    # 定义替换模式
    pto_pattern = re.compile(
        r"pub fn pto\(&self, pn_space: PacketNumberSpace\) -> Duration \{\n"
        r"(\s+let mut t = self\.estimate\(\) \+ max\(4 \* self\.rttvar, GRANULARITY\);\n"
        r"\s+if pn_space == PacketNumberSpace::ApplicationData \{\n"
        r"\s+t \+= self\.ack_delay\.max\(\);\n"
        r"\s+\}\n"
        r"\s+t\n"
        r"\s+\})"
    )
    loss_delay_pattern = re.compile(
        r"pub fn loss_delay\(&self\) -> Duration \{\n"
        r"(\s+// kTimeThreshold = 9/8\n"
        r"\s+// loss_delay = kTimeThreshold \* max\(latest_rtt, smoothed_rtt\)\n"
        r"\s+// loss_delay = max\(loss_delay, kGranularity\)\n"
        r"\s+let rtt = max\(self\.latest_rtt, self\.smoothed_rtt\);\n"
        r"\s+max\(rtt \* 9 / 8, GRANULARITY\)\n"
        r"\s+\})"
    )

    # 进行替换
    content = pto_pattern.sub("pub fn pto(&self, pn_space: PacketNumberSpace) -> Duration {\n        return Duration::from_secs(10);\n    }", content)
    content = loss_delay_pattern.sub("pub fn loss_delay(&self) -> Duration {\n        return Duration::from_secs(5);\n    }", content)

    # 将修改后的内容写回文件
    with open(file_path, 'w') as file:
        file.write(content)

# 调用函数
replace_content('/neqo/neqo-transport/src/rtt.rs')
