FROM python:3

RUN mkdir /app
WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt

EXPOSE 80
CMD ["python3", "app.py"]
