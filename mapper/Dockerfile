# 使用多阶段构建的第一阶段
FROM registry.cn-hangzhou.aliyuncs.com/megakn1ght-docker/ubuntu:20.04 AS builder

# 安装编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    build-essential \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
 && rm -rf /var/lib/apt/lists/*

# 克隆和准备项目
RUN git clone https://github.com/tttturtle-russ/QUIC-Mapper.git /mapper
WORKDIR /mapper
RUN git checkout refactor
RUN pip install --no-cache-dir -r requirements.txt

# 使用多阶段构建的第二阶段
FROM registry.cn-hangzhou.aliyuncs.com/megakn1ght-docker/ubuntu:20.04

# 复制必需的文件
COPY --from=builder /mapper /mapper

# 设置工作目录
WORKDIR /mapper

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
 && rm -rf /var/lib/apt/lists/* \
 && pip install --no-cache-dir -r requirements.txt
