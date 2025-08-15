import time
import json
import psutil
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

PORT = 8080

# Prometheus metrics
REQUEST_COUNT = Counter(
    'lazargaws_pyapp_local_request_count', 'Request count', ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'lazargaws_pyapp_local_request_latency_seconds', 'Request latency', ['method', 'endpoint']
)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        start_time = time.time()

        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            content = "<html><body><h1>Hello from simple server</h1></body></html>"
            self.wfile.write(content.encode())

            REQUEST_COUNT.labels('GET', '/', 200).inc()
            REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"OK")

            REQUEST_COUNT.labels('GET', '/health', 200).inc()
            REQUEST_LATENCY.labels('GET', '/health').observe(time.time() - start_time)

        elif self.path == '/resources':
            cpu_percent = psutil.cpu_percent()
            mem = psutil.virtual_memory().used / (1024 * 1024)
            body = f"CPU: {cpu_percent}%, Memory: {mem:.2f} MB"
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(body.encode())

            REQUEST_COUNT.labels('GET', '/resources', 200).inc()
            REQUEST_LATENCY.labels('GET', '/resources').observe(time.time() - start_time)

        elif self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest())
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        start_time = time.time()

        if self.path == '/submit':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_post_data = self.rfile.read(content_length)
            try:
                data = json.loads(raw_post_data)
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            time.sleep(0.5)
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'received', 'data': data}
            self.wfile.write(json.dumps(response).encode())

            REQUEST_COUNT.labels('POST', '/submit', 201).inc()
            REQUEST_LATENCY.labels('POST', '/submit').observe(time.time() - start_time)
        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self):
        start_time = time.time()

        match = re.match(r"^/resource/(\d+)$", self.path)
        if match:
            resource_id = int(match.group(1))
            self.log_message(f"Deleting resource with ID: {resource_id}")
            time.sleep(0.2)  # Simulate deletion

            self.send_response(204)
            self.end_headers()

            REQUEST_COUNT.labels('DELETE', '/resource', 204).inc()
            REQUEST_LATENCY.labels('DELETE', '/resource').observe(time.time() - start_time)
        else:
            self.send_error(404, "Not Found")

def run():
    logging.info(f"Starting server on port {PORT}")
    server = HTTPServer(('', PORT), MyHandler)
    server.serve_forever()

if __name__ == '__main__':
    run()
