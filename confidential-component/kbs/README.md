# Reproducible Build Key Broker Service

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The key broker service source code is located at [trustee/kbs at main · confidential-containers/trustee (github.com)](https://github.com/confidential-containers/trustee/tree/main/kbs). 

## Files



- `run.sh` main script. Use `./run.sh` to run.
- `Dockerfile` to build docker and get binary.



## Prerequisites



- Ensure Docker is installed on your system
- Install libtss2-dev and libsgx-dcap-quote-verify



## Instructions

First, run the script to start.

```shell
sudo sh run.sh
```

If  build process is successful, the binary attestation-service file ` kbs` is in current directory. If you want to check the reproducibility, use `sha256sum` to get the hash value as `1ddeb4c047378c7d780e244e684fef3f04db7a3d36a10ec8c53bfe131cc0ec30`. For more information, coco provides a [quick start](https://github.com/confidential-containers/trustee/blob/main/kbs/quickstart.md) guide to deploy KBS locally and conduct configuration and testing on Ubuntu 22.04.

