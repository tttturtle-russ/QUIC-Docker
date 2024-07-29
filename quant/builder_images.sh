#!/bin/sh

# 定义分支列表
branches="27 28 29 32 33 main"

# 确保 Docker 网络存在
docker network create quic || true

# 清除旧的 addresses.txt 文件
echo "" > ../addresses.txt

# 遍历分支并构建 Docker 镜像，然后运行容器
for branch in $branches; do
    echo "Building Docker image for branch $branch..."
    docker build --build-arg BRANCH_NAME=$branch -t quic/quant:$branch .

    echo "Running Docker container for branch $branch..."
    docker run -d --name quant_$branch --network quic quic/quant:$branch

    # 将容器名:端口格式写入到文件中
    echo "quant_$branch:4433" >> addresses.txt
done
