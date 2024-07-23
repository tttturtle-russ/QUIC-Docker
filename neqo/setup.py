import os   
import argparse
import subprocess
import docker
from rich import print

client = docker.from_env()

def list_all_tags_for_remote_git_repo(url):
    """
    Given a repository URL, list all tags for that repository
    without cloning it.

    This function use "git ls-remote", so the
    "git" command line program must be available.
    """
    # Run the 'git' command to fetch and list remote tags
    result = subprocess.run([
        "git", "ls-remote", "--tags", repo_url
    ], stdout=subprocess.PIPE, text=True)

    # Process the output to extract tag names
    output_lines = result.stdout.splitlines()
    tags = [
        line.split("refs/tags/")[-1] for line in output_lines
        if "refs/tags/" in line and "^{}" not in line
    ]

    return tags

repo_url = "https://github.com/mozilla/neqo.git"

template = """
FROM ubuntu:20.04

# RUN sed -i.bak 's|https\?://archive.ubuntu.com|https://mirrors.aliyun.com|g' /etc/apt/sources.list
RUN apt update && apt upgrade -y
RUN apt install -y git python3-dev curl build-essential mercurial python-dev ninja-build gyp libclang-dev
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y 
ENV PATH=$PATH:/root/.cargo/bin/
RUN git clone https://github.com/mozilla/neqo.git
WORKDIR /neqo
RUN git checkout {tag}
RUN git clone https://github.com/nss-dev/nss.git
RUN hg clone https://hg.mozilla.org/projects/nspr
WORKDIR /neqo/nss
ENV NSS_DIR=/neqo/nss
RUN ./build.sh
WORKDIR /neqo
ENV LD_LIBRARY_PATH=/neqo/dist/Debug/lib/
RUN cargo build

EXPOSE 12345
CMD [ "/neqo/target/debug/neqo-server", "[::]:12345" ]
"""

def generate():
    tags = list_all_tags_for_remote_git_repo(repo_url)
    for tag in tags:
        with open(f"./Dockerfile.{tag}", "w") as f:
            f.write(template.format(tag=tag))
    print(f"Generate [green]{len(tags)}[/green] Dockerfile for mozilla/neqo")

def build():
    cnt = 0
    for dockerfile in os.listdir(os.getcwd()):
        if not dockerfile.startswith("Dockerfile"):
            continue
        tag = f"neqo:{dockerfile.split(".")[1]}"
        client.images.build(dockerfile=dockerfile, tag=tag, quiet=False)
        cnt += 1
    print(f"Build [green]{cnt}[/green] images")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["generate", "build"], required=True)
    args = parser.parse_args()
    if args.mode == "generate": generate()
    else: build()
