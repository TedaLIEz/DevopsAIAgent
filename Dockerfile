FROM python:3.11
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./src /code/src
COPY .env /code/.env
COPY ./log_conf.yaml /code/log_conf.yaml
COPY ./data/test-app.private-key.pem /code/private-key.pem
EXPOSE 80
CMD ["python", "-m", "uvicorn", "src.main:app", "--reload", "--log-config=log_conf.yaml", "--port", "80", "--host", "0.0.0.0"]