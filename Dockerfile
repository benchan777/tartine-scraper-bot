From python:latest

WORKDIR /app

COPY . /app
RUN pip3 install -r requirements.txt

CMD python3 app.py
EXPOSE 3000