# 第一阶段：构建环境
FROM debian:latest as builder

ARG BRANCH_NAME

# 安装所有需要的构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential \
    git cmake golang make autoconf automake libtool \
    libevent-dev net-tools python3 && \
    git config --global http.sslverify false && \
    git config --global https.sslverify false

# 克隆源码和构建
RUN git clone --branch ${BRANCH_NAME} --depth 1 https://github.com/alibaba/xquic.git /xquic
COPY ./build.sh /build.sh
COPY ./modify_script.py /modify_script.py
RUN chmod 777 /build.sh && \
    python3 /modify_script.py && \
    /build.sh

# 第二阶段：运行环境
FROM debian:stable-slim
# 安装运行时所需的基础依赖库
RUN apt-get update && \
    apt-get install -y --no-install-recommends libevent-2.1-7

# 从构建阶段复制 demo_server 及其依赖的库
COPY --from=builder /xquic/build/demo/demo_server /xquic_bin/demo_server
COPY --from=builder /lib/x86_64-linux-gnu/libevent-2.1.so.7 /lib/x86_64-linux-gnu/
COPY --from=builder /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/
COPY --from=builder /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/
COPY ./server.crt /xquic_bin/server.crt
COPY ./server.key /xquic_bin/server.key

WORKDIR /xquic_bin

# 设置环境变量以包含库路径，并使用 ldconfig 更新运行时链接器的配置
ENV LD_LIBRARY_PATH=/lib/x86_64-linux-gnu
# RUN ldconfig

# 清理并设置运行命令
# EXPOSE 8443
RUN apt-get -y purge net-tools && \
    apt-get -y autoremove --purge && \
    ldconfig && \
    rm -rf /var/lib/apt/lists/* /var/log/*

# CMD ["./demo_server", "-a", "0.0.0.0", "-p", "4433", "-l", "d"]
