FROM python:3.9-slim

# Create a project folder
RUN mkdir /dagster-sklearn

# Change working dirtory
WORKDIR /dagster-sklearn

ENV DAGSTER_HOME=/dagster-sklearn/.dagster

COPY  . /dagster-sklearn/

RUN pip install scikit-learn dagster dagit dagster_pandas

WORKDIR /dagster-sklearn/src 

# For debugging purposes
# RUN pwd
# RUN ls -la

# By default, dagit listens on port 3000, so we need to expose it
EXPOSE 3000

# Launch dagit, but we need to use workspace_docker.yaml
# instead of the default workspace.yaml since we are using the python
# executable from the container image, not the local Python executable
ENTRYPOINT ["dagit", "-w", "workspace_docker.yaml", "-h", "0.0.0.0", "-p", "3000"]