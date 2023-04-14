#Install base image
FROM python:3-alpine3.15

# TYPE arg passed at build determines if server or client files are used
# BUILD CODE:
#   docker build -t samclutterbuck/<gust_server | gust_client>:<version> . --build-arg TYPE=<gust_server | gust_client>
ARG TYPE=gust_client
ENV GUST_FILE=$TYPE
ENV GUST_IP='127.0.0.1'

# set up file structire
WORKDIR /app
COPY $TYPE/ /app/$TYPE/
COPY gust_core/ /app/gust_core/
COPY $TYPE.py /app
COPY docs/ /app/docs/

# install relevent requirements
RUN pip install -r ./$TYPE/requirements.txt
RUN pip install -r ./gust_core/requirements.txt

# if server move the services python file to root app to be usable
RUN if [[ "$TYPE" == "gust_server" ]]; then cp /app/$GUST_FILE/services/gust_service.py /app/gust_service.py; cp /app/$GUST_FILE/services/gust_web_service.py /app/gust_web_service.py; fi

# Expose gust port and web gui port
EXPOSE 80
EXPOSE 11811

# if a server set host ip as server host ip (otherwise use passed ENV var)
# Start the default opening services if server 
# run infinite loop for access
CMD if [[ "$GUST_FILE" == "gust_server" ]]; then GUST_IP=$(hostname -i); fi; echo $GUST_IP > /app/gust_core/data/gust_ip; if [[ "$GUST_FILE" == "gust_server" ]]; then /app/$GUST_FILE/services/gust_service.service; /app/$GUST_FILE/services/gust_web_service.service;  fi; tail -f /dev/null