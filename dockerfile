FROM python:alpine AS base

ENV LANG=C.UTF-8
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./models ./models
COPY ./main.py .
COPY ./db.py .
COPY ./migrations ./migrations
COPY ./alembic.ini .
COPY ./entrypoint.sh .
COPY ./utils ./utils
COPY ./cronjob.py .
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 80

FROM base AS dev
ENV DEBUG=True
CMD ["fastapi", "run", "/app/main.py", "--port", "80"]

FROM base AS prod
ENV DEBUG=False
CMD ["fastapi", "run", "/app/main.py", "--port", "80"]
