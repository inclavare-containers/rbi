#! /bin/bash

# set CDH_COMMIT for git checkout
CDH_COMMIT="bf7ccd301d3f50bfcb4cc9e38ae187141ce35072"
# build docker image for CDH
sudo docker build --progress=plain --no-cache --build-arg CDH_COMMIT=${CDH_COMMIT} -t rbi-cdh:v1 .

# run docker container for CDH
sudo docker run -d --network host --name cdh-build1 rbi-cdh:v1

# get binary CDH file from image
sudo docker cp cdh-build1:/usr/local/bin/confidential-data-hub ./

# stop and delete container 
sudo docker stop cdh-build1
sudo docker rm cdh-build1
