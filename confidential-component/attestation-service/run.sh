#! /bin/bash

# set COMMIT for git checkout
AS_COMMIT="f6402d020248673482a4902d34c09a4fe109fe06"

# build docker image for CDH
sudo docker build --progress=plain --build-arg AS_COMMIT=${AS_COMMIT} -t rbi-as:v1 .

# run docker container for CDH
sudo docker run -d --network host --name as-build1 rbi-as:v1

# get binary CDH file from image
sudo docker cp as-build1:/usr/src/trustee/target/release/grpc-as ./
sudo docker cp as-build1:/usr/src/trustee/target/release/restful-as ./

# stop and delete container 
sudo docker stop as-build1
sudo docker rm as-build1
