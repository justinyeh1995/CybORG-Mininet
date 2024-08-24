# Set Ubuntu and Python versions from pre-built images
FROM ubuntu:22.04
#FROM python:3.10.12

# Install system dependencies
# Mininet installation instructions recommend python-is-python3 on Ubuntu to link python to python3
# Packages that will be used to run actions shall be installed at this step as well
RUN apt update && apt install -y \
    sudo \
    curl \
    git \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    python3-dev \
    python-is-python3 \
    ifupdown \
    iproute2 \
    iptables \
    iputils-ping \
    nmap \
    net-tools \ 
    bind9 \
    bind9utils \
    bind9-doc \
    dnsutils \
    openvswitch-switch \
    openvswitch-testcontroller \
    tcpdump \
    xterm \
    mininet \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /cage

# Copy the current directory contents into the container at /cage
COPY . /cage

ENV PYTHON_EXE_FILEPATH="python3"

# Install packages
RUN pip3 install -e .

EXPOSE 8050

# Run evaluation script
ENTRYPOINT ["python3", "CybORG/Mininet/main.py"]
