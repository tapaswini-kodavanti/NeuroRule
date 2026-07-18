# VERSION 1.0.0
# AUTHOR: Darren Sargent
# DESCRIPTION: Docker file for ESP SDK.

FROM python:3.10-slim
ENV DEBIAN_FRONTEND noninteractive

# Debian basics
RUN apt-get update -y
RUN apt-get install git -y

# These values are passed into the build by Codefresh
# with defaults provided here.
ARG REPO=esp-sdk
ARG USERNAME=leaf
ARG APP_HOME=/home/leaf
ARG APP_SOURCE=/home/leaf/esp-sdk

ENV REPO=$REPO
ENV USERNAME=$USERNAME
ENV APP_HOME=$APP_HOME
ENV APP_SOURCE=$APP_SOURCE

ENV PYTHONPATH=$APP_HOME

# Create and use a non-root user
RUN  adduser --disabled-password --gecos '' ${USERNAME}

ENV SHELL=bash
ENV PIP3_VERSION 24.0
ENV EXTERNAL_BUILD_ROOT .

RUN pip3 install --upgrade pip==${PIP3_VERSION}

# Use the with_creds_requirements secret as the basis for the pip install
# of the main requirements.  We still do the COPY first so the container
# cache is properly broken on changes.
#
# NOTE: We expect the with_creds_requirement file to provide us with
#       ephemeral GitHub creds from vault as the proper replacement mechanism
#       for LEAF_SOURCE_CREDENTIALS.  This way, it's OK if these inherently
#       short-lived happen to be stored in the container.
COPY --chown=${USERNAME}:${USERNAME}  ${EXTERNAL_BUILD_ROOT}/requirements.txt ${APP_SOURCE}
RUN --mount=type=secret,id=with_creds_requirements \
    /bin/bash -c "pip3 install -r <(cat /run/secrets/with_creds_requirements)"

# Copy rest of source dir
COPY ./ ${APP_HOME}/

USER ${USERNAME}
WORKDIR ${APP_HOME}
