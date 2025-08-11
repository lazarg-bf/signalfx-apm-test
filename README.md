# Kubernetes + Splunk OpenTelemetry Example

This guide demonstrates how to run Node.js and Python sample applications on Kubernetes (via Docker Desktop) with Splunk OpenTelemetry instrumentation.

## Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Kubernetes enabled
- `kubectl` CLI installed and configured
- Splunk Observability Cloud account with:
  - **Access Token** (`SPLUNK_ACCESS_TOKEN`)
  - **HEC Token** (`SPLUNK_HEC_TOKEN`)

---

## 1. Start Kubernetes in Docker Desktop
1. Open Docker Desktop.
2. Go to **Settings** → **Kubernetes**.
3. Enable **Kubernetes** and wait until it's running.

---

## 2. Configure Splunk OpenTelemetry Collector
Edit `splunk-otel-deploy.yaml` and update the following environment variables:

```yaml
env:
  - name: SPLUNK_ACCESS_TOKEN
    value: "<ADD-YOURS>"
  - name: SPLUNK_REALM
    value: "eu0"
  - name: SPLUNK_METRICS_ENABLED
    value: "true"
  - name: SPLUNK_TRACE_ENABLED
    value: "true"
  - name: SPLUNK_LOGS_ENABLED
    value: "false"
  - name: SPLUNK_HEC_TOKEN
    value: "<ADD-YOURS>"
```

Apply the configuration:

```bash
kubectl apply -f splunk-otel-deploy.yaml
```

---

## 3. Build and Deploy Applications

### Build Docker images
```bash
# Build Node.js app image
cd nodejs-app
docker build -t apmtest-nodejs:latest .

# Build Python app image
cd ../python-app
docker build -t apmtest-python:latest .

# Return to project root
cd ../
```

### Deploy to Kubernetes
```bash
# Deploy Node.js app
kubectl apply -f apmtest-nodejs-deploy.yaml

# Deploy Python app
kubectl apply -f apmtest-python-deploy.yaml
```

---

## 4. Access the Applications

- **Node.js App:** [http://localhost:8000/](http://localhost:8000/)  
- **Python App:** [http://localhost:8001/](http://localhost:8001/)
- **Do some test calls:** 
```bash
for i in {1..10000}; do curl http://localhost:8000/; curl http://localhost:8001/; sleep 1; done
```

---

## 5. Verify
Check if all pods are running:

```bash
kubectl get pods
```

Logs can be viewed with:

```bash
kubectl logs <pod-name>
```

---

## 6. Check signalfx AP
If traces are sent OK, you should find<br>
**apmtest-nodejs** & **apmtest-python**<br>
in<br>
https://dev.signalfx.com/#/apm<br>
filtering by Environment **Dev**


