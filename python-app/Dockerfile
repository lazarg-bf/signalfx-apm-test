FROM python:3

EXPOSE 8080

WORKDIR /python_app
#RUN apt update
#RUN apt install -y awscli

COPY requirements.txt .

RUN adduser --uid 1000 uki

RUN pip install --no-cache-dir -r requirements.txt
RUN opentelemetry-bootstrap -a install


COPY --chown=uki python_app.py /python_app/app.py
COPY --chown=uki templates /python_app/templates

ENV OTEL_SERVICE_NAME=apmtest-python
# required to get the logs corelated with span_id
# ENV OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
# ENV OTEL_PYTHON_LOG_CORRELATION=true

USER 1000

CMD ["opentelemetry-instrument", "python", "app.py"]
