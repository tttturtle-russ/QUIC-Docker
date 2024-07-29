FROM alpine:latest
RUN apk add --no-cache cmake ninja gcc g++ git musl-dev linux-headers \
        openssl openssl-dev http-parser-dev libev-dev  bsd-compat-headers
RUN git config --global user.email "docker@example.com"
RUN git clone --recursive https://github.com/NTAP/quant.git /src
WORKDIR /src
RUN git checkout 29
WORKDIR /src/Debug
RUN cmake -GNinja -DNO_SANITIZERS=True -DNO_FUZZER_CORPUS_COLLECTION=True \
        -DCMAKE_INSTALL_PREFIX=/dst ..
RUN ninja install

FROM alpine:latest
COPY --from=0 /dst /
# COPY --from=0 /2048-master /www
COPY --from=0 /src/Debug/test/dummy.* /tls/
RUN apk add --no-cache openssl http-parser libev ethtool
EXPOSE 4433/UDP
EXPOSE 4434/UDP
CMD ["/bin/server", "-i", "eth0", "-d", "/www", \
        "-c", "/tls/dummy.crt", "-k", "/tls/dummy.key"]