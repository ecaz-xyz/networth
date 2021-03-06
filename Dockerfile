FROM python:3.10.5

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim

RUN pip install --upgrade pip

COPY pkg/ /app/

RUN pip install .

ENTRYPOINT ["networth"]
