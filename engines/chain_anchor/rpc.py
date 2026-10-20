"""Small authenticated-transport-agnostic Ethereum JSON-RPC client."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Protocol


USER_AGENT = "KryptRoom-M7/1"


class RpcError(RuntimeError):
    pass


class RpcClient(Protocol):
    def call(self, method: str, params: list[Any]) -> Any: ...


class JsonRpcClient:
    def __init__(self, url: str, *, timeout_seconds: float = 30.0):
        if not url.startswith("https://"):
            raise ValueError("Public-chain RPC URL must use HTTPS")
        self._url = url
        self._timeout = timeout_seconds
        self._next_id = 1

    def call(self, method: str, params: list[Any]) -> Any:
        request_id = self._next_id
        self._next_id += 1
        body = json.dumps(
            {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params},
            separators=(",", ":"),
        ).encode("utf-8")
        request = urllib.request.Request(
            self._url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                value = json.loads(response.read())
        except Exception as error:
            raise RpcError(f"JSON-RPC transport failed for {method}") from error
        if value.get("id") != request_id or value.get("jsonrpc") != "2.0":
            raise RpcError("Malformed JSON-RPC response")
        if "error" in value:
            raise RpcError(f"JSON-RPC {method} returned an error: {value['error']}")
        if "result" not in value:
            raise RpcError("JSON-RPC response omitted result")
        return value["result"]
