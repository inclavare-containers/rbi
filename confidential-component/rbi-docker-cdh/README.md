# Reproducible Build docker image of confidential-data-hub

This project is based on Docker for reproducible build, and currently supports running on Ubuntu 22.04 platform. The CDH source code is located at [guest-components/confidential-data-hub at 03fcb12c4cd8471e59e0ea4752e945ea46e7dc65 · confidential-containers/guest-components (github.com)](https://github.com/confidential-containers/guest-components/tree/03fcb12c4cd8471e59e0ea4752e945ea46e7dc65/confidential-data-hub). The construction of Docker containers draws inspiration from the implementation in [inclavare-containers/docker-confidential-data-hub (github.com)](https://github.com/inclavare-containers/docker-confidential-data-hub/tree/main?tab=readme-ov-file).

## Files



- `run.sh` main script. Use `./run.sh` to run.
- `Dockerfile` to build docker.



## Prerequisites



- Ensure Docker is installed on your system
- - Ensure that the buildkit is downloaded and configured locally, according to section **安装buildkit**  in [use nerdctl and buildkit](https://www.cnblogs.com/punchlinux/p/16575328.html#:~:text=nerdctl). The github link is https://github.com/moby/buildkit/releases, first download the package and copy to /usr/local/bin

```bash
root@master1:~# tar xf buildkit-v0.10.3.linux-amd64.tar.gz
root@master1:~# cp * /usr/local/bin/
```

  Create buildkit.socket in /lib/systemd/system/buildkit.socket and input the content below.

```bash
[Unit]
Description=BuildKit
Documention=https://github.com/moby/buildkit
 
[Socket]
ListenStream=%t/buildkit/buildkitd.sock
 
[Install]
WantedBy=sockets.target
```

​		Create buildkitd.service in /lib/systemd/system/buildkitd.service  and input the content below.

```bash
[Unit]
Description=BuildKit
Require=buildkit.socket
After=buildkit.socketDocumention=https://github.com/moby/buildkit
 
[Service]
ExecStart=/usr/local/bin/buildkitd --oci-worker=false --containerd-worker=true
 
[Install]
WantedBy=multi-user.target
```

 		configure buildkitd: create folder /etc/buildkit/ and file /etc/buildkit/buildkitd.toml, input the content below.

```bash
[registry."harbor.cncf.net"]
  http = true
  insecure = true
```

  start buildkitd service

```bash
root@master1:~# systemctl daemon-reload
root@master1:~# systemctl start buildkitd
root@master1:~# systemctl enable buildkitd
```





## Instructions

First, run the script to start.

```shell
sudo sh run.sh
```

If  build process is successful, the OCI file ` docker-cdh.tar` and `metadata.json` are in current directory, then bash `sudo docker load -i ./docker-cdh.tar` to run a container. To confirm the reproducibility, you can run `sha256sum docker-cdh.tar` and `sha256sum metadata.json `, and get the hash value `df518475d8be5e0021407c552f99c4348942dabe9a4dae549f69388635ff1dd5` for ` docker-cdh.tar`  and `843a5ae3ac0316b500ff7b78f94e65cddd6a5f1ab9f390f9a2119cb71dcf9c29` for `metadata.json`.
