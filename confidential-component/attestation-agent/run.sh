#! /bin/bash

# set CDH_COMMIT for git checkout
AA_COMMIT="bf7ccd301d3f50bfcb4cc9e38ae187141ce35072"
# build docker image for CDH
sudo docker build --progress=plain --no-cache --build-arg AA_COMMIT=${AA_COMMIT} -t rbi-aa:v1 .

# run docker container for CDH
sudo docker run -d --network host --name aa-build1 rbi-aa:v1

# get binary CDH file from image
sudo docker cp aa-build1:/usr/src/guest-components/target/x86_64-unknown-linux-gnu/release/attestation-agent ./

# stop and delete container 
sudo docker stop aa-build1
sudo docker rm aa-build1
