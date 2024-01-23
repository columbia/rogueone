FROM ubuntu:22.04

USER root

ADD ./ /RO

RUN apt-get update -y
run DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y python3 python3.10-venv nodejs npm libjemalloc-dev jq
#postgresql-14 postgresql-client-14 redis-server


#RUN python3 -c "import sys;print(sys.prefix)"
RUN chmod -R +rwX /RO
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install wheel

WORKDIR /RO/fast
#RUN python3 -c "import sys;print(sys.prefix)"
RUN ["bash", "install.sh"]
#RUN [“echo” , “READY”]

WORKDIR /RO

RUN rm ./db.json
RUN rm ./db2.json

RUN cp sample_db.json db.json
#RUN service redis-server start
#RUN service postgresql start
#RUN su postgres -c "createuser -w -d -r -s rogueone"
#RUN su postgres -c "createdb -O rogueone rogueone"