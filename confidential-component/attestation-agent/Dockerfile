FROM rust:1.80.0-bookworm as builder

# Define the default commit of source code
ARG AA_COMMIT=HEAD

WORKDIR /usr/src

# Install the build dependencies
RUN apt-get update && \
    apt-get install -y clang=1:14.0-55.7~deb12u1 libtss2-dev=3.2.1-3 protobuf-compiler=3.21.12-3 sudo=1.9.13p3-1+deb12u1

# Install the SGX & TDX build dependencies
RUN curl \
      -L https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | \
    tee intel-sgx-deb.key | apt-key add - && \
    echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | \
    tee /etc/apt/sources.list.d/intel-sgx.list && \
    apt-get update && \
    apt-get install -y libtdx-attest-dev=1.21.100.3-focal1 libsgx-dcap-quote-verify-dev=1.21.100.3-focal1

# Build the attestation-agent with all features
RUN git clone https://github.com/confidential-containers/guest-components \
      guest-components && \
    cd guest-components/attestation-agent && git checkout ${AA_COMMIT} && \
    make 
