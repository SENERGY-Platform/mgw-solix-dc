FROM python:3-slim

LABEL org.opencontainers.image.source=https://github.com/SENERGY-Platform/mgw-solix-dc

RUN apt-get update && apt-get install git -y

WORKDIR /usr/src/app

COPY . .
RUN pip install --extra-index-url https://www.piwheels.org/simple --no-cache-dir -r requirements.txt

CMD [ "python", "-u", "./dc.py"]
