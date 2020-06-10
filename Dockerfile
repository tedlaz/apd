FROM python:3.7-slim

copy requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt && \
    mkdir apd

COPY . /apd

RUN chmod +x /apd/start.sh

WORKDIR /apd

EXPOSE 8000

CMD ["/apd/start.sh"]
