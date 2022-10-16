FROM python:latest

WORKDIR /app

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

RUN pip3 install psycopg2==2.9.3

COPY . .

EXPOSE 5001

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5001"]
