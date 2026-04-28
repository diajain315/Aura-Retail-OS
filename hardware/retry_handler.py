# Pattern: Chain of Responsibility (Concrete Handler)
import random
from hardware.failure_handler import FailureHandler

class RetryHandler(FailureHandler):

    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries

    def get_handler_name(self): return "AutoRetry"

    def handle(self, failure: dict, log_cb=None) -> dict:
        component = failure.get("component", "Unknown")
        severity = failure.get("severity", "medium")
        if log_cb:
            log_cb(f"🔄 AutoRetry: Attempting to restart {component}...")

        success_prob = {"low": 0.75, "medium": 0.45, "high": 0.20, "critical": 0.05}.get(severity, 0.4)

        for attempt in range(1, self.max_retries + 1):
            if random.random() < success_prob:
                msg = f"Recovered on attempt {attempt}/{self.max_retries}"
                if log_cb:
                    log_cb(f"✅ AutoRetry: {msg}")
                return {"resolved": True, "handler": self.get_handler_name(), "message": msg}
            if log_cb:
                log_cb(f"⚠ AutoRetry: Attempt {attempt}/{self.max_retries} failed...")

        if log_cb:
            log_cb(f"❌ AutoRetry: All {self.max_retries} attempts failed — escalating to Recalibration...")
        return self._forward(failure, log_cb)
