#---------------------------
#FROM rootproject/root-ubuntu16:6.12
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

# obsolete
RUN pip3 install --upgrade pip
RUN pip3 install pythondialog

#RUN ln -s /usr/lib/x86_64-linux-gnu/libgsl.so.19.0.0 /usr/lib/libgsl.so.0 && \
#  echo '/usr/local/bin/root -b $@' > /usr/local/sbin/root && chmod +x /usr/local/sbin/root &&\
#  git clone https://github.com/acidbourbon/mdc_3d_garfield.git
# RUN apt-get -y install \

RUN wget https://root.cern/download/root_v6.18.02.source.tar.gz && tar -zxvf root_v6.18.02.source.tar.gz && rm root_v6.18.02.source.tar.gz

RUN mkdir /root-build && cd /root-build; cmake -DPYTHON_EXECUTABLE=/usr/bin/python3 ../root-6.18.02
RUN cd /root-build; make -j6 

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
  wget
  
COPY --from=0 /root-build /root-build 

RUN pip3 install --upgrade pip
RUN pip3 install pythondialog

RUN ln -s /usr/lib/x86_64-linux-gnu/libgslcblas.so.0.0.0 /usr/lib/libgsl.so.0 

RUN apt-get update && \
  apt-get -y install \
  libgfortran3
  
RUN apt-get update && \
  apt-get -y install \
  wine-stable
  

#RUN dpkg --add-architecture i386 && apt-get update && apt-get -y install wine32

# this will create /LTspiceXVII with all the windows binaries and libraries you'll need
ADD ./build/LTspiceXVII.tgz /

ENV HOME=/workdir

#RUN chmod 777 -R /LTspiceXVII

RUN echo "#!/bin/bash\n. /root-build/bin/thisroot.sh" >entrypoint.sh ; chmod +x entrypoint.sh

#RUN echo "cd workdir \n ./view.sh gen_MDC_I_1750V_3x3x3.py" >> entrypoint.sh

RUN echo "cd /workdir/; /bin/bash" >> entrypoint.sh

ENTRYPOINT "/entrypoint.sh"
