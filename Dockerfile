FROM ubuntu:18.04

RUN mkdir -p /iFabric

WORKDIR /iFabric


RUN apt-get update
RUN apt-get install -y sudo 
RUN apt-get install -y python 
RUN apt-get install -y python3 
RUN apt-get install -y mininet 
RUN apt-get install -y git 
RUN apt-get install -y lsb-release

RUN adduser --disabled-password --gecos '' admin
RUN adduser admin sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

#bmv2

RUN git clone https://github.com/p4lang/behavioral-model.git || (cd behavioral-model ; git pull)
RUN cd behavioral-model && \
    bash ./install_deps.sh

RUN ldconfig
RUN cd behavioral-model && \
    bash ./autogen.sh
RUN cd behavioral-model && \
    bash ./configure

RUN cd behavioral-model && \
    make

RUN cd behavioral-model && \
    make install 

RUN cd behavioral-model && \
    make check

#p4 compiler dependencies
    
RUN apt-get install -y \
cmake \
g++ \
git \
automake \
libtool \
libgc-dev \
bison \
flex \
libfl-dev \
libgmp-dev \
libboost-dev \
libboost-iostreams-dev \
libboost-graph-dev \
llvm \ 
pkg-config \
python-scapy \
python-ipaddr \
python-ply \
python3-pip \
tcpdump

RUN pip3 install scapy ply

#protobuf dependencies

RUN apt-get install -y \
autoconf \
automake \
libtool \
curl \
g++ \
unzip

#protobuf

RUN git clone https://github.com/protocolbuffers/protobuf.git 

RUN cd protobuf && \
    git submodule update --init --recursive && \
    bash ./autogen.sh

RUN cd protobuf && \
    ./configure

RUN cd protobuf && \
    make

RUN cd protobuf && \
    make install

RUN cd protobuf && \
    ldconfig

#p4 compiler

RUN git clone --recursive https://github.com/p4lang/p4c.git 

RUN cd p4c && \
    mkdir build && \
    cd build && \
    cmake ..

RUN cd p4c/build && \
    make -j4 

RUN cd p4c/build && \
    make -j4 check || true

RUN cd p4c/build && \
    make install

#gRPC

RUN git clone https://github.com/google/grpc.git && \
cd grpc/ && \
git checkout tags/v1.17.2 && \
git submodule update --init --recursive

RUN cd grpc/ && \
    make

RUN cd grpc/ && \
    make install

RUN ldconfig

#PI
RUN apt-get install -y libjudy-dev

RUN git clone https://github.com/p4lang/PI && \
    cd PI/ && \
    git submodule update --init --recursive && \
    sh ./autogen.sh

RUN cd PI/ && \
    ./configure --with-proto --without-internal-rpc --without-cli --without-bmv2 && \ 
    make

RUN cd PI/ && \
    make check

RUN cd PI/ && \
    make install


#BMV2 for grpc

RUN cd behavioral-model/ && \
    sh ./autogen.sh

RUN cd behavioral-model/ && \
    ./configure --with-pi

RUN cd behavioral-model/ && \
    make 

RUN cd behavioral-model/ && \
    make install


#build simple_switch_grpc
RUN cd behavioral-model/targets/simple_switch_grpc && \
    sh ./autogen.sh

RUN cd behavioral-model/targets/simple_switch_grpc && \
    ./configure 

RUN cd behavioral-model/targets/simple_switch_grpc && \
    make 

RUN cd behavioral-model/targets/simple_switch_grpc && \
    make install

ENV LD_LIBRARY_PATH="/usr/local/lib"

RUN mkdir -p /home/mpodles/


RUN mkdir -p /home/mpodles/iFabric

WORKDIR /home/mpodles/iFabric

RUN apt-get install -y python-pip && \
    pip install jinja2\
    grpcio \
    psutil \
    rstr

RUN cd /iFabric/protobuf/python && \
    python setup.py build && \
    python setup.py test && \
    python setup.py install && \ 
    cp -R google/protobuf /usr/local/lib/python2.7/dist-packages/google

RUN apt-get install -y \
    iproute2 \
    iputils-ping \
    net-tools \
    vim \
    x11-xserver-utils \
    xterm 

COPY . .
EXPOSE 6379

ENTRYPOINT [ "/bin/bash" ]  