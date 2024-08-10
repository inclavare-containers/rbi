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
    make # ATTESTER=all-attesters


FROM ubuntu:jammy-20240627.1

# The list of runtime argument with docker run -e NAME=VALUE
# Use the default KBC cc_kbc and local KBS with address http://127.0.0.1:8085
ARG AA_KBC_PARAMS=cc_kbc::http://127.0.0.1:8085
ARG RUST_LOG=debug

# Define the source of this AA image
LABEL org.opencontainers.image.source="https://github.com/inclavare-containers/attestation-agent"

# Install the SGX & TDX runtime dependencies
RUN apt-get update && apt-get install -y curl=7.81.0-1ubuntu1.17 gnupg=2.2.27-3ubuntu2.1 openssl=3.0.2-0ubuntu1.17 && \
    curl \
      -L https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | \
    tee intel-sgx-deb.key | apt-key add - && \
    echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' | \
    tee /etc/apt/sources.list.d/intel-sgx.list && \
    apt-get update && \
    apt-get install -y libtdx-attest-dev=1.21.100.3-focal1 libsgx-dcap-quote-verify=1.21.100.3-focal1 && \
    rm -rf /var/lib/apt/lists/{apt,dpkg,cache,log} /tmp/* /var/tmp/*

# Copy the TPM runtime dependencies
COPY --from=builder /usr/lib/x86_64-linux-gnu/libtss* /usr/lib/x86_64-linux-gnu

# Copy the attestation-agent binary
COPY --from=builder \
     /usr/src/guest-components/target/x86_64-unknown-linux-gnu/release/attestation-agent \
     /usr/local/bin/attestation-agent

# Set the environment parameters
ENV AA_KBC_PARAMS=${AA_KBC_PARAMS}
ENV RUST_LOG=${RUST_LOG}

EXPOSE 50002
