#! /bin/bash

AA_COMMIT="bf7ccd301d3f50bfcb4cc9e38ae187141ce35072"
SOURCE_DATE_EPOCH="315532800"

sudo buildctl build \
  --frontend dockerfile.v0 \
  --local dockerfile=. \
  --local context=. \
  --metadata-file metadata.json \
  --output type=oci,dest=./docker-aa.tar,name=docker-aa,push=false,rewrite-timestamp=true \
  --opt build-arg:SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH} AA_COMMIT=${AA_COMMIT}
