import os
import json
import csv
import hashlib

from web3 import Web3

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


# ============================================================
# AYARLAR
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ORIGINAL_JSON_DIR = os.path.join(
    BASE_DIR,
    "orijinal_jsonlar"
)

CONTROL_JSON_DIR = os.path.join(
    BASE_DIR,
    "kontrol_jsonlar"
)

RESULT_DIR = os.path.join(
    BASE_DIR,
    "sonuc"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


TARGET_FILE = "00003.json"

ORIGINAL_JSON_PATH = os.path.join(
    ORIGINAL_JSON_DIR,
    TARGET_FILE
)

CONTROL_JSON_PATH = os.path.join(
    CONTROL_JSON_DIR,
    TARGET_FILE
)


AUTHORIZED_PUBLIC_KEY_PATH = os.path.join(
    BASE_DIR,
    "keys",
    "public_key.pem"
)

AUTHORIZED_SIGNATURE_PATH = os.path.join(
    BASE_DIR,
    "signatures",
    "00003.sig"
)


ATTACKER_PRIVATE_KEY_PATH = os.path.join(
    BASE_DIR,
    "attacker_keys",
    "attacker_private_key.pem"
)

ATTACKER_PUBLIC_KEY_PATH = os.path.join(
    BASE_DIR,
    "attacker_keys",
    "attacker_public_key.pem"
)


CSV_PATH = os.path.join(
    RESULT_DIR,
    "security_test_results.csv"
)


BATCH_ID = "BATCH_001"

RPC_URL = "http://127.0.0.1:7545"

CONTRACT_ADDRESS = (
    "0x542b1D0b374265BE807C8637a95365e17b2F2992"
)


# ============================================================
# SMART CONTRACT ABI
# ============================================================

ABI = [
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "batchId",
                "type": "string"
            }
        ],
        "name": "getMerkleRoot",
        "outputs": [
            {
                "internalType": "bytes32",
                "name": "",
                "type": "bytes32"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]


# ============================================================
# JSON HASH
# ============================================================

def canonical_json_hash(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    canonical_json = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()


# ============================================================
# HASH PAIR
# ============================================================

def hash_pair(left_hash, right_hash):

    combined = (
        bytes.fromhex(left_hash)
        +
        bytes.fromhex(right_hash)
    )

    return hashlib.sha256(
        combined
    ).hexdigest()


# ============================================================
# MERKLE TREE
# ============================================================

def build_merkle_tree(hashes):

    if len(hashes) == 0:

        raise ValueError(
            "Merkle Tree icin en az bir hash gerekir."
        )

    tree = [hashes[:]]

    current_level = hashes[:]

    while len(current_level) > 1:

        if len(current_level) % 2 == 1:

            current_level = (
                current_level
                +
                [current_level[-1]]
            )

        next_level = []

        for i in range(
            0,
            len(current_level),
            2
        ):

            parent_hash = hash_pair(
                current_level[i],
                current_level[i + 1]
            )

            next_level.append(
                parent_hash
            )

        tree.append(
            next_level
        )

        current_level = next_level

    return tree


# ============================================================
# MERKLE PROOF
# ============================================================

def generate_merkle_proof(
    tree,
    leaf_index
):

    proof = []

    index = leaf_index

    for level in tree[:-1]:

        working_level = level[:]

        if len(working_level) % 2 == 1:

            working_level.append(
                working_level[-1]
            )

        if index % 2 == 0:

            sibling_index = index + 1
            position = "right"

        else:

            sibling_index = index - 1
            position = "left"

        proof.append({
            "position": position,
            "hash": working_level[sibling_index]
        })

        index = index // 2

    return proof


# ============================================================
# PROOF'TAN ROOT HESAPLA
# ============================================================

def calculate_root_from_proof(
    leaf_hash,
    proof
):

    current_hash = leaf_hash

    for item in proof:

        sibling_hash = item["hash"]

        if item["position"] == "left":

            current_hash = hash_pair(
                sibling_hash,
                current_hash
            )

        elif item["position"] == "right":

            current_hash = hash_pair(
                current_hash,
                sibling_hash
            )

        else:

            return None

    return current_hash


# ============================================================
# İMZA DOĞRULAMA
# ============================================================

def verify_signature(
    public_key,
    signature,
    json_hash
):

    try:

        public_key.verify(
            signature,
            bytes.fromhex(json_hash),
            padding.PSS(
                mgf=padding.MGF1(
                    hashes.SHA256()
                ),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return True

    except InvalidSignature:

        return False


# ============================================================
# TEST SONUÇLARI
# ============================================================

results = []


# ============================================================
# ANAHTARLARI YÜKLE
# ============================================================

with open(
    AUTHORIZED_PUBLIC_KEY_PATH,
    "rb"
) as f:

    authorized_public_key_bytes = f.read()


authorized_public_key = (
    serialization.load_pem_public_key(
        authorized_public_key_bytes
    )
)


with open(
    ATTACKER_PUBLIC_KEY_PATH,
    "rb"
) as f:

    attacker_public_key_bytes = f.read()


attacker_public_key = (
    serialization.load_pem_public_key(
        attacker_public_key_bytes
    )
)


with open(
    ATTACKER_PRIVATE_KEY_PATH,
    "rb"
) as f:

    attacker_private_key = (
        serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    )


with open(
    AUTHORIZED_SIGNATURE_PATH,
    "rb"
) as f:

    authorized_signature = f.read()


# ============================================================
# YETKİLİ ANAHTAR LİSTESİ
# ============================================================

authorized_fingerprint = hashlib.sha256(
    authorized_public_key_bytes
).hexdigest()


AUTHORIZED_SIGNERS = {
    authorized_fingerprint
}


def is_authorized(public_key_bytes):

    fingerprint = hashlib.sha256(
        public_key_bytes
    ).hexdigest()

    return fingerprint in AUTHORIZED_SIGNERS


# ============================================================
# ORİJİNAL VERİ SETİNDEN MERKLE TREE OLUŞTUR
# ============================================================

json_files = sorted(
    [
        file_name

        for file_name
        in os.listdir(
            ORIGINAL_JSON_DIR
        )

        if file_name.lower().endswith(
            ".json"
        )
    ]
)


leaf_hashes = []


for file_name in json_files:

    path = os.path.join(
        ORIGINAL_JSON_DIR,
        file_name
    )

    leaf_hashes.append(
        canonical_json_hash(
            path
        )
    )


tree = build_merkle_tree(
    leaf_hashes
)


local_merkle_root = tree[-1][0]


target_index = json_files.index(
    TARGET_FILE
)


original_hash = leaf_hashes[
    target_index
]


correct_proof = generate_merkle_proof(
    tree,
    target_index
)


# ============================================================
# BLOCKCHAIN ROOT
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


contract = web3.eth.contract(
    address=Web3.to_checksum_address(
        CONTRACT_ADDRESS
    ),
    abi=ABI
)


blockchain_root = (
    contract.functions
    .getMerkleRoot(
        BATCH_ID
    )
    .call()
    .hex()
)


# ============================================================
# GENEL TEST FONKSİYONU
# ============================================================

def run_test(
    test_name,
    json_path,
    signature,
    signer_public_key,
    signer_public_key_bytes,
    proof,
    expected_result
):

    current_hash = canonical_json_hash(
        json_path
    )


    # --------------------------------
    # JSON bütünlüğü
    # --------------------------------

    json_integrity = (
        current_hash
        ==
        original_hash
    )


    # --------------------------------
    # Dijital imza
    # --------------------------------

    signature_valid = verify_signature(
        signer_public_key,
        signature,
        current_hash
    )


    # --------------------------------
    # Yetkili imzalayan
    # --------------------------------

    signer_authorized = is_authorized(
        signer_public_key_bytes
    )


    # --------------------------------
    # Merkle Proof
    # --------------------------------

    calculated_root = (
        calculate_root_from_proof(
            current_hash,
            proof
        )
    )


    merkle_proof_valid = (
        calculated_root
        ==
        local_merkle_root
    )


    # --------------------------------
    # Blockchain
    # --------------------------------

    blockchain_match = (
        calculated_root is not None
        and
        calculated_root.lower()
        ==
        blockchain_root.lower()
    )


    # --------------------------------
    # Final karar
    # --------------------------------

    accepted = (
        json_integrity
        and
        signature_valid
        and
        signer_authorized
        and
        merkle_proof_valid
        and
        blockchain_match
    )


    final_result = (
        "ACCEPTED"
        if accepted
        else
        "REJECTED"
    )


    test_passed = (
        final_result
        ==
        expected_result
    )


    results.append({
        "Test": test_name,

        "JSON Integrity":
            "OK"
            if json_integrity
            else
            "FAILED",

        "Digital Signature":
            "VALID"
            if signature_valid
            else
            "INVALID",

        "Authorized Signer":
            "YES"
            if signer_authorized
            else
            "NO",

        "Merkle Proof":
            "VALID"
            if merkle_proof_valid
            else
            "INVALID",

        "Blockchain Root":
            "MATCH"
            if blockchain_match
            else
            "MISMATCH",

        "Final Result":
            final_result,

        "Expected Result":
            expected_result,

        "Test Passed":
            "YES"
            if test_passed
            else
            "NO"
    })


# ============================================================
# TEST 1
# NORMAL / ORİJİNAL VERİ
# ============================================================

run_test(
    test_name="Normal Verification",

    json_path=ORIGINAL_JSON_PATH,

    signature=authorized_signature,

    signer_public_key=authorized_public_key,

    signer_public_key_bytes=authorized_public_key_bytes,

    proof=correct_proof,

    expected_result="ACCEPTED"
)


# ============================================================
# TEST 2
# DEĞİŞTİRİLMİŞ JSON
# ============================================================

run_test(
    test_name="Modified JSON",

    json_path=CONTROL_JSON_PATH,

    signature=authorized_signature,

    signer_public_key=authorized_public_key,

    signer_public_key_bytes=authorized_public_key_bytes,

    proof=correct_proof,

    expected_result="REJECTED"
)


# ============================================================
# TEST 3
# GEÇERSİZ İMZA
# ============================================================

invalid_signature = bytearray(
    authorized_signature
)


invalid_signature[0] ^= 0x01


invalid_signature = bytes(
    invalid_signature
)


run_test(
    test_name="Invalid Signature",

    json_path=ORIGINAL_JSON_PATH,

    signature=invalid_signature,

    signer_public_key=authorized_public_key,

    signer_public_key_bytes=authorized_public_key_bytes,

    proof=correct_proof,

    expected_result="REJECTED"
)


# ============================================================
# TEST 4
# YETKİSİZ ANAHTAR
# ============================================================

attacker_signature = (
    attacker_private_key.sign(
        bytes.fromhex(
            original_hash
        ),
        padding.PSS(
            mgf=padding.MGF1(
                hashes.SHA256()
            ),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
)


run_test(
    test_name="Unauthorized Signer",

    json_path=ORIGINAL_JSON_PATH,

    signature=attacker_signature,

    signer_public_key=attacker_public_key,

    signer_public_key_bytes=attacker_public_key_bytes,

    proof=correct_proof,

    expected_result="REJECTED"
)


# ============================================================
# TEST 5
# HATALI MERKLE PROOF
# ============================================================

invalid_proof = []


for item in correct_proof:

    invalid_proof.append({
        "position": item["position"],
        "hash": item["hash"]
    })


invalid_proof[0]["hash"] = (
    "0" * 64
)


run_test(
    test_name="Invalid Merkle Proof",

    json_path=ORIGINAL_JSON_PATH,

    signature=authorized_signature,

    signer_public_key=authorized_public_key,

    signer_public_key_bytes=authorized_public_key_bytes,

    proof=invalid_proof,

    expected_result="REJECTED"
)


# ============================================================
# CSV KAYDET
# ============================================================

fieldnames = [
    "Test",
    "JSON Integrity",
    "Digital Signature",
    "Authorized Signer",
    "Merkle Proof",
    "Blockchain Root",
    "Final Result",
    "Expected Result",
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
# EKRANA SONUÇLARI YAZ
# ============================================================

print()
print("==============================================================")
print("                SECURITY TEST RESULTS")
print("==============================================================")
print()


for result in results:

    print(
        "TEST:",
        result["Test"]
    )

    print(
        "JSON Integrity       :",
        result["JSON Integrity"]
    )

    print(
        "Digital Signature    :",
        result["Digital Signature"]
    )

    print(
        "Authorized Signer    :",
        result["Authorized Signer"]
    )

    print(
        "Merkle Proof         :",
        result["Merkle Proof"]
    )

    print(
        "Blockchain Root      :",
        result["Blockchain Root"]
    )

    print(
        "Final Result         :",
        result["Final Result"]
    )

    print(
        "Expected Result      :",
        result["Expected Result"]
    )

    print(
        "TEST PASSED          :",
        result["Test Passed"]
    )

    print()
    print(
        "--------------------------------------------------------------"
    )
    print()


successful_tests = sum(
    1
    for result in results
    if result["Test Passed"] == "YES"
)


print()
print("==============================================================")

print(
    "BASARILI TEST SAYISI:",
    successful_tests,
    "/",
    len(results)
)

print(
    "CSV RAPORU:"
)

print(
    CSV_PATH
)

print("==============================================================")