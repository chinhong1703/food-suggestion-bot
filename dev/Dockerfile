FROM python:3.7

RUN mkdir /app
ADD .. /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt


CMD python /app/application.py