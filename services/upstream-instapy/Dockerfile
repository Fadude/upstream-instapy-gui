FROM python:3.7-slim-buster

WORKDIR /usr/instapy

RUN sed -i "s#deb http://deb.debian.org/debian buster main#deb http://deb.debian.org/debian buster main contrib non-free#g" /etc/apt/sources.list \
	&& apt-get update && apt-get install -y --no-install-recommends \
	wget git gcc g++ libffi6 libffi-dev musl-dev python3-dev\
	firefox-esr \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*
	
RUN pip3 install --upgrade setuptools pip
RUN pip3 install grpcio

COPY . .

RUN pip3 install -r requirements.txt;

RUN sed -i.bak "320s|^.*$|            filename = [name for name in filenames if os_name + bitness in name and name[-3:] != 'asc' ]|" /usr/local/lib/python3.7/site-packages/webdriverdownloader/webdriverdownloader.py

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
RUN tar -xvzf geckodriver-v0.26.0-linux64.tar.gz
RUN chmod +x geckodriver
RUN mv geckodriver /usr/bin/

CMD ["python3", "-u", "start.py"]
