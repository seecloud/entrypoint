FROM entry_base:latest

COPY conf.json /etc/conf.json
COPY service.py /opt/

EXPOSE 8000

CMD ["/usr/bin/python", "/opt/service.py"]
