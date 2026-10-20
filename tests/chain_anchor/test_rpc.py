from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from engines.chain_anchor.rpc import JsonRpcClient, RpcError, USER_AGENT


class FakeResponse:
    def __init__(self, value: dict):
        self._body = io.BytesIO(json.dumps(value).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self._body.read()


class JsonRpcClientTests(unittest.TestCase):
    def test_https_is_required(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            JsonRpcClient("http://rpc.invalid")

    @patch("engines.chain_anchor.rpc.urllib.request.urlopen")
    def test_headers_and_request_response_semantics(self, urlopen):
        urlopen.side_effect = [
            FakeResponse({"jsonrpc": "2.0", "id": 1, "result": "0x14a34"}),
            FakeResponse({"jsonrpc": "2.0", "id": 2, "result": {"status": "0x1"}}),
        ]
        client = JsonRpcClient("https://rpc.example", timeout_seconds=7.5)

        self.assertEqual(client.call("eth_chainId", []), "0x14a34")
        self.assertEqual(
            client.call("eth_getTransactionReceipt", ["0x" + "11" * 32]),
            {"status": "0x1"},
        )

        first_request = urlopen.call_args_list[0].args[0]
        first_payload = json.loads(first_request.data)
        self.assertEqual(first_request.get_header("Content-type"), "application/json")
        self.assertEqual(first_request.get_header("User-agent"), USER_AGENT)
        self.assertEqual(first_payload, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_chainId",
            "params": [],
        })
        self.assertEqual(urlopen.call_args_list[0].kwargs["timeout"], 7.5)
        self.assertEqual(json.loads(urlopen.call_args_list[1].args[0].data)["id"], 2)

    @patch("engines.chain_anchor.rpc.urllib.request.urlopen")
    def test_transport_errors_fail_closed(self, urlopen):
        urlopen.side_effect = OSError("network unavailable")

        with self.assertRaisesRegex(RpcError, "transport failed for eth_chainId"):
            JsonRpcClient("https://rpc.example").call("eth_chainId", [])

    @patch("engines.chain_anchor.rpc.urllib.request.urlopen")
    def test_json_rpc_validation_is_unchanged(self, urlopen):
        client = JsonRpcClient("https://rpc.example")

        urlopen.return_value = FakeResponse({"jsonrpc": "2.0", "id": 9, "result": "0x1"})
        with self.assertRaisesRegex(RpcError, "Malformed"):
            client.call("eth_chainId", [])

        urlopen.return_value = FakeResponse(
            {"jsonrpc": "2.0", "id": 2, "error": {"code": -32000}}
        )
        with self.assertRaisesRegex(RpcError, "returned an error"):
            client.call("eth_chainId", [])

        urlopen.return_value = FakeResponse({"jsonrpc": "2.0", "id": 3})
        with self.assertRaisesRegex(RpcError, "omitted result"):
            client.call("eth_chainId", [])


if __name__ == "__main__":
    unittest.main()
