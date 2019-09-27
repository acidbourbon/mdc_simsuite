#---------------------------

##################################################
##    intermediate stage to build CERN ROOT     ##
##################################################


FROM ubuntu:18.04

USER root

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get -y install \
  vim \
  nano \
  libgslcblas0 \
  python3-numpy \
  python3-scipy \
  python3-matplotlib \
  perl \
  bc \
  git \
  liblapack3 \
  libboost-all-dev \
  gv ghostscript xterm x11-utils \
  dialog \
  python3-pip \
  wget \
  git dpkg-dev cmake g++ gcc binutils libx11-dev libxpm-dev \
  libxft-dev libxext-dev

RUN wget https://root.cern/download/root_v6.18.02.source.tar.gz && tar -zxvf root_v6.18.02.source.tar.gz && rm root_v6.18.02.source.tar.gz

# arguments for cmake to use python3 for pyROOT
RUN mkdir /root-build && cd /root-build; cmake -DPYTHON_EXECUTABLE=/usr/bin/python3 ../root-6.18.02

# making with too many threads at once makes my notebook swap :/
#RUN cd /root-build; make -j6
RUN cd /root-build; make -j2
  
  


##################################################
##        build actual working container        ##
##################################################

# leave some 500 MB of root source files behind

FROM ubuntu:18.04

USER root

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
  apt-get -y install \
  vim \
  nano \
  libgslcblas0 \
  python3-numpy \
  python3-scipy \
  python3-matplotlib \
  perl \
  bc \
  git \
  liblapack3 \
  libboost-all-dev \
  gv ghostscript xterm x11-utils \
  dialog \
  python3-pip \
  wget \
  libgfortran3 \
  wine-stable \
  iputils-ping \
  curl

RUN pip3 install --upgrade pip && \
  pip3 install setuptools && \
  pip3 install pythondialog python-vxi11

COPY --from=0 /root-build /root-build 

# for garfield to feel at home make symlink to som gsl libs
RUN ln -s /usr/lib/x86_64-linux-gnu/libgslcblas.so.0.0.0 /usr/lib/libgsl.so.0 

# this will create /LTspiceXVII with all the 
# windows binaries and libraries you'll need
ADD ./build/LTspiceXVII.tgz /

ENV HOME=/workdir

RUN echo "#!/bin/bash\n. /root-build/bin/thisroot.sh" >entrypoint.sh ; chmod +x entrypoint.sh

RUN echo "cd /workdir/; /bin/bash" >> entrypoint.sh

ENTRYPOINT "/entrypoint.sh"
