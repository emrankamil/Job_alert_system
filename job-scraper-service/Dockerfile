FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["flask", "--app", "src/app.py", "--debug", "run","--host=0.0.0.0", "--port=5000"]
