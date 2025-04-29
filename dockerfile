FROM alpine:3.21
WORKDIR /monitoring
COPY ./monitoring /monitoring

RUN apk update && apk add --no-cache \
    keepalived \
    python3 \
    py3-pip \
    iputils \
    openssl \
    tmux \
    nano \
    bash \
&& pip install requests pyotp flask ping3 discord watchdog --break-system-packages

RUN mkdir -p /etc/keepalived

#Fa partire lo script che esegue python in background 
COPY ./start.sh /start.sh 
RUN chmod +x /start.sh
# Fix potential line ending issues
RUN sed -i 's/\r$//' /start.sh

CMD ["/bin/bash", "/start.sh"]