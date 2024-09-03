#! /bin/bash

# set CDH_COMMIT for git checkout
AA_COMMIT="bf7ccd301d3f50bfcb4cc9e38ae187141ce35072"
# build docker image for CDH
sudo docker build --progress=plain --no-cache --build-arg AA_COMMIT=${AA_COMMIT} -t rbi-kbs:v1 .

# run docker container for CDH
sudo docker run -d --network host --name kbs-build1 rbi-kbs:v1

# get binary CDH file from image
sudo docker cp kbs-build1:/usr/src/trustee/target/release/kbs ./

# stop and delete container 
sudo docker stop kbs-build1
sudo docker rm kbs-build1
