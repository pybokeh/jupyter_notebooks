FROM daskdev/dask-notebook
USER root
COPY requirements.txt build.sh ./
COPY start-notebook.sh /opt/app
RUN sh build.sh
RUN rm build.sh
EXPOSE 8888
CMD ["sh","/opt/app/start-notebook.sh"]
