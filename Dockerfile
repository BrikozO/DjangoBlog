FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /brikolog

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /brikolog

EXPOSE 8000
#RUN python manage.py makemigrations && python manage.py migrate && python manage.py loaddata blog_data.json
