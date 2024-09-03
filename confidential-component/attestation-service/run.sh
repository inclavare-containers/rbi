#! /bin/bash

# set CDH_COMMIT for git checkout
AA_COMMIT="bf7ccd301d3f50bfcb4cc9e38ae187141ce35072"
# build docker image for CDH
sudo docker build --progress=plain --no-cache -t rbi-as:v1 .

# run docker container for CDH
sudo docker run -d --network host --name as-build1 rbi-as:v1

# get binary CDH file from image
sudo docker cp as-build1:/usr/src/trustee/target/release/grpc-as ./
sudo docker cp as-build1:/usr/src/trustee/target/release/restful-as ./

# stop and delete container 
sudo docker stop as-build1
sudo docker rm as-build1
