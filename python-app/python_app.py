from flask import Flask, request, render_template
from flask_sock import Sock
import time
import asyncio
import psutil
import numpy as np
import logging
from prometheus_client import make_wsgi_app, Counter, Histogram
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import time
import requests
#The traces instrumentation is done "automatically" as the library supports flask(), you will get the traces and the RED metrics out of the box, so 
#for the use-case here you don't need to manually create your lazargaws_* counts and latency metrics (RED stands for Request Errors and Duration).
#Just for the sake of the exercise I am creating the same measurements via Otel Native.
#The same way is for logs, the autoinstrumentation supports loggin(), so if you setup your HEC/Token you will get your application logs sent directly to Splunk Cloud, 
#no need to pipe it to stdout and then read the logfile with Splunk Universal Forwarder of Otel Filelog receiver.. 

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )

from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)

metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
provider = MeterProvider(metric_readers=[metric_reader])
# Sets the global default meter provider
metrics.set_meter_provider(provider)
# Creates a meter from the global meter provider, the metrics are named "cf_pyapp_local_request" and "cf_pyapp_local_request_latency_second"
meter = metrics.get_meter("my.meter.name")
cf_request_count = meter.create_counter(name="cf_pyapp_local_request.count", unit="1", description="Counter type metric type")
cf_request_latency = meter.create_histogram(name="cf_pyapp_local_request_latency_seconds.histo", unit="s")

app = Flask(__name__)
sock = Sock(app)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

REQUEST_COUNT = Counter(
    'lazargaws_pyapp_local_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'lazargaws_pyapp_local_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)


class HealthRequestFilter(logging.Filter):
    def filter(self, record):
        # Exclude log records for /health requests
        return 'health' not in record.getMessage() and 'metrics' not in record.getMessage()

# Create a logger and add the custom filter to it
logger = logging.getLogger('werkzeug')
# logger.addFilter(HealthRequestFilter())

@app.route('/')
def hello():
    start_time = time.time()
    REQUEST_COUNT.labels('GET', '/', 200).inc()
    # getting a counter  metric via Otel native
    cf_request_count.add(1, {
        "method": request.method,
        "endpoint": request.endpoint,
    });
    template = render_template('index.html')
    REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)
    # getting a histogram  metric via Otel native
    cf_request_latency.record((time.time() - start_time), {
        "method": request.method,
        "endpoint": request.endpoint})
    return template


@app.route('/health')
def health():
    cf_request_count.add(1, {
        "method": request.method,
        "endpoint": request.endpoint,
    });    
    return "OK";


@app.route('/submit', methods=['POST'])
def submit():
    start_time = time.time()

    # Simulate processing submitted data
    data = request.get_json()
    app.logger.info(f"Received data: {data}")
    time.sleep(0.5)  # simulate work

    REQUEST_COUNT.labels('POST', '/submit', 201).inc()
    # getting a counter  metric via Otel native
    cf_request_count.add(1, {
        "method": request.method,
        "endpoint": request.endpoint,
    });


    REQUEST_LATENCY.labels('POST', '/submit').observe(time.time() - start_time)
    # getting a histogram  metric via Otel native
    cf_request_latency.record((time.time() - start_time), {
        "method": request.method,
        "endpoint": request.endpoint})

    return {"status": "received", "data": data}, 201


@app.route('/resource/<int:id>', methods=['DELETE'])
def delete_resource(id):
    start_time = time.time()

    # Simulate deletion of a resource
    app.logger.info(f"Deleting resource with ID: {id}")
    time.sleep(0.2)  # simulate work

    REQUEST_COUNT.labels('DELETE', '/resource', 204).inc()
    # getting a counter  metric via Otel native
    cf_request_count.add(1, {
        "method": request.method,
        "endpoint": request.endpoint,
    });    
    REQUEST_LATENCY.labels('DELETE', '/resource').observe(time.time() - start_time)
    # getting a histogram  metric via Otel native
    cf_request_latency.record((time.time() - start_time), {
        "method": request.method,
        "endpoint": request.endpoint})

    return '', 204

# the debug parameter here was creating the original issue
# https://opentelemetry.io/docs/zero-code/python/troubleshooting/#flask-debug-mode-with-reloader-breaks-instrumentation
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

