import os
import csv
import hashlib

from web3 import Web3


# ============================================================
# AYARLAR
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

AUTHORIZED_PUBLIC_KEY_PATH = os.path.join(
    BASE_DIR,
    "keys",
    "public_key.pem"
)

ATTACKER_PUBLIC_KEY_PATH = os.path.join(
    BASE_DIR,
    "attacker_keys",
    "attacker_public_key.pem"
)

RESULT_DIR = os.path.join(
    BASE_DIR,
    "sonuc"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)

CSV_PATH = os.path.join(
    RESULT_DIR,
    "signer_lifecycle_results.csv"
)

RPC_URL = "http://127.0.0.1:7545"

CONTRACT_ADDRESS = (
    "0xFd9B08BE8CD2BeFb960191c6d41c183ef6A6e0D8"
)


# ============================================================
# ABI
# ============================================================

ABI = [
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "signerFingerprint",
                "type": "bytes32"
            }
        ],
        "name": "authorizeSigner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "signerFingerprint",
                "type": "bytes32"
            }
        ],
        "name": "revokeSigner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes32",
                "name": "signerFingerprint",
                "type": "bytes32"
            }
        ],
        "name": "isSignerAuthorized",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


# ============================================================
# PUBLIC KEY FINGERPRINT
# ============================================================

def get_fingerprint(file_path):

    with open(
        file_path,
        "rb"
    ) as f:

        public_key_bytes = f.read()

    fingerprint_hex = hashlib.sha256(
        public_key_bytes
    ).hexdigest()

    return (
        fingerprint_hex,
        bytes.fromhex(
            fingerprint_hex
        )
    )


authorized_hex, authorized_bytes = (
    get_fingerprint(
        AUTHORIZED_PUBLIC_KEY_PATH
    )
)

attacker_hex, attacker_bytes = (
    get_fingerprint(
        ATTACKER_PUBLIC_KEY_PATH
    )
)


# ============================================================
# GANACHE BAGLANTISI
# ============================================================

web3 = Web3(
    Web3.HTTPProvider(
        RPC_URL
    )
)

if not web3.is_connected():

    print(
        "GANACHE BAGLANTISI BASARISIZ."
    )

    raise SystemExit


print()
print(
    "GANACHE BAGLANTISI BASARILI."
)


sender_account = web3.eth.accounts[0]


contract = web3.eth.contract(
    address=Web3.to_checksum_address(
        CONTRACT_ADDRESS
    ),
    abi=ABI
)


results = []


# ============================================================
# TEST 1
# YETKILI SIGNER
# ============================================================

print()
print(
    "=============================================="
)

print(
    "TEST 1 - YETKILI SIGNER"
)

print(
    "=============================================="
)


authorized_status = (
    contract.functions
    .isSignerAuthorized(
        authorized_bytes
    )
    .call()
)


print(
    "Yetki durumu:",
    authorized_status
)


test1_result = (
    "ACCEPTED"
    if authorized_status
    else
    "REJECTED"
)


results.append({
    "Test":
        "Authorized Signer",

    "Signer":
        "Main Authorized Key",

    "Blockchain Authorization":
        str(
            authorized_status
        ),

    "Expected Result":
        "ACCEPTED",

    "Final Result":
        test1_result,

    "Test Passed":
        (
            "YES"
            if test1_result == "ACCEPTED"
            else
            "NO"
        )
})


# ============================================================
# TEST 2
# HIC YETKILENDIRILMEMIS SALDIRGAN
# ============================================================

print()
print(
    "=============================================="
)

print(
    "TEST 2 - UNAUTHORIZED ATTACKER"
)

print(
    "=============================================="
)


attacker_status = (
    contract.functions
    .isSignerAuthorized(
        attacker_bytes
    )
    .call()
)


print(
    "Attacker yetki durumu:",
    attacker_status
)


test2_result = (
    "ACCEPTED"
    if attacker_status
    else
    "REJECTED"
)


results.append({
    "Test":
        "Never Authorized Attacker",

    "Signer":
        "Attacker Key",

    "Blockchain Authorization":
        str(
            attacker_status
        ),

    "Expected Result":
        "REJECTED",

    "Final Result":
        test2_result,

    "Test Passed":
        (
            "YES"
            if test2_result == "REJECTED"
            else
            "NO"
        )
})


# ============================================================
# TEST 3
# YETKILI SIGNER'IN YETKISINI KALDIR
# ============================================================

print()
print(
    "=============================================="
)

print(
    "TEST 3 - REVOKED SIGNER"
)

print(
    "=============================================="
)


tx_hash = (
    contract.functions
    .revokeSigner(
        authorized_bytes
    )
    .transact({
        "from": sender_account
    })
)


receipt = (
    web3.eth
    .wait_for_transaction_receipt(
        tx_hash
    )
)


print(
    "Revoke transaction tamamlandi."
)

print(
    "Gas Used:",
    receipt.gasUsed
)


revoked_status = (
    contract.functions
    .isSignerAuthorized(
        authorized_bytes
    )
    .call()
)


print(
    "Revoke sonrasi yetki durumu:",
    revoked_status
)


test3_result = (
    "ACCEPTED"
    if revoked_status
    else
    "REJECTED"
)


results.append({
    "Test":
        "Revoked Signer",

    "Signer":
        "Previously Authorized Key",

    "Blockchain Authorization":
        str(
            revoked_status
        ),

    "Expected Result":
        "REJECTED",

    "Final Result":
        test3_result,

    "Test Passed":
        (
            "YES"
            if test3_result == "REJECTED"
            else
            "NO"
        )
})


# ============================================================
# SISTEMI ESKI HALINE GETIR
# MAIN SIGNER'I TEKRAR YETKILENDIR
# ============================================================

print()
print(
    "=============================================="
)

print(
    "SISTEM DURUMU GERI YUKLENIYOR"
)

print(
    "=============================================="
)


tx_hash = (
    contract.functions
    .authorizeSigner(
        authorized_bytes
    )
    .transact({
        "from": sender_account
    })
)


receipt = (
    web3.eth
    .wait_for_transaction_receipt(
        tx_hash
    )
)


restored_status = (
    contract.functions
    .isSignerAuthorized(
        authorized_bytes
    )
    .call()
)


print(
    "Ana signer tekrar yetkilendirildi."
)

print(
    "Yetki durumu:",
    restored_status
)


# ============================================================
# CSV
# ============================================================

fieldnames = [
    "Test",
    "Signer",
    "Blockchain Authorization",
    "Expected Result",
    "Final Result",
    "Test Passed"
]


with open(
    CSV_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=fieldnames,
        delimiter=";"
    )

    writer.writeheader()

    writer.writerows(
        results
    )


# ============================================================
# SONUC
# ============================================================

successful_tests = sum(
    1

    for result in results

    if result[
        "Test Passed"
    ] == "YES"
)


print()
print(
    "=============================================="
)

print(
    "SIGNER LIFECYCLE TEST RESULTS"
)

print(
    "=============================================="
)


for result in results:

    print()

    print(
        "Test                 :",
        result["Test"]
    )

    print(
        "Blockchain Authority :",
        result[
            "Blockchain Authorization"
        ]
    )

    print(
        "Expected             :",
        result[
            "Expected Result"
        ]
    )

    print(
        "Result               :",
        result[
            "Final Result"
        ]
    )

    print(
        "TEST PASSED          :",
        result[
            "Test Passed"
        ]
    )


print()
print(
    "BASARILI TEST SAYISI:",
    successful_tests,
    "/",
    len(results)
)

print()

print(
    "CSV RAPORU:"
)

print(
    CSV_PATH
)

print()
print(
    "MAIN SIGNER RESTORED:",
    restored_status
)

print(
    "=============================================="
)