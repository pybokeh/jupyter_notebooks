# My first ever Dockerfile to create and launch a "minimal" jupyter notebook container
# Based on Docker's official online tutorial: https://docs.docker.com/get-started/part2/
# Created on 7/17/2019


# Use an official Python 3.7 runtime as a parent image from hub.docker.com
FROM python:3.7-buster

# Define a user other than root so that you can run the notebook server without root privileges
ARG NB_USER="pybokeh"
ARG NB_UID="1000"

ENV NB_USER=$NB_USER \
    NB_UID=$NB_UID


# Add user to group to allow it to execute bash commands
RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at the /app directory
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Per bottom of this jupyter documentation:
# https://jupyter-notebook.readthedocs.io/en/stable/public_server.html#running-a-public-notebook-server
ENV TINI_VERSION v0.6.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

# Make port 8888 available to the world outside this container
EXPOSE 8888

# Grant read/write access to the /app folder
RUN chmod -R a+rwx /app

# Container by default first runs as root user, but need to switch to a non-root user
# in order to run the jupyter notebook server without root privileges.  Otherwise, you
# will have to supply the --allow-root option to the jupyter notebook command
USER $NB_UID

# start jupyter notebook server
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser"]