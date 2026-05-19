const express = require("express");
const { spawn } = require("child_process");
const swaggerUi = require("swagger-ui-express");
const swaggerDocument = require("./swagger.json");
const client = require("prom-client");

const app = express();
app.use(express.json());
const register = new client.Registry();

const cpuUsageGauge = new client.Gauge({
  name: "vrce_cpu_usage_percent",
  help: "CPU usage percentage"
});

const memoryUsageGauge = new client.Gauge({
  name: "vrce_memory_usage_bytes",
  help: "RAM memory usage in bytes"
});

const httpRequestCounter = new client.Counter({
  name: "vrce_http_requests_total",
  help: "Total HTTP requests",
  labelNames: ["method", "route", "status"]
});

const predictionLatencyHistogram = new client.Histogram({
  name: "vrce_prediction_latency_seconds",
  help: "Prediction latency in seconds",
  buckets: [0.1, 0.3, 0.5, 1, 2, 5]
});

register.registerMetric(cpuUsageGauge);
register.registerMetric(memoryUsageGauge);
register.registerMetric(httpRequestCounter);
register.registerMetric(predictionLatencyHistogram);

let lastCpuUsage = process.cpuUsage();
let lastHrTime = process.hrtime();

function updateSystemMetrics() {
  const currentCpuUsage = process.cpuUsage(lastCpuUsage);
  const currentHrTime = process.hrtime(lastHrTime);

  const elapsedMicros = currentHrTime[0] * 1e6 + currentHrTime[1] / 1e3;
  const usedMicros = currentCpuUsage.user + currentCpuUsage.system;

  const cpuPercent = (usedMicros / elapsedMicros) * 100;

  cpuUsageGauge.set(cpuPercent);

  const memoryUsage = process.memoryUsage();
  memoryUsageGauge.set(memoryUsage.rss);

  lastCpuUsage = process.cpuUsage();
  lastHrTime = process.hrtime();
}

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));

app.get("/health", (req, res) => {
  httpRequestCounter.inc({
    method: "GET",
    route: "/health",
    status: "200"
  });

  res.json({
    status: "OK",
    service: "VRCE Inference API"
  });
});

app.post("/predict", (req, res) => {
  const python = spawn("python3", ["predict.py"]);

  python.stdin.write(JSON.stringify(req.body));
  python.stdin.end();
  const endTimer = predictionLatencyHistogram.startTimer();

  let result = "";
  let error = "";

  python.stdout.on("data", (data) => {
    result += data.toString();
  });

  python.stderr.on("data", (data) => {
    error += data.toString();
  });

  python.on("close", (code) => {
    if (code !== 0) {
      endTimer();
      httpRequestCounter.inc({
        method: "POST",
        route: "/predict",
        status: "500"
      });

      return res.status(500).json({
        error: "Prediction failed",
        details: error
      });
    }

    try {
      endTimer();
      httpRequestCounter.inc({
        method: "POST",
        route: "/predict",
        status: "200"
      });

      res.json(JSON.parse(result));
    } catch (err) {
      endTimer();
      httpRequestCounter.inc({
        method: "POST",
        route: "/predict",
        status: "500"
      });

      res.status(500).json({
        error: "Invalid prediction output",
        raw: result
      });
    }
  });
});

app.get("/metrics", async (req, res) => {
  updateSystemMetrics();

  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});

app.listen(3000, () => {
  console.log("VRCE Inference API running on port 3000");
  console.log("Swagger docs available at http://localhost:3000/api-docs");
});
