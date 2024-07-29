import subprocess
import os
import time

# 镜像名称和标签
image_name = "quic-mapper:latest"

# 确保或创建Docker网络
network_name = "quic"
# subprocess.run(["docker", "network", "create", network_name], check=True)

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
    
    # 运行容器并等待其结束
    subprocess.run([
        "docker", "run",
        "--name", container_name,
        "--network", network_name,
        image_name,
        "python3", "infer_server.py",
        "-L", f"{container_name}:10000",
        "-R", f"{remote_container_name}:{remote_port}"
    ])

    # 检查容器是否停止并获取退出代码
    result = subprocess.run(["docker", "wait", container_name], capture_output=True, text=True)
    exit_code = result.stdout.strip()

    # 根据退出代码判断任务是否成功完成
    if exit_code == "0":
        print(f"Container {container_name} finished successfully. Starting to copy files...")
        # 定义容器内的文件夹和目标文件夹
        source_folder = f"/tmp/quic-infer/"
        target_folder = f"./output/quant/{container_name}/"
        
        # 从容器复制文件到外部
        subprocess.run(["docker", "cp", f"{container_name}:{source_folder}", target_folder])

        print(f"Files copied to {target_folder}")
    else:
        print(f"Container {container_name} exited with code {exit_code}")

    # 清理容器
    subprocess.run(["docker", "rm", container_name])

    # 等待一段时间，以免启动太多容器
    time.sleep(1)

