const express = require("express");
const { spawn } = require("child_process");

const app = express();
app.use(express.json({ limit: "1mb" }));

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "VRCE Inference API" });
});

app.post("/predict", (req, res) => {
  const py = spawn("python3", ["predict.py"], { cwd: __dirname });

  let stdout = "";
  let stderr = "";

  py.stdout.on("data", (data) => {
    stdout += data.toString();
  });

  py.stderr.on("data", (data) => {
    stderr += data.toString();
  });

  py.on("close", (code) => {
    if (code !== 0) {
      return res.status(500).json({
        error: "Prediction failed",
        details: stderr.trim()
      });
    }

    try {
      return res.json(JSON.parse(stdout));
    } catch (_err) {
      return res.status(500).json({
        error: "Invalid prediction output",
        raw: stdout
      });
    }
  });

  py.stdin.write(JSON.stringify(req.body));
  py.stdin.end();
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`VRCE Inference API running on port ${port}`);
});
