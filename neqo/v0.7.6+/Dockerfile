# Stage 1: Build the executable
FROM ubuntu:18.04 AS builder

ARG BRANCH_NAME

# Install build dependencies
RUN apt update && apt upgrade -y && \
    apt-get install -y --no-install-recommends \
            ca-certificates coreutils curl git make mercurial ssh \
            build-essential clang llvm libclang-dev gyp ninja-build \
            pkg-config zlib1g-dev python3 && \
    rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y 
ENV PATH=$PATH:/root/.cargo/bin/

# Clone and build Neqo
RUN git clone --branch ${BRANCH_NAME} --depth 1 https://github.com/mozilla/neqo.git && \
    git clone https://github.com/nss-dev/nss.git  /neqo/nss && \
    hg clone https://hg.mozilla.org/projects/nspr /neqo/nspr
WORKDIR /neqo
COPY ./modify_script.py /neqo
RUN python3 /neqo/modify_script.py
WORKDIR /neqo/nss
ENV NSS_DIR=/neqo/nss
ENV NSPR_DIR=/neqo/nspr
ENV LD_LIBRARY_PATH=/neqo/dist/Debug/lib/
RUN ./build.sh --static -Ddisable_tests=1
WORKDIR /neqo
RUN cargo build -v --all-targets --tests --release && \
    strip /neqo/target/release/neqo-server

# Stage 2: Setup the runtime environment
FROM ubuntu:18.04
COPY --from=builder /neqo/target/release/neqo-server /usr/local/bin/
# COPY --from=builder /neqo/nss/dist/Debug/lib/*.so /usr/local/lib/
# COPY --from=builder /neqo/nspr/dist/Debug/lib/*.so /usr/local/lib/
COPY --from=builder /neqo/dist/Debug/lib/*.so /usr/local/lib/
COPY --from=builder /neqo/test-fixture/db /usr/local/bin/db

# Install only the runtime dependencies necessary
RUN apt update && apt install -y libclang1 libssl1.1 && \
    rm -rf /var/lib/apt/lists/* && \
    ldconfig
# Expose the necessary port
EXPOSE 4433/udp
WORKDIR /usr/local/bin
CMD ["neqo-server","--db","db","[::]:4433"]