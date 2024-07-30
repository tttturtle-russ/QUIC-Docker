# 使用基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/megakn1ght-docker/alpine:latest

# 定义构建时的分支变量
ARG BRANCH_NAME

# 安装所需的软件包
RUN apk add --no-cache \
        bsd-compat-headers \
        cmake \
        g++ \
        gcc \
        git \
        http-parser-dev \
        linux-headers \
        musl-dev \
        ninja \
        openssl \
        openssl-dev \
        python3

# 设置全局 Git 配置
RUN git config --global user.email "docker@example.com"

# 克隆 NTAP/quant 仓库并切换到指定分支
RUN git clone --recursive https://github.com/NTAP/quant.git /src && \
    git -C /src checkout ${BRANCH_NAME}

# 应用修改
COPY ./modify_script.py /src
# RUN python3 /src/modify_script.py

# 设置工作目录
WORKDIR /src/Debug

# 运行 CMake 和 Ninja 构建
RUN cmake -GNinja -DDOCKER=True -DCMAKE_INSTALL_PREFIX=/dst ..
RUN ninja install

# 设置默认命令以保持容器运行
# CMD ["tail", "-f", "/dev/null"]


# 创建新的基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/megakn1ght-docker/alpine:latest

# 从之前的构建阶段复制构建结果
COPY --from=0 /dst /
COPY --from=0 /src/Debug/test/dummy.* /tls/
COPY --from=0 /src/test/interop.sh /bin

# 安装运行所需的软件包
RUN apk add --no-cache openssl http-parser ethtool

# 设置默认命令以保持容器运行
CMD ["tail", "-f", "/dev/null"]

# 暴露端口（如果需要）
# EXPOSE 443/UDP
# EXPOSE 4433/UDP
# EXPOSE 4434/UDP

# 设置默认命令（如果需要）
CMD ["/bin/server", "-i", "eth0", "-d", "/tmp", \
        "-c", "/tls/dummy.crt", "-k", "/tls/dummy.key"]
