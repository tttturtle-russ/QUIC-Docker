FROM ubuntu:18.04

# RUN sed -i.bak 's|https\?://archive.ubuntu.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt-get install -y --no-install-recommends \
            ca-certificates coreutils curl git make mercurial ssh \
            build-essential clang llvm libclang-dev gyp ninja-build \
            pkg-config zlib1g-dev
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y 
ENV PATH=$PATH:/root/.cargo/bin/
RUN git clone https://github.com/mozilla/neqo.git
WORKDIR /neqo
RUN git clone https://github.com/nss-dev/nss.git
RUN hg clone https://hg.mozilla.org/projects/nspr
WORKDIR /neqo/nss
ENV NSS_DIR=/neqo/nss
ENV NSPR_DIR=/neqo/nspr
ENV LD_LIBRARY_PATH=/neqo/dist/Debug/lib/
RUN ./build.sh --static -Ddisable_tests=1
WORKDIR /neqo
RUN cargo build -v --all-targets --tests --release

EXPOSE 4433
CMD [ "/neqo/target/release/neqo-server", "[::]:4433", "--db", "/neqo/test-fixture/db", "--qlog-dir","/qlog" ]
