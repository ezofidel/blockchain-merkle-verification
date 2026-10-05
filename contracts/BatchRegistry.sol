// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BatchRegistry {

    address public owner;

    mapping(string => bytes32) private batchRoots;

    event BatchRootStored(
        string batchId,
        bytes32 merkleRoot
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Yetkisiz kullanici"
        );
        _;
    }

    function storeBatchRoot(
        string calldata batchId,
        bytes32 merkleRoot
    )
        external
        onlyOwner
    {
        require(
            merkleRoot != bytes32(0),
            "Merkle Root bos olamaz"
        );

        batchRoots[batchId] = merkleRoot;

        emit BatchRootStored(
            batchId,
            merkleRoot
        );
    }

    function getBatchRoot(
        string calldata batchId
    )
        external
        view
        returns (bytes32)
    {
        return batchRoots[batchId];
    }
}