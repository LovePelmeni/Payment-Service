FROM python:3.8.13-buster

RUN pip install --upgrade pip
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./production_requirements.txt
RUN pip install -r production_requirements.txt
COPY . .

ENTRYPOINT ["sh", "./entrypoint.sh"]
