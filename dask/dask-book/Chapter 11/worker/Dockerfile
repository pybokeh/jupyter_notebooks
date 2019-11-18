FROM daskdev/dask

USER root

# Install dependencies
COPY requirements.txt build.sh worker-start.sh ./
RUN sh build.sh
RUN rm build.sh

CMD ["sh", "worker-start.sh"]
