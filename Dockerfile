FROM python:3.11.1-slim

# set env variables
ENV PYTHONDONTWRITEBYTECODE="1"
ENV PYTHONUNBUFFERED="1"

# install dependencies
COPY requirements.txt .
COPY /src /src
RUN ["pip", "install", "-r",  "requirements.txt"]

# start main script
WORKDIR /src


CMD ["python", "main.py", "docker"]