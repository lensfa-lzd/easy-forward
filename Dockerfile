FROM ubuntu:latest
LABEL authors="liang"

ENTRYPOINT ["top", "-b"]