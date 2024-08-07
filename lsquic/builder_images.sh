#!/bin/sh

# 获取所有大于等于 0.9.8 的标签
branches=$(git ls-remote --tags https://github.com/litespeedtech/lsquic.git | \
           grep -o 'refs/tags/v[0-9]\+\.[0-9]\+\.[0-9]\+$' | \
           sed 's|refs/tags/||' | \
           awk '$1 >= "v3.0.1" && $1 <= "v4.0.6"')

# 确保 Docker 网络存在
# docker network create quic || true

# 清除旧的 addresses.txt 文件
echo "" > addresses.txt

# 遍历分支并构建 Docker 镜像，然后运行容器
for branch in $branches; do
    echo "Building Docker image for branch $branch..."
    docker build --build-arg BRANCH_NAME=$branch -t lsquic:$branch .

    echo "Running Docker container for branch $branch..."
    docker run -d --name lsquic_$branch --network quic lsquic:$branch

    # 将容器名:端口格式写入到文件中
    echo "lsquic_$branch:4433" >> addresses.txt
done

cd ../
nohup python3 start_learn.py --folder_path lsquic & 