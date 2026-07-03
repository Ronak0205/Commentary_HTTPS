
import base64
import os

import requests

BASE_URL = "http://localhost:11434"

DEFAULT_TIMEOUT = 300


class OllamaError(Exception):
    """Base class for all errors raised by this client."""


class OllamaConnectionError(OllamaError):
    """Raised when the Ollama server can't be reached."""


class OllamaTimeoutError(OllamaError):
    """Raised when a request to Ollama times out."""


class OllamaResponseError(OllamaError):
    """Raised when Ollama returns a non-200 status code."""


class OllamaInvalidJSONError(OllamaError):
    """Raised when Ollama's response body isn't valid JSON."""


def _encode_image(image):
    """
    Reproduce the ollama-python SDK's image handling so callers can keep
    passing file paths exactly as before.
    """
    if isinstance(image, bytes):
        return base64.b64encode(image).decode("utf-8")

    if isinstance(image, str):
        if os.path.isfile(image):
            with open(image, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        return image

    raise OllamaError(f"Unsupported image type: {type(image)!r}")


def _prepare_messages(messages):
    prepared = []
    for msg in messages:
        new_msg = dict(msg)
        if new_msg.get("images"):
            new_msg["images"] = [_encode_image(img) for img in new_msg["images"]]
        prepared.append(new_msg)
    return prepared


def _post(path, payload, timeout):
    url = f"{BASE_URL}{path}"

    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.exceptions.Timeout as exc:
        raise OllamaTimeoutError(
            f"Request to {url} timed out after {timeout}s: {exc}"
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise OllamaConnectionError(
            f"Could not connect to Ollama at {url}. "
            f"Is the local Ollama server running? ({exc})"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise OllamaError(f"Request to {url} failed: {exc}") from exc

    if response.status_code != 200:
        raise OllamaResponseError(
            f"Ollama returned HTTP {response.status_code} for {url}: "
            f"{response.text[:500]}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise OllamaInvalidJSONError(
            f"Ollama returned a non-JSON response from {url}: {exc}"
        ) from exc


def chat(model, messages, think=False, options=None, stream=False, timeout=DEFAULT_TIMEOUT):
    payload = {
        "model": model,
        "messages": _prepare_messages(messages),
        "stream": stream,
        "think": think,
    }
    if options is not None:
        payload["options"] = options

    return _post("/api/chat", payload, timeout)


def generate(model, prompt, system=None, think=False, options=None, stream=False, timeout=DEFAULT_TIMEOUT):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "think": think,
    }
    if system is not None:
        payload["system"] = system
    if options is not None:
        payload["options"] = options

    return _post("/api/generate", payload, timeout)