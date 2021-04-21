FROM python

WORKDIR /opt
COPY ./ .
RUN python -m pip install -r requirements.txt

WORKDIR /opt/src
ENTRYPOINT ["python", "main.py"]
