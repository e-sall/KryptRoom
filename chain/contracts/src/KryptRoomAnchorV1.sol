// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.37;

/// @title KryptRoomAnchorV1
/// @notice Permissionless, event-only publication of opaque KryptRoom commitments.
/// @dev The submitter is only the transaction sender. It is not a KryptRoom
/// participant identity, authorization, or approval signal.
contract KryptRoomAnchorV1 {
    error ZeroAnchorCommitment();

    event AnchorRecorded(bytes32 indexed anchorCommitment, address indexed submitter);

    function anchor(bytes32 anchorCommitment) external {
        if (anchorCommitment == bytes32(0)) revert ZeroAnchorCommitment();
        emit AnchorRecorded(anchorCommitment, msg.sender);
    }
}
