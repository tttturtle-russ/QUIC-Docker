# 使用 Ubuntu 作为构建基础镜像
FROM ubuntu:20.04 as builder

# Avoid interactive dialogues by setting this environment variable
ENV DEBIAN_FRONTEND=noninteractive

RUN echo 'tzdata tzdata/Areas select Europe' | debconf-set-selections \
 && echo 'tzdata tzdata/Zones/Europe select Berlin' | debconf-set-selections

# 更新软件包列表和安装构建依赖
RUN apt update && apt upgrade -y --fix-missing
RUN apt install -y        \
    git \
    g++-10                      \
    cmake                    \
    libboost-all-dev         \
    libevent-dev             \
    libdouble-conversion-dev \
    libgoogle-glog-dev       \
    libgflags-dev            \
    libiberty-dev            \
    liblz4-dev               \
    liblzma-dev              \
    libsnappy-dev            \
    make                     \
    zlib1g-dev               \
    binutils-dev             \
    libjemalloc-dev          \
    libssl-dev               \
    pkg-config               \
    libsodium-dev

RUN git config --global user.email "docker@example.com"

ENV CXX=/usr/bin/g++-10
ENV CC=/usr/bin/gcc-10


# 克隆 mvfst 仓库
WORKDIR /build
RUN git clone https://github.com/facebookincubator/mvfst

COPY ./build_helper.sh /build/mvfst

RUN chmod 777 /build/mvfst/build_helper.sh
# 进入 mvfst 目录
WORKDIR /build/mvfst

# 使用 getdeps.py 安装系统依赖
# RUN ./build/fbcode_builder/getdeps.py install-system-deps --recursive --install-prefix=$(pwd)/_build mvfst

# 构建 mvfst
RUN ./build_helper.sh

# 设置容器启动时执行的命令
# CMD ["<mvfst-executable-name>"]
