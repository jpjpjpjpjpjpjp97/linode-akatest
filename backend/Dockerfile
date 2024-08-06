FROM python:3.12

RUN pip install pipenv

WORKDIR /code

COPY ./Pipfile* /code/

RUN pipenv install --system

COPY ./app /code/app

EXPOSE 80

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
