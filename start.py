import subprocess

# 镜像名称和标签
image_name = "quic_mapper"

# 确保或创建Docker网络
network_name = "quic"
subprocess.run(["docker", "network", "create", network_name], check=True)

# 读取remoteaddr列表
with open("addresses.txt", "r") as file:
    remote_addresses = file.readlines()

# 清理空白字符并拆分容器名和端口
remote_addresses = [addr.strip().split(':') for addr in remote_addresses if addr.strip()]

# 遍历地址列表并启动容器
for remote_addr in remote_addresses:
    remote_container_name, remote_port = remote_addr
    container_name = f"mapper_{remote_container_name}"
    print(f"Starting {container_name} with remote address {remote_container_name}:{remote_port}...")
    subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "--network", network_name,
        image_name,
        "python3", "infer_server.py",
        "-L", f"{container_name}:10000",  # 使用容器名作为本地名称
        "-R", f"{remote_container_name}:{remote_port}"
    ], check=True)
