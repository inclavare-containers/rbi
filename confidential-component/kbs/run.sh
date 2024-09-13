#! /bin/bash

# set COMMIT for git checkout
KBS_COMMIT="f6402d020248673482a4902d34c09a4fe109fe06"
# build docker image for CDH
sudo docker build --progress=plain --build-arg KBS_COMMIT=${KBS_COMMIT} -t rbi-kbs:v1 .

# run docker container for CDH
sudo docker run -d --network host --name kbs-build1 rbi-kbs:v1

# get binary CDH file from image
sudo docker cp kbs-build1:/usr/src/trustee/target/release/kbs ./

# stop and delete container 
sudo docker stop kbs-build1
sudo docker rm kbs-build1
