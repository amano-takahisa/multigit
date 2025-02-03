FROM python:latest

ARG USER_NAME=docker

# create a normal user
RUN useradd -ms /bin/bash $USER_NAME

ENV PATH="$PATH:/home/$USER_NAME/.local/bin"

USER $USER_NAME
WORKDIR /home/$USER_NAME
