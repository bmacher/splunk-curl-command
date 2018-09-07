# docker build -t splunk_appinspect .
# docker run --name splunk_appinspect -it splunk_appinspect
# ENTRYPOINT

FROM ubuntu:latest

LABEL maintainer="Benjamin Macher"
LABEL "splunk-appinspect-version"="1.5.4.145"
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python-pip
RUN pip install --upgrade pip setuptools
RUN apt-get install -y libxml2-dev libxslt-dev lib32z1-dev python-lxml
RUN mkdir -p /home/downloads
RUN mkdir -p /home/splunk_apps
RUN apt-get install -y wget
RUN wget http://dev.splunk.com/goto/appinspectdownload -O "/home/downloads/splunk_appinspect.tar.gz"
RUN pip install /home/downloads/splunk_appinspect.tar.gz
COPY ./dist/curl_command* /home/splunk_apps