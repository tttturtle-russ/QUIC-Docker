# 使用多阶段构建
# 首先使用 Ubuntu 作为构建基础镜像
FROM ubuntu:20.04 as builder

ARG BRANCH_NAME

ENV DEBIAN_FRONTEND=noninteractive

RUN echo 'tzdata tzdata/Areas select Europe' | debconf-set-selections \
 && echo 'tzdata tzdata/Zones/Europe select Berlin' | debconf-set-selections

# RUN sed -i.bak 's|https\?://archive.ubuntu.com|https://mirrors.hust.edu.cn|g' /etc/apt/sources.list
# 安装必要的包
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    g++-10 \
    cmake \
    libboost-all-dev \
    libevent-dev \
    libdouble-conversion-dev \
    libgoogle-glog-dev \
    libgflags-dev \
    libiberty-dev \
    liblz4-dev \
    liblzma-dev \
    libsnappy-dev \
    make \
    zlib1g-dev \
    binutils-dev \
    libjemalloc-dev \
    libssl-dev \
    pkg-config \
    libsodium-dev \
    python3 && \
    rm -rf /var/lib/apt/lists/*

ENV CXX=/usr/bin/g++-10
ENV CC=/usr/bin/gcc-10

WORKDIR /build
# RUN git config --global --get http.proxy
# RUN git config --global --get https.proxy

RUN git clone --branch ${BRANCH_NAME} --depth 1 https://github.com/facebookincubator/mvfst
COPY ./build_helper.sh /build/mvfst
COPY ./modify_script.py /build
RUN python3 modify_script.py
RUN chmod 777 /build/mvfst/build_helper.sh
WORKDIR /build/mvfst
RUN ./build_helper.sh

# 使用更小的基础镜像进行最终构建
FROM ubuntu:20.04
# 拷贝程序
COPY --from=builder /build/mvfst/_build/build/quic/samples/echo /app/echo

# 拷贝所需的动态库
# COPY --from=builder /lib/x86_64-linux-gnu/libgflags.so.2.2 \
#                     /lib/x86_64-linux-gnu/libboost_context.so.1.71.0 \
#                     /lib/x86_64-linux-gnu/libevent-2.1.so.7 \
#                     /lib/x86_64-linux-gnu/libz.so.1 \
#                     /lib/x86_64-linux-gnu/libsodium.so.23 \
#                     /lib/x86_64-linux-gnu/libdouble-conversion.so.3 \
#                     /lib/x86_64-linux-gnu/libglog.so.0 \
#                     /lib/x86_64-linux-gnu/libcrypto.so.1.1 \
#                     /lib/x86_64-linux-gnu/libzstd.so.1 \
#                     /lib/x86_64-linux-gnu/libdl.so.2 \
#                     /lib/x86_64-linux-gnu/libstdc++.so.6 \
#                     /lib/x86_64-linux-gnu/libm.so.6 \
#                     /lib/x86_64-linux-gnu/libgcc_s.so.1 \
#                     /lib/x86_64-linux-gnu/libc.so.6 \
#                     /lib/x86_64-linux-gnu/libunwind.so.8 \
#                     /lib/x86_64-linux-gnu/liblzma.so.5 \
#                     /lib/x86_64-linux-gnu/

COPY --from=builder /lib/x86_64-linux-gnu/ /lib/x86_64-linux-gnu/
# 设置环境变量
ENV LD_LIBRARY_PATH /lib/x86_64-linux-gnu

# 设置容器启动时执行的命令
CMD ["/app/echo","-host","0.0.0.0","-port","4433"]
