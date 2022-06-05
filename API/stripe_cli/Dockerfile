FROM python:3.8.13-buster
WORKDIR cli/
COPY ../../stripe_cli.py ./cli/stripe_cli.py
RUN pip install asgiref && pip install docker
RUN python ./cli/stripe_cli.py




