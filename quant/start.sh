#!/bin/bash

# 设置镜像名称和标签
IMAGE_NAME="ntap/quant:latest"

# 构建 Docker 镜像
echo "Building Docker image..."
sudo docker build -t $IMAGE_NAME .

# 检查是否成功构建
if [ $? -ne 0 ]; then
  echo "Error: Docker image build failed!"
  exit 1
fi

# 运行 Docker 容器
CONTAINER_NAME="quant-container"
sudo docker run -d --name $CONTAINER_NAME $IMAGE_NAME

# 检查是否成功启动容器
if [ $? -ne 0 ]; then
  echo "Error: Failed to start Docker container!"
  exit 1
fi

# 检查 server.crt 文件是否存在
if [ ! -f server.crt ]; then
  echo "Error: server.crt file not found!"
  exit 1
fi

# 检查 server.key 文件是否存在
if [ ! -f server.key ]; then
  echo "Error: server.key file not found!"
  exit 1
fi

# 复制证书文件到容器
echo "Copying server.crt to container $CONTAINER_NAME:/tls/"
sudo docker cp server.crt $CONTAINER_NAME:/tls/

echo "Copying server.key to container $CONTAINER_NAME:/tls/"
sudo docker cp server.key $CONTAINER_NAME:/tls/

# 确认文件已成功复制
echo "Verifying files in the container..."
sudo docker exec -it $CONTAINER_NAME ls /tls/

echo "Done."
sudo docker exec -it $CONTAINER_NAME /bin/sh
