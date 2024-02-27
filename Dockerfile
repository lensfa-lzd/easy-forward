# registry.cn-hongkong.aliyuncs.com/lensfa/easy-forward:latest
FROM ubuntu:22.04

WORKDIR /app

# 从构建阶段复制编译好的应用程序
COPY bin/ef /app/ef

# 暴露端口
EXPOSE 8888

RUN apt update \
	&& apt install build-essential libpcap-dev -y \
    && chmod +x ef

VOLUME /app/config
ENV TZ=Asia/Shanghai
CMD [ "/app/ef", "-c", "/app/config/config.yaml"]