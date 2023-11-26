ARG PYTHON=2.7

FROM python:${PYTHON}-alpine as builder

RUN apk add --no-cache gcc openssl-dev libffi-dev musl-dev
COPY requirements-testing.txt /
RUN pip install --no-cache-dir -r /requirements-testing.txt

FROM python:${PYTHON}-alpine

ARG PYTHON=2.7
COPY --from=builder \
    /usr/local/lib/python${PYTHON}/site-packages \
    /usr/local/lib/python${PYTHON}/site-packages

RUN apk add --no-cache bash zsh openssl && \
    (apk add --no-cache man || apk add --no-cache mandoc)

COPY . /pexpect
WORKDIR /pexpect

CMD python -m pytest --color yes --cov pexpect --cov-config .coveragerc tests
