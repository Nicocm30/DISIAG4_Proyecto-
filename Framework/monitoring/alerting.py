import smtplib
import json
from email.mime.text import MIMEText
from pathlib import Path


# ============================================================
# CONFIG
# ============================================================

EMAIL_FROM = "tu_correo@gmail.com"
EMAIL_PASSWORD = "tu_app_password"
EMAIL_TO = "tu_correo@gmail.com"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

DRIFT_RESULTS_PATH = Path("/app/monitoring/reports/drift_results.json")


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(subject, body):

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f"Email enviado: {subject}")


# ============================================================
# ALERTA DE MODELO (DRIFT)
# ============================================================

def model_alert():

    if not DRIFT_RESULTS_PATH.exists():
        print("No hay reporte de drift")
        return

    with open(DRIFT_RESULTS_PATH, "r", encoding="utf-8") as f:
        results = json.load(f)

    drifted = [r for r in results if r["drift_detected"]]

    if not drifted:
        print("No hay drift, no se envía alerta")
        return

    body = "ALERTA DE MODELO (DRIFT DETECTADO)\n\n"
    body += "Variables afectadas:\n"

    for d in drifted:
        body += f"- {d['feature']} (p={d['p_value']:.5f})\n"

    body += "\nSe recomienda reentrenar el modelo."

    send_email(
        subject="VRCE ALERTA: Drift detectado",
        body=body
    )


# ============================================================
# ALERTA OPERATIVA (EJEMPLO SIMPLE)
# ============================================================

def operational_alert(latency_value):

    THRESHOLD = 2.0  # segundos

    if latency_value < THRESHOLD:
        print("Latencia normal")
        return

    body = f"""
ALERTA OPERATIVA

Latencia alta detectada:
{latency_value} segundos

Posible degradación del sistema.
"""

    send_email(
        subject="VRCE ALERTA: Alta latencia",
        body=body
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("\n===== SISTEMA DE ALERTAS =====\n")

    # ALERTA DE MODELO
    model_alert()

    # ALERTA OPERATIVA (simulada)
    operational_alert(latency_value=2.5)
