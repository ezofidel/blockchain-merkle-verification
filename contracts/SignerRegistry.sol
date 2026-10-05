// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SignerRegistry {

    address public owner;

    mapping(bytes32 => bool) private authorizedSigners;

    event SignerAuthorized(
        bytes32 indexed signerFingerprint
    );

    event SignerRevoked(
        bytes32 indexed signerFingerprint
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

    function authorizeSigner(
        bytes32 signerFingerprint
    )
        external
        onlyOwner
    {
        require(
            signerFingerprint != bytes32(0),
            "Fingerprint bos olamaz"
        );

        authorizedSigners[signerFingerprint] = true;

        emit SignerAuthorized(
            signerFingerprint
        );
    }

    function revokeSigner(
        bytes32 signerFingerprint
    )
        external
        onlyOwner
    {
        require(
            authorizedSigners[signerFingerprint],
            "Imzaci zaten yetkisiz"
        );

        authorizedSigners[signerFingerprint] = false;

        emit SignerRevoked(
            signerFingerprint
        );
    }

    function isSignerAuthorized(
        bytes32 signerFingerprint
    )
        external
        view
        returns (bool)
    {
        return authorizedSigners[
            signerFingerprint
        ];
    }
}