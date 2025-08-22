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
    template = render_template('index.html')
    REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)
    return template


@app.route('/health')
def health():
    return "OK"

@app.route('/submit', methods=['POST'])
def submit():
    start_time = time.time()

    # Simulate processing submitted data
    data = request.get_json()
    app.logger.info(f"Received data: {data}")
    time.sleep(0.5)  # simulate work

    REQUEST_COUNT.labels('POST', '/submit', 201).inc()
    REQUEST_LATENCY.labels('POST', '/submit').observe(time.time() - start_time)
    return {"status": "received", "data": data}, 201


@app.route('/resource/<int:id>', methods=['DELETE'])
def delete_resource(id):
    start_time = time.time()

    # Simulate deletion of a resource
    app.logger.info(f"Deleting resource with ID: {id}")
    time.sleep(0.2)  # simulate work

    REQUEST_COUNT.labels('DELETE', '/resource', 204).inc()
    REQUEST_LATENCY.labels('DELETE', '/resource').observe(time.time() - start_time)
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
