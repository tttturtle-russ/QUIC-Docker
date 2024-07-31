# 使用官方的 Python 镜像作为基础镜像
FROM python:3.9-slim

ARG BRANCH_NAME

# 设置工作目录
WORKDIR /app

# 安装系统依赖项，包括 OpenSSL 开发头文件和 Python 3 开发包
RUN apt-get update && apt-get install -y \
    libssl-dev \
    python3-dev \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 克隆特定的 aioquic 标签
RUN git clone --branch ${BRANCH_NAME} --depth 1 https://github.com/aiortc/aioquic.git /aioquic

# 复制你的应用程序代码到工作目录
COPY ./file .

RUN python modify_script.py

# 安装 aioquic 及其他依赖
RUN pip install --no-cache-dir /aioquic dnslib jinja2 starlette wsproto

# 暴露服务器的端口
EXPOSE 4433

# 运行 QUIC 服务器脚本
CMD ["python", "quic_server.py"]
