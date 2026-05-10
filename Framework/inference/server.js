const express = require("express");
const { spawn } = require("child_process");
const swaggerUi = require("swagger-ui-express");
const swaggerDocument = require("./swagger.json");

const app = express();
app.use(express.json());

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerDocument));

app.get("/health", (req, res) => {
  res.json({
    status: "OK",
    service: "VRCE Inference API"
  });
});

app.post("/predict", (req, res) => {
  const python = spawn("python3", ["predict.py"]);

  python.stdin.write(JSON.stringify(req.body));
  python.stdin.end();

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
      return res.status(500).json({
        error: "Prediction failed",
        details: error
      });
    }

    try {
      res.json(JSON.parse(result));
    } catch (err) {
      res.status(500).json({
        error: "Invalid prediction output",
        raw: result
      });
    }
  });
});

app.listen(3000, () => {
  console.log("VRCE Inference API running on port 3000");
  console.log("Swagger docs available at http://localhost:3000/api-docs");
});
