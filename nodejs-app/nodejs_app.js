const express = require('express');
const promClient = require('prom-client');
const path = require('path');

const app = express();
const port = process.env.PORT || 8080;
const fetch = require('node-fetch');

const https = require('https');
const http = require('http');
const url = require('url');

const httpsAgent = new https.Agent({
  rejectUnauthorized: false
});

// Default metrics collection
promClient.collectDefaultMetrics({ timeout: 5000 });

// Custom metrics
const REQUEST_COUNT = new promClient.Counter({
  name: 'lazargaws_app_request_count',
  help: 'Application Request Count',
  labelNames: ['method', 'endpoint', 'http_status']
});

const REQUEST_LATENCY = new promClient.Histogram({
  name: 'lazargaws_app_request_latency_seconds',
  help: 'Application Request Latency',
  labelNames: ['method', 'endpoint'],
  buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5] // latency buckets in seconds
});

// Middleware to measure latency and count
app.use((req, res, next) => {
  const startEpoch = process.hrtime.bigint(); // high-resolution start
  const endTimer = REQUEST_LATENCY.startTimer({ method: req.method, endpoint: req.path });

  res.on('finish', () => {
    const endEpoch = process.hrtime.bigint();
    const durationMs = Number(endEpoch - startEpoch) / 1_000_000; // nanoseconds to ms

    REQUEST_COUNT.inc({
      method: req.method,
      endpoint: req.path,
      http_status: res.statusCode
    });

    endTimer(); // record latency in histogram

    console.log(`[${req.method}] ${req.path} - ${res.statusCode} - ${durationMs.toFixed(2)}ms`);
  });

  next();
});

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', promClient.register.contentType);
    res.end(await promClient.register.metrics());
  } catch (err) {
    res.status(500).end(err.message);
  }
});

// POST /submit
app.post('/submit', (req, res) => {
  const data = req.body;
  console.log(`Received data:`, data);
  setTimeout(() => {
    res.status(201).json({ status: 'received', data });
  }, 500); // Simulate delay
});

// DELETE /resource/:id
app.delete('/resource/:id', (req, res) => {
  const id = req.params.id;
  console.log(`Deleting resource with ID: ${id}`);
  setTimeout(() => {
    res.status(204).send(); // Simulate deletion delay
  }, 200);
});

app.get('/backendrita', async (req, res) => {
  const backendUrl = process.env.BACKEND_RITA;

  if (!backendUrl) {
    return res.status(500).json({ error: 'BACKEND_RITA not set' });
  }

  const parsedUrl = require('url').parse(backendUrl);
  const agent = parsedUrl.protocol === 'https:' 
    ? new https.Agent({ rejectUnauthorized: false }) 
    : new http.Agent();

  try {
    const response = await fetch(backendUrl, { agent });
    const data = await response.json();
    res.status(response.status).send(data);
  } catch (error) {
    console.error('Error calling BACKEND_RITA:', error);
    res.status(502).json({ error: 'Failed to call BACKEND_RITA' });
  }
});

app.get('/backendtom', async (req, res) => {
  const backendUrl = process.env.BACKEND_TOM;

  if (!backendUrl) {
    return res.status(500).json({ error: 'BACKEND_TOM not set' });
  }

  const parsedUrl = require('url').parse(backendUrl);
  const agent = parsedUrl.protocol === 'https:' 
    ? new https.Agent({ rejectUnauthorized: false }) 
    : new http.Agent();

  try {
    const response = await fetch(backendUrl, { agent });
    const data = await response.json();
    res.status(response.status).send(data);
  } catch (error) {
    console.error('Error calling BACKEND_TOM:', error);
    res.status(502).json({ error: 'Failed to call BACKEND_TOM' });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
