import git
import docker
import argparse
from rich import print

client = docker.from_env()

def build_docker(path:str, tag: str):
    client.images.build(path=path, tag=tag, quiet=False)


def build(path: str):
    git.Repo.clone_from(url="https://github.com/private-octopus/picoquic.git", to_path=path)
    repo = git.Repo(path=path)
    for tag in repo.tags:
        repo.git.checkout(tag)
        for submodule in repo.submodules:
            submodule.update(init=True)
        build_docker(path, f"picoquic:{tag}")
    print(f"Build [green]{len(repo.tags)}[/green] images")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["build"], required=True)
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    if args.mode == "build": build(args.path)
    else: print(f"Unknown mode option: {args.mode}")