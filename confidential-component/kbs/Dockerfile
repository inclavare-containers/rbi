FROM rust:1.80.0-bookworm as builder

WORKDIR /usr/src

# Install the build dependencies
RUN apt-get update && \
    apt-get install -y git=1:2.39.2-1.1 libtss2-dev=3.2.1-3 protobuf-compiler=3.21.12-3 clang=1:14.0-55.7~deb12u1 

# Install the SGX & TDX build dependencies
RUN curl \
      -L https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | \
    tee intel-sgx-deb.key | apt-key add - && \
    echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | \
    tee /etc/apt/sources.list.d/intel-sgx.list && \
    apt-get update && \
    apt-get install -y libsgx-dcap-quote-verify-dev=1.21.100.3-focal1

# Build the attestation-agent with all features
RUN git clone https://github.com/confidential-containers/trustee.git \
    && cd trustee/kbs \
    && make 
   
