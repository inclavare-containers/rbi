# Reproducible Build Confidential-data-hub

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The CDH source code is located at [guest-components/confidential-data-hub at 03fcb12c4cd8471e59e0ea4752e945ea46e7dc65 · confidential-containers/guest-components (github.com)](https://github.com/confidential-containers/guest-components/tree/03fcb12c4cd8471e59e0ea4752e945ea46e7dc65/confidential-data-hub). The construction of Docker containers draws inspiration from the implementation in [inclavare-containers/docker-confidential-data-hub (github.com)](https://github.com/inclavare-containers/docker-confidential-data-hub/tree/main?tab=readme-ov-file).

## Files



- `run.sh` main script. Use `./run.sh` to run.
- `Dockerfile` to build docker.



## Prerequisites



- Ensure Docker is installed on your system



## Instructions

First, run the script to start.

```shell
sudo sh run.sh
```

If  build process is successful, the binary CDH file ` confidential-data-hub` is in the current directory, then bash `./confidential-data-hub` to run it.
