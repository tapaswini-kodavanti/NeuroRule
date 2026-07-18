#
#       Base Image for Evolution
#
#       Sid Stuart 8/30/2020
#
FROM python:3.7-stretch

MAINTAINER Sid Stuart <sid.stuart@cognizant.com>

ENV PIP3_VERSION 20.2.3

RUN pip3 install --upgrade pip==${PIP3_VERSION} \
    && adduser --disabled-password --gecos '' leaf \
    && adduser leaf sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV APP_HOME /home/leaf
USER leaf
ENV VENV ${APP_HOME}/venv/
ENV PATH="$VENV/bin:$PATH"
RUN mkdir -p ${APP_HOME}
RUN python3 -m venv $VENV


COPY ./evolution/leaf-common ${APP_HOME}/leaf-common
COPY ./evolution/esp-sdk ${APP_HOME}/esp-sdk
COPY ./evolution ${APP_HOME}/evolution
RUN pip3 install ${APP_HOME}/leaf-common \ 
                 ${APP_HOME}/esp-sdk
RUN cd ${APP_HOME}/evolution && pip3 install -r requirements.txt
RUN cd ${APP_HOME}/evolution && pip3 install -r requirements-build.txt
