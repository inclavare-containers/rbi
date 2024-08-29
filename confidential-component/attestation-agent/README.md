# Reproducible Build Attestation-agent

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The AA source code is located at [guest-components/attestation-agent at 917097b5dbd61078af037e5411f0760d47981640 · confidential-containers/guest-components (github.com)](https://github.com/confidential-containers/guest-components/tree/917097b5dbd61078af037e5411f0760d47981640/attestation-agent). The construction of Docker containers draws inspiration from the implementation in [inclavare-containers/docker-attestation-agent (github.com)](https://github.com/inclavare-containers/docker-attestation-agent).

## Files



- `run.sh` main script. Use `./run.sh` to run.
- `Dockerfile` to build docker.



## Prerequisites



- Ensure Docker is installed on your system
- Install libtss2-dev and libsgx-dcap-quote-verify



## Instructions

First, run the script to start.

```shell
sudo sh run.sh
```

If  build process is successful, the binary AA file ` attestation-agent` is in current directory. For help information, just run:

```shell
attestation-agent --help
```

Start AA and specify the endpoint of AA's gRPC service:

```shell
attestation-agent --attestation_sock 127.0.0.1:50002
```

Or start AA with default address (127.0.0.1:50002)

```shell
attestation-agent
```
