FROM python:3-slim as builder

WORKDIR /usr/src/app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt > requirements.txt


FROM python:3-slim
WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get install -y mariadb-client
COPY --from=builder /usr/src/app/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "./main.py" ]
