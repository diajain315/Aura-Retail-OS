# Pattern: Chain of Responsibility (Concrete Handler)
from datetime import datetime
from hardware.failure_handler import FailureHandler

class TechnicianAlertHandler(FailureHandler):

    def __init__(self):
        super().__init__()
        self.alerts_sent = []

    def get_handler_name(self): return "TechnicianAlert"

    def handle(self, failure: dict, log_cb=None) -> dict:
        component = failure.get("component", "Unknown")
        severity = failure.get("severity", "unknown")
        ts = datetime.now().strftime("%H:%M:%S")

        alert = {
            "timestamp": ts,
            "component": component,
            "severity": severity,
            "error": failure.get("error_message", "")
        }
        self.alerts_sent.append(alert)

        msg = f"Technician dispatched for {component} [{severity.upper()}]"
        if log_cb:
            log_cb(f"🚒 TechnicianAlert: {msg}")
            log_cb(f"📧 Alert sent to maintenance team @ {ts}")

        return {"resolved": True, "handler": self.get_handler_name(),
                "message": msg, "alert": alert}
