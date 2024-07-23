FROM ubuntu:20.04

# RUN sed -i.bak 's|https\?://archive.ubuntu.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt install -y git python3-dev curl build-essential mercurial python-dev ninja-build gyp libclang-dev
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y 
ENV PATH=$PATH:/root/.cargo/bin/
RUN git clone https://github.com/mozilla/neqo.git
WORKDIR /neqo
RUN git clone https://github.com/nss-dev/nss.git
RUN hg clone https://hg.mozilla.org/projects/nspr
WORKDIR /neqo/nss
ENV NSS_DIR=/neqo/nss
RUN ./build.sh
WORKDIR /neqo
ENV LD_LIBRARY_PATH=/neqo/dist/Debug/lib/
RUN cargo build

EXPOSE 12345
CMD [ "/neqo/target/debug/neqo-server", "[::]:12345" ]