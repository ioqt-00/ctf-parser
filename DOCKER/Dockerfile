#======================================================
# Setup
#======================================================

FROM debian



ENV DISCORD_TOKEN PUT-YOUR-TOKEN-HERE



ENV USER discordbot
ENV ROOTPWD root
ENV SHELL /bin/bash 
ENV DOCUMENT_ROOT /home/${USER}
ENV ZIPFILE discord.zip
ENV HTTP_PORT 80
ENV HTTPS_PORT 443
ENV SSH_PORT 22
ENV DEBIAN_FRONTEND noninteractive

#======================================================
# Dependencies
#======================================================



# Add User
RUN \
    useradd -m -s /bin/bash ${USER}; \
    echo "${USER}:${USER}" | chpasswd; \
    echo "root:${ROOTPWD}" | chpasswd; \
    echo "cd ${DOCUMENT_ROOT}" >> /root/.bashrc;

# Update + Requirements
RUN \
    apt-get -y -qq update; \
    apt-get install -y -qq build-essential ;

RUN \
    apt-get -y -qq install systemctl bash ffmpeg libsndfile1 pip tar file sox nano git unzip sudo wget curl zip gzip ssldump exiftool pngcheck binwalk rubygems ssh stegsnow sox tshark chaosreader strace ltrace checksec  binutils-multiarch;
# sagemath

#  Copy Bot  + Unzip 
COPY ${ZIPFILE} ${DOCUMENT_ROOT}/${ZIPFILE}
RUN unzip ${DOCUMENT_ROOT}/${ZIPFILE} -d /home/${USER}/.;


# Requirements Python
RUN \
    python3 -m pip install -r /home/${USER}/requirements.txt;

# Delete Discord.zip
RUN \
    rm ${DOCUMENT_ROOT}/${ZIPFILE};

# StegoPvd
RUN \
    wget https://gist.githubusercontent.com/dhondta/feaf4f5fb3ed8d1eb7515abe8cde4880/raw/stegopvd.py && chmod +x stegopvd.py && sudo mv stegopvd.py /usr/bin/stegopvd;\
    stegoveritas_install_deps;

# identify
# Useless
# RUN mv /home/${USER}/utils/analysis/tools/identify /usr/bin/identify && chmod +x  /usr/bin/identify ;

# # dtmf-decoder
RUN \
    git clone https://github.com/ribt/dtmf-decoder.git; \
    cd dtmf-decoder/; \
    sudo python3 -m pip install -r requirement.txt --upgrade; \
    chmod +x dtmf.py; \
    sudo cp dtmf.py /usr/local/bin/dtmf;

# jsteg
RUN \
    wget -O /usr/bin/jsteg https://github.com/lukechampine/jsteg/releases/download/v0.1.0/jsteg-linux-amd64; \
    chmod +x /usr/bin/jsteg; \
    wget -O /usr/bin/slink https://github.com/lukechampine/jsteg/releases/download/v0.2.0/slink-linux-amd64; \
    chmod +x /usr/bin/slink;

# stegseek
RUN \
    wget https://github.com/RickdeJager/stegseek/releases/download/v0.6/stegseek_0.6-1.deb; \
    apt install ./stegseek_0.6-1.deb; \
    rm stegseek_0.6-1.deb;

# OpenSll
RUN \
    wget http://www.openssl.org/source/openssl-1.0.1g.tar.gz; \
    tar -xvzf openssl-1.0.1g.tar.gz; \
    cd openssl-1.0.1g; \
    ./config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl; \
    make; \
    make install_sw; \
    rm openssl-1.0.1g.tar.gz;

# Radare2
RUN \
    git clone https://github.com/radareorg/radare2; \
    cd radare2 ; sys/install.sh;


# Rockyou
RUN \
   cd /tmp; \
   wget https://github.com/praetorian-inc/Hob0Rules/raw/master/wordlists/rockyou.txt.gz; \
   gzip -d rockyou.txt.gz;\
   mv rockyou.txt /home/${USER}/utils/wordlists/rockyou.txt;

# End
RUN \
    echo "Finish ! | Discord CTFD Bot Docker by Vozec from FlagPoisoning CTF team"


#======================================================
# Other
#======================================================

VOLUME ${DOCUMENT_ROOT}
WORKDIR ${DOCUMENT_ROOT}

EXPOSE ${HTTP_PORT}
EXPOSE ${HTTPS_PORT}
EXPOSE ${SSH_PORT}

ENTRYPOINT /bin/bash
CMD ["sleep", "infinity"]
