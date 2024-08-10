#! /bin/bash

AA_COMMIT="bf7ccd301d3f50bfcb4cc9e38ae187141ce35072"

sudo docker build --progress=plain --no-cache --build-arg AA_COMMIT=${AA_COMMIT} -t rbi-aa:v1 .
sudo docker build --progress=plain --no-cache --build-arg AA_COMMIT=${AA_COMMIT} -t rbi-aa:v2 .

mkdir -m 755 -p pkg1
mkdir -m 755 -p pkg2

sudo docker run -d --network host --name aa-build1 rbi-aa:v1
sudo docker run -d --network host --name aa-build2 rbi-aa:v2

sudo docker cp aa-build1:/usr/local/bin/attestation-agent ./pkg1
sudo docker cp aa-build2:/usr/local/bin/attestation-agent ./pkg2

diffoscope ./pkg1/attestation-agent ./pkg2/attestation-agent --html diff.html

sudo docker stop aa-build1
sudo docker stop aa-build2

sudo docker rm aa-build1
sudo docker rm aa-build2
