FROM python:3.8.13-buster

WORKDIR payment/app/
RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt ./production_requirements.txt
RUN pip install psycopg2-binary --no-cache-dir --no-input
RUN pip install -r production_requirements.txt

COPY . .
ENTRYPOINT ["sh", "./entrypoint.sh"]


