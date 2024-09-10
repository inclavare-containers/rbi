# Reproducible Build docker image of attestation-agent

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The AA source code is located at [guest-components/attestation-agent at 917097b5dbd61078af037e5411f0760d47981640 · confidential-containers/guest-components (github.com)](https://github.com/confidential-containers/guest-components/tree/917097b5dbd61078af037e5411f0760d47981640/attestation-agent). The construction of Docker containers draws inspiration from the implementation in [inclavare-containers/docker-attestation-agent (github.com)](https://github.com/inclavare-containers/docker-attestation-agent).

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

If  build process is successful, the OCI file ` docker-aa.tar` and `metadata.json` are in current directory, then bash `sudo docker load -i ./docker-aa.tar` to run a container. To confirm the reproducibility, you can run `sha256sum docker-aa.tar` and `sha256sum metadata.json `, and get the hash value `04c0abe7741f3d107407ca10609f94dd50181d86e9d37ca32ed91ca9819f1e93` for ` docker-aa.tar`  and `56f69650860876763baa0f7848b1dc8036eb37abe8a47af78b18ca932804dae2` for `metadata.json`.