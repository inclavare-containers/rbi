# Reproducible Build Attestation-service

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The attestation-service source code is located at [trustee/attestation-service at main · confidential-containers/trustee (github.com)](https://github.com/confidential-containers/trustee/tree/main/attestation-service). 

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

If  build process is successful, the binary attestation-service file ` grpc-as` and `restful-as` are in current directory. If you want to check the reproducibility, use `sha256sum` to get the hash value as `dc3aa9bd6b8e3c2886cd477069b9482f35d81a1909f59d4a0add1b607c0fa98a` for `grpc-as` and `3d0ebc55a098581f061fde404a15f40249d2d63e0d323743493c978bc5fdb462` for `restful-as`. For more information, please refer to

- [Restful CoCo AS](https://github.com/confidential-containers/trustee/blob/main/attestation-service/docs/restful-as.md#quick-start)
- [gRPC CoCo AS](https://github.com/confidential-containers/trustee/blob/main/attestation-service/docs/grpc-as.md#quick-start)

