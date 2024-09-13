FROM rust:1.80.0-bookworm as builder

# The list of build argument with docker build --build-arg NAME=VALUE
# Define the default commit of source code
ARG CDH_COMMIT=HEAD

# Set the working directory inside the container
WORKDIR /usr/src/guest-components

# Clone the specific commit from the GitHub repository
RUN apt-get update && apt-get install -y git=1:2.39.2-1.1 \
    && git clone https://github.com/confidential-containers/guest-components.git . \
    && git checkout ${CDH_COMMIT}

# Install additional build dependencies
RUN apt-cache madison protobuf-compiler
RUN apt-get install -y protobuf-compiler=3.21.12-3

# Build and install confidential-data-hub with specific configurations
RUN cd confidential-data-hub && make 
