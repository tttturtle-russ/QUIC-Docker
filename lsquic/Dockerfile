# 第一阶段：构建环境
FROM ubuntu:16.04 AS builder

ARG BRANCH_NAME

RUN apt-get update && \
    apt-get install -y build-essential git cmake software-properties-common \
                       zlib1g-dev libevent-dev

RUN add-apt-repository ppa:gophers/archive && \
    apt-get update && \
    apt-get install -y golang-1.9-go && \
    cp /usr/lib/go-1.9/bin/go* /usr/bin/.

WORKDIR /src

# 克隆lsquic
RUN mkdir /src/lsquic
RUN git clone -b ${BRANCH_NAME} --depth 1 https://github.com/litespeedtech/lsquic.git /src/lsquic && \
    cd /src/lsquic && \
    git submodule update --init

# 克隆并编译boringssl
RUN git clone https://boringssl.googlesource.com/boringssl && \
    cd boringssl && \
    git checkout a2278d4d2cabe73f6663e3299ea7808edfa306b9 && \
    cmake . && \
    make

# 编译lsquic
RUN cd /src/lsquic && \
    cmake -DBORINGSSL_DIR=/src/boringssl . && \
    make

# 第二阶段：生产环境
FROM ubuntu:16.04

# 复制所需文件
COPY --from=builder /src/lsquic/bin/http_server /lsquic_bin/
COPY --from=builder /lib/x86_64-linux-gnu/libpthread.so.0 /lib/x86_64-linux-gnu/
COPY --from=builder /lib/x86_64-linux-gnu/libm.so.6 /lib/x86_64-linux-gnu/
COPY --from=builder /lib/x86_64-linux-gnu/libc.so.6 /lib/x86_64-linux-gnu/
COPY --from=builder /lib64/ld-linux-x86-64.so.2 /lib64/

# 复制证书和密钥
COPY ./lsquic.crt /
COPY ./lsquic.key /

WORKDIR /lsquic_bin

CMD ["./http_server", "-c", "localhost.com,/lsquic.crt,/lsquic.key", "-L", "debug", "-s", "0.0.0.0:4433", "-Q", "h3"]
