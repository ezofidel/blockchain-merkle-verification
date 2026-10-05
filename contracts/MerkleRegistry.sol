// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MerkleRegistry {

    address public owner;

    mapping(string => bytes32) private merkleRoots;

    event MerkleRootStored(
        string batchId,
        bytes32 merkleRoot,
        address indexed storedBy
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

    function storeMerkleRoot(
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

        merkleRoots[batchId] = merkleRoot;

        emit MerkleRootStored(
            batchId,
            merkleRoot,
            msg.sender
        );
    }

    function getMerkleRoot(
        string calldata batchId
    )
        external
        view
        returns (bytes32)
    {
        return merkleRoots[batchId];
    }

    function verifyMerkleRoot(
        string calldata batchId,
        bytes32 merkleRoot
    )
        external
        view
        returns (bool)
    {
        return merkleRoots[batchId] == merkleRoot;
    }
}