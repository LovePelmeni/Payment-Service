ARG arch=amd64
# / * There is some issues with SCRAM Authentication on Postgresql on M1 Chip.
FROM --platform=linux/${arch} python:3.8.13-buster
MAINTAINER Klimushin Kirill email: kirklimushin@gmail.com

WORKDIR payment/app/
RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt ./production_requirements.txt
RUN pip install psycopg2-binary --no-cache-dir --no-input
RUN pip install -r production_requirements.txt

COPY . .

RUN chmod +x ./API/entrypoint.sh
ENTRYPOINT ["sh", "./API/entrypoint.sh"]


