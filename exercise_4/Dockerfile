FROM python:3.8-slim-buster

COPY . /app
WORKDIR /app

RUN pip3 install poetry==1.1.7
RUN pip3 install poetry-core==1.0.4
RUN poetry install

CMD ["poetry", "run", "jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]