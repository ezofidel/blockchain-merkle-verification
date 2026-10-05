import os
import json
import csv
import copy
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


# ============================================================
# DOSYA YOLLARI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ORIGINAL_JSON_PATH = os.path.join(
    BASE_DIR,
    "orijinal_jsonlar",
    "00003.json"
)

PROVENANCE_PATH = os.path.join(
    BASE_DIR,
    "provenance_records",
    "00003_provenance.json"
)

SIGNATURE_PATH = os.path.join(
    BASE_DIR,
    "provenance_signatures",
    "00003_provenance.sig"
)

PUBLIC_KEY_PATH = os.path.join(
    BASE_DIR,
    "keys",
    "public_key.pem"
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
    "provenance_attack_results.csv"
)


# ============================================================
# ORIJINAL JSON HASH
# ============================================================

with open(
    ORIGINAL_JSON_PATH,
    "r",
    encoding="utf-8"
) as f:

    original_json = json.load(f)


canonical_json = json.dumps(
    original_json,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)


real_json_hash = hashlib.sha256(
    canonical_json.encode("utf-8")
).hexdigest()


# ============================================================
# ORIJINAL PROVENANCE
# ============================================================

with open(
    PROVENANCE_PATH,
    "r",
    encoding="utf-8"
) as f:

    original_provenance = json.load(f)


# ============================================================
# ORIJINAL IMZA
# ============================================================

with open(
    SIGNATURE_PATH,
    "rb"
) as f:

    original_signature = f.read()


# ============================================================
# PUBLIC KEY
# ============================================================

with open(
    PUBLIC_KEY_PATH,
    "rb"
) as f:

    public_key = serialization.load_pem_public_key(
        f.read()
    )


# ============================================================
# IMZA DOGRULAMA FONKSIYONU
# ============================================================

def verify_provenance_signature(
    provenance_data,
    signature
):

    canonical_provenance = json.dumps(
        provenance_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )

    provenance_hash = hashlib.sha256(
        canonical_provenance.encode("utf-8")
    ).digest()

    try:

        public_key.verify(
            signature,
            provenance_hash,
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
# TEK TEST FONKSIYONU
# ============================================================

results = []


def run_test(
    test_name,
    modified_provenance,
    changed_field,
    original_value,
    modified_value,
    expected_result
):

    signature_valid = (
        verify_provenance_signature(
            modified_provenance,
            original_signature
        )
    )

    json_hash_match = (
        modified_provenance[
            "json_hash"
        ]
        ==
        real_json_hash
    )

    accepted = (
        signature_valid
        and
        json_hash_match
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
        "Test":
            test_name,

        "Changed Field":
            changed_field,

        "Original Value":
            str(
                original_value
            ),

        "Modified Value":
            str(
                modified_value
            ),

        "JSON Hash Link":
            (
                "MATCH"
                if json_hash_match
                else
                "MISMATCH"
            ),

        "Provenance Signature":
            (
                "VALID"
                if signature_valid
                else
                "INVALID"
            ),

        "Final Result":
            final_result,

        "Expected Result":
            expected_result,

        "Test Passed":
            (
                "YES"
                if test_passed
                else
                "NO"
            )
    })


# ============================================================
# TEST 1 - NORMAL PROVENANCE
# ============================================================

run_test(
    test_name="Original Provenance",
    modified_provenance=copy.deepcopy(
        original_provenance
    ),
    changed_field="None",
    original_value="-",
    modified_value="-",
    expected_result="ACCEPTED"
)


# ============================================================
# TEST 2 - IMAGE ID DEGISTIR
# ============================================================

test_data = copy.deepcopy(
    original_provenance
)

original_value = test_data[
    "image_id"
]

test_data[
    "image_id"
] = "99999"


run_test(
    test_name="Modified Image ID",
    modified_provenance=test_data,
    changed_field="image_id",
    original_value=original_value,
    modified_value="99999",
    expected_result="REJECTED"
)


# ============================================================
# TEST 3 - MODEL DEGISTIR
# ============================================================

test_data = copy.deepcopy(
    original_provenance
)

original_value = test_data[
    "model"
]

test_data[
    "model"
] = "UNAUTHORIZED_MODEL"


run_test(
    test_name="Modified Model",
    modified_provenance=test_data,
    changed_field="model",
    original_value=original_value,
    modified_value="UNAUTHORIZED_MODEL",
    expected_result="REJECTED"
)


# ============================================================
# TEST 4 - MODEL VERSION DEGISTIR
# ============================================================

test_data = copy.deepcopy(
    original_provenance
)

original_value = test_data[
    "model_version"
]

test_data[
    "model_version"
] = "fake_version_1.0"


run_test(
    test_name="Modified Model Version",
    modified_provenance=test_data,
    changed_field="model_version",
    original_value=original_value,
    modified_value="fake_version_1.0",
    expected_result="REJECTED"
)


# ============================================================
# TEST 5 - TIMESTAMP DEGISTIR
# ============================================================

test_data = copy.deepcopy(
    original_provenance
)

original_value = test_data[
    "timestamp"
]

test_data[
    "timestamp"
] = "2030-01-01T00:00:00+00:00"


run_test(
    test_name="Modified Timestamp",
    modified_provenance=test_data,
    changed_field="timestamp",
    original_value=original_value,
    modified_value="2030-01-01T00:00:00+00:00",
    expected_result="REJECTED"
)


# ============================================================
# TEST 6 - BATCH ID DEGISTIR
# ============================================================

test_data = copy.deepcopy(
    original_provenance
)

original_value = test_data[
    "batch_id"
]

test_data[
    "batch_id"
] = "BATCH_ATTACK"


run_test(
    test_name="Modified Batch ID",
    modified_provenance=test_data,
    changed_field="batch_id",
    original_value=original_value,
    modified_value="BATCH_ATTACK",
    expected_result="REJECTED"
)


# ============================================================
# TEST 7 - JSON HASH DEGISTIR
# ============================================================

test_data = copy.deepcopy(
    original_provenance
)

original_value = test_data[
    "json_hash"
]

fake_hash = (
    "0" * 64
)

test_data[
    "json_hash"
] = fake_hash


run_test(
    test_name="Modified JSON Hash",
    modified_provenance=test_data,
    changed_field="json_hash",
    original_value=original_value,
    modified_value=fake_hash,
    expected_result="REJECTED"
)


# ============================================================
# CSV KAYDET
# ============================================================

fieldnames = [
    "Test",
    "Changed Field",
    "Original Value",
    "Modified Value",
    "JSON Hash Link",
    "Provenance Signature",
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
# EKRANA YAZ
# ============================================================

print()
print(
    "============================================================"
)

print(
    "             PROVENANCE ATTACK TEST RESULTS"
)

print(
    "============================================================"
)


for result in results:

    print()

    print(
        "TEST:",
        result["Test"]
    )

    print(
        "Changed Field         :",
        result["Changed Field"]
    )

    print(
        "JSON Hash Link        :",
        result["JSON Hash Link"]
    )

    print(
        "Provenance Signature  :",
        result["Provenance Signature"]
    )

    print(
        "Final Result          :",
        result["Final Result"]
    )

    print(
        "Expected Result       :",
        result["Expected Result"]
    )

    print(
        "TEST PASSED           :",
        result["Test Passed"]
    )

    print(
        "------------------------------------------------------------"
    )


successful_tests = sum(
    1

    for result
    in results

    if result[
        "Test Passed"
    ] == "YES"
)


print()
print(
    "============================================================"
)

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

print(
    "============================================================"
)