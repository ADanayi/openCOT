FROM python:3.6-slim

WORKDIR /app

COPY . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 2020

ENV openCOT V1

CMD ["python", "FEU.py"]
