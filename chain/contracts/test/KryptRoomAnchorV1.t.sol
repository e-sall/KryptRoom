// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.37;

import { KryptRoomAnchorV1 } from "../src/KryptRoomAnchorV1.sol";

struct VmLog {
    bytes32[] topics;
    bytes data;
    address emitter;
}

interface Vm {
    function recordLogs() external;
    function getRecordedLogs() external returns (VmLog[] memory);
}

contract KryptRoomAnchorV1Test {
    Vm private constant VM = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    bytes32 private constant EVENT_TOPIC = keccak256("AnchorRecorded(bytes32,address)");

    KryptRoomAnchorV1 private anchorContract;

    function setUp() public {
        anchorContract = new KryptRoomAnchorV1();
    }

    function testAnchorEmitsOnlyCommitmentAndSubmitter() public {
        bytes32 commitment = sha256("kryptroom-m7-test-vector");
        VM.recordLogs();

        anchorContract.anchor(commitment);

        VmLog[] memory entries = VM.getRecordedLogs();
        require(entries.length == 1, "unexpected log count");
        require(entries[0].emitter == address(anchorContract), "wrong emitter");
        require(entries[0].topics.length == 3, "wrong topic count");
        require(entries[0].topics[0] == EVENT_TOPIC, "wrong event signature");
        require(entries[0].topics[1] == commitment, "wrong commitment");
        require(entries[0].topics[2] == bytes32(uint256(uint160(address(this)))), "wrong submitter");
        require(entries[0].data.length == 0, "unexpected event data");
    }

    function testZeroCommitmentReverts() public {
        (bool ok,) =
            address(anchorContract).call(abi.encodeCall(KryptRoomAnchorV1.anchor, (bytes32(0))));
        require(!ok, "zero commitment accepted");
    }

    function testDuplicateCommitmentIsAccepted() public {
        bytes32 commitment = sha256("duplicate-is-legal");
        VM.recordLogs();

        anchorContract.anchor(commitment);
        anchorContract.anchor(commitment);

        VmLog[] memory entries = VM.getRecordedLogs();
        require(entries.length == 2, "duplicate was not emitted twice");
        require(entries[0].topics[1] == commitment, "first duplicate mismatch");
        require(entries[1].topics[1] == commitment, "second duplicate mismatch");
    }
}
