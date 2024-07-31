import subprocess
import argparse
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置命令行参数解析
parser = argparse.ArgumentParser(description="Start multiple Docker containers for QUIC mapping.")
parser.add_argument("--folder_path", type=str, required=True, help="Path to the folder containing addresses.txt file.")
args = parser.parse_args()

def run_container(remote_addr):
    remote_container_name, remote_port = remote_addr
    container_name = f"mapper_{remote_container_name}"
    print(f"Starting {container_name} with remote address {remote_container_name}:{remote_port}...")
    
    # 定义日志文件路径
    host_log_path = os.path.abspath(f"./logs/{container_name}_info")
    container_log_path = "/tmp"  # 假设容器内部路径为/app
    container_logfile = "/tmp/info.txt"
    # 确保日志目录存在
    os.makedirs(os.path.dirname(host_log_path), exist_ok=True)

    # 运行容器并重定向输出到 info.txt
    subprocess.run([
        "docker", "run", "-d",
        "--name", container_name,
        "--network", network_name,
        "-v", f"{host_log_path}:{container_log_path}",
        image_name,
        "/bin/bash", "-c", f"python3 infer_server.py -L {container_name}:10000 -R {remote_container_name}:{remote_port} > {container_logfile} 2>&1"
    ])

    # 检查容器是否停止并获取退出代码
    result = subprocess.run(["docker", "wait", container_name], capture_output=True, text=True)
    exit_code = result.stdout.strip()

    # 定义目标文件夹
    target_folder = f"./log/{container_name}/"
    os.makedirs(target_folder, exist_ok=True)
    subprocess.run(["docker", "cp", f"{container_name}:{container_log_path}", target_folder])
    # 根据退出代码判断任务是否成功完成
    if exit_code == "0":
        print(f"Container {container_name} finished successfully. Files are in {host_log_path}")
    else:
        print(f"Container {container_name} finished unsuccessfully. Check logs in {host_log_path}/info.txt")


    # 清理容器
    # subprocess.run(["docker", "rm", container_name])

# 镜像名称和标签
image_name = "quic-mapper:latest"

# 确保或创建Docker网络
network_name = "quic"
# subprocess.run(["docker", "network", "create", network_name], check=True)

# 读取remoteaddr列表
address_file_path = os.path.join(args.folder_path, "addresses.txt")
with open(address_file_path, "r") as file:
    remote_addresses = file.readlines()

# 清理空白字符并拆分容器名和端口
remote_addresses = [addr.strip().split(':') for addr in remote_addresses if addr.strip()]

# 使用线程池并行启动容器
with ThreadPoolExecutor(max_workers=len(remote_addresses)) as executor:
    future_to_container = {executor.submit(run_container, addr): addr for addr in remote_addresses}

    # 等待所有容器任务完成
    for future in as_completed(future_to_container):
        addr = future_to_container[future]
        try:
            data = future.result()
        except Exception as exc:
            print(f"{addr} generated an exception: {exc}")
