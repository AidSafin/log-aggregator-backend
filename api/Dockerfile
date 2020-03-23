FROM python:3.8-alpine

ENV PYTHONPATH=${PYTHONPATH}:/app
WORKDIR /app
RUN apk add --no-cache gcc make libc-dev postgresql-dev
RUN apk add --no-cache python3-dev build-base linux-headers pcre-dev curl
ADD requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
