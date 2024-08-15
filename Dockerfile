# Set Ubuntu and Python versions from pre-built images
FROM ubuntu:22.10
FROM python:3.10.12

# Install system dependencies
# Mininet installation instructions recommend python-is-python3 on Ubuntu to link python to python3
# Packages that will be used to run actions shall be installed at this step as well
RUN apt-get update && apt-get install -y \
    git \
    openjdk-17-jdk \
    python3-pip \
    python3-dev \
    python-is-python3 \
    iproute2 \
    nmap \ 
    bind9 \
    bind9utils \
    bind9-doc \
    dnsutils \
    openvswitch-switch \
    xterm \
    mininet \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# # Install Mininet
# RUN git clone https://github.com/mininet/mininet.git && \
#     cd mininet && \
#     util/install.sh -fnv && \
#     rm -rf /mininet/.git

# Set working directory
WORKDIR /cage

# Copy the current directory contents into the container at /cage
COPY . /cage

ENV PYTHON_EXE_FILEPATH="python3"

WORKDIR /cage/CybORG

# Install packages
RUN python3 -m pip install -e .

WORKDIR /cage/CybORG/CybORG/Mininet
# Run evaluation script
ENTRYPOINT ["python3", "main.py"]
