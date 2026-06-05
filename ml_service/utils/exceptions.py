"""Custom exception classes for NeuroBright pipeline."""


class NeuroBrightError(Exception):
    """Base exception for NeuroBright."""
    
    def __init__(self, message, error_code=None, suggested_fix=None):
        self.message = message
        self.error_code = error_code
        self.suggested_fix = suggested_fix
        super().__init__(self.message)
    
    def __str__(self):
        msg = f"{self.message}"
        if self.error_code:
            msg += f" [Error Code: {self.error_code}]"
        if self.suggested_fix:
            msg += f"\nSuggested Fix: {self.suggested_fix}"
        return msg


class HardwareConnectionError(NeuroBrightError):
    """Raised when Arduino connection fails."""
    
    def __init__(self, message):
        super().__init__(
            message,
            error_code="HW001",
            suggested_fix="Check COM port, USB cable, and Arduino power. Verify port in config.yaml"
        )


class SignalQualityError(NeuroBrightError):
    """Raised when EEG signal quality is poor."""
    
    def __init__(self, message):
        super().__init__(
            message,
            error_code="SIG001",
            suggested_fix="Check electrode contact, reduce movement, ensure proper grounding"
        )


class ModelNotFoundError(NeuroBrightError):
    """Raised when trained model file is missing."""
    
    def __init__(self, message):
        super().__init__(
            message,
            error_code="MDL001",
            suggested_fix="Run 'python app.py --mode train' to train a model first"
        )


class InferenceError(NeuroBrightError):
    """Raised when real-time inference fails."""
    
    def __init__(self, message):
        super().__init__(
            message,
            error_code="INF001",
            suggested_fix="Check model compatibility, input shape, and preprocessing pipeline"
        )


class PreprocessingError(NeuroBrightError):
    """Raised when signal preprocessing fails."""
    
    def __init__(self, message):
        super().__init__(
            message,
            error_code="PRE001",
            suggested_fix="Verify raw data format, check filter parameters in config.yaml"
        )
