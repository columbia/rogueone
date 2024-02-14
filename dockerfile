FROM ubuntu:22.04

USER root

ADD ./ /RO

RUN apt-get update -y
run DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y python3 python3-dev python3.10-venv nodejs npm libjemalloc-dev jq
#postgresql-14 postgresql-client-14 redis-server


RUN chmod -R +rwX /RO
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install wheel

WORKDIR /RO/fast
RUN ["bash", "install.sh"]

WORKDIR /RO

RUN rm -f ./db.json
RUN rm -f ./db2.json

RUN cp sample_db.json db.json
#RUN service redis-server start
#RUN service postgresql start
#RUN su postgres -c "createuser -w -d -r -s rogueone"
#RUN su postgres -c "createdb -O rogueone rogueone"