FROM python:3.6

WORKDIR /usr/src/app
RUN pip install caom2repo && pip install caom2utils && pip install vos

COPY ./docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]

