# Pattern: Chain of Responsibility (Concrete Handler)
import random
from hardware.failure_handler import FailureHandler

class RecalibrationHandler(FailureHandler):

    def get_handler_name(self): return "Recalibration"

    def handle(self, failure: dict, log_cb=None) -> dict:
        component = failure.get("component", "Unknown")
        if log_cb:
            log_cb(f"⚙ Recalibration: Running hardware diagnostics on {component}...")

        success = random.random() < 0.60  # 60% success rate
        if success:
            msg = f"{component} successfully recalibrated"
            if log_cb:
                log_cb(f"✅ Recalibration: {msg}")
            return {"resolved": True, "handler": self.get_handler_name(), "message": msg}

        if log_cb:
            log_cb(f"❌ Recalibration: Failed — escalating to Technician Alert...")
        return self._forward(failure, log_cb)
