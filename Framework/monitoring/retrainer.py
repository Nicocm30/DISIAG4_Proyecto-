import time
import subprocess

INTERVAL = 3600  # 1 hora

while True:
    print("\n=== VRCE AUTO RETRAIN ===\n")

    subprocess.run([
        "docker", "compose", "run", "--rm",
        "training",
        "python", "//app/monitoring/drift_report.py"
    ])

    subprocess.run([
        "docker", "compose", "run", "--rm",
        "training",
        "python", "//app/monitoring/feedback_loop.py"
    ])

    result = subprocess.run(
        ["grep", "-q", '"drift_detected": true', "monitoring/reports/drift_results.json"]
    )

    if result.returncode == 0:
        print("Drift detectado → reentrenando")

        subprocess.run([
            "docker", "compose", "run", "--rm", "training"
        ])

        subprocess.run([
            "docker", "compose", "up", "-d", "--build", "inference"
        ])

    else:
        print("No hay drift")

    time.sleep(INTERVAL)
