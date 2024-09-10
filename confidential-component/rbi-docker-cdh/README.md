# Reproducible Build docker image of confidential-data-hub

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The CDH source code is located at [guest-components/confidential-data-hub at 03fcb12c4cd8471e59e0ea4752e945ea46e7dc65 · confidential-containers/guest-components (github.com)](https://github.com/confidential-containers/guest-components/tree/03fcb12c4cd8471e59e0ea4752e945ea46e7dc65/confidential-data-hub). The construction of Docker containers draws inspiration from the implementation in [inclavare-containers/docker-confidential-data-hub (github.com)](https://github.com/inclavare-containers/docker-confidential-data-hub/tree/main?tab=readme-ov-file).

## Files



- `run.sh` main script. Use `./run.sh` to run.
- `Dockerfile` to build docker.



## Prerequisites



- Ensure Docker is installed on your system
- Ensure that the buildkit is downloaded and configured locally, according to [use nerdctl and buildkit](https://www.cnblogs.com/punchlinux/p/16575328.html#:~:text=nerdctl).



## Instructions

First, run the script to start.

```shell
sudo sh run.sh
```

If  build process is successful, the OCI file ` docker-cdh.tar` and `metadata.json` are in current directory, then bash `sudo docker load -i ./docker-cdh.tar` to run a container. To confirm the reproducibility, you can run `sha256sum docker-cdh.tar` and `sha256sum metadata.json `, and get the hash value `df518475d8be5e0021407c552f99c4348942dabe9a4dae549f69388635ff1dd5` for ` docker-cdh.tar`  and `843a5ae3ac0316b500ff7b78f94e65cddd6a5f1ab9f390f9a2119cb71dcf9c29` for `metadata.json`.