// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BenchmarkRegistry {

    address public owner;

    mapping(string => bytes32) private individualHashes;
    mapping(string => bytes32) private merkleRoots;

    event IndividualHashStored(
        string recordId,
        bytes32 dataHash
    );

    event MerkleRootStored(
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

    function storeIndividualHash(
        string calldata recordId,
        bytes32 dataHash
    )
        external
        onlyOwner
    {
        require(
            dataHash != bytes32(0),
            "Hash bos olamaz"
        );

        individualHashes[recordId] = dataHash;

        emit IndividualHashStored(
            recordId,
            dataHash
        );
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
            merkleRoot
        );
    }

    function getIndividualHash(
        string calldata recordId
    )
        external
        view
        returns (bytes32)
    {
        return individualHashes[recordId];
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
}