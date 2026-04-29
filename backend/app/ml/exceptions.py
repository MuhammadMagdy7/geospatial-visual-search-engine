"""Custom exceptions for the ML module."""


class MLException(Exception):
    """Base exception for ML errors."""
    pass


class ModelNotLoadedError(MLException):
    """Raised when trying to use the model before it is loaded."""
    pass


class ModelLoadError(MLException):
    """Raised when the model fails to load (network, missing file, etc.)."""
    pass


class EmbeddingFailedError(MLException):
    """Raised when an embedding operation fails."""
    pass
