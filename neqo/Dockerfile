# Stage 1: Build the executable
FROM ubuntu:18.04 AS builder

# Install build dependencies
RUN apt update && apt upgrade -y
RUN apt-get install -y --no-install-recommends \
            ca-certificates coreutils curl git make mercurial ssh \
            build-essential clang llvm libclang-dev gyp ninja-build \
            pkg-config zlib1g-dev python3

# Install Rust
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y 
ENV PATH=$PATH:/root/.cargo/bin/

# Clone and build Neqo
RUN git clone https://github.com/mozilla/neqo.git
WORKDIR /neqo
COPY ./modify_script.py /neqo
RUN python3 /neqo/modify_script.py
RUN git clone https://github.com/nss-dev/nss.git
RUN hg clone https://hg.mozilla.org/projects/nspr
WORKDIR /neqo/nss
ENV NSS_DIR=/neqo/nss
ENV NSPR_DIR=/neqo/nspr
ENV LD_LIBRARY_PATH=/neqo/dist/Debug/lib/
RUN ./build.sh --static -Ddisable_tests=1
WORKDIR /neqo
RUN cargo build -v --all-targets --tests --release

# Stage 2: Create a smaller runtime image
FROM ubuntu:18.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
            ca-certificates libclang1 zlib1g

# Copy the built executable and necessary files from the builder stage
COPY --from=builder /neqo/target/release/neqo-server /usr/local/bin/neqo-server
COPY --from=builder /neqo/test-fixture/db /neqo/test-fixture/db
COPY --from=builder /neqo/nss/dist/Debug/lib/* /usr/local/lib/

# Set environment variables
ENV LD_LIBRARY_PATH=/usr/local/lib

# Expose the necessary port
EXPOSE 4433/udp

# Specify the command to run the application
# CMD ["/usr/local/bin/neqo-server", "[::]:4433", "--db", "/neqo/test-fixture/db", "--qlog-dir","/qlog"]
