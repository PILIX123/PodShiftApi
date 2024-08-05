FROM python:alpine

ENV LANG=C.UTF-8
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./models ./models
COPY ./main.py .
COPY ./db.py .
COPY ./migrations ./migrations
COPY ./alembic.ini .
COPY ./entrypoint.sh .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 80

CMD ["fastapi", "run", "/app/main.py", "--port", "80"]