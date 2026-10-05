import os
import json
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


# ============================================================
# 1. PROVENANCE KAYDINI OKU
# ============================================================

with open(
    PROVENANCE_PATH,
    "r",
    encoding="utf-8"
) as f:

    provenance = json.load(f)


print()
print("==============================================")
print("        PROVENANCE DOGRULAMA SISTEMI")
print("==============================================")
print()

print("Image ID       :", provenance["image_id"])
print("Model          :", provenance["model"])
print("Model Version  :", provenance["model_version"])
print("Timestamp      :", provenance["timestamp"])
print("Batch ID       :", provenance["batch_id"])


# ============================================================
# 2. ORIJINAL JSON HASH'INI TEKRAR HESAPLA
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


calculated_json_hash = hashlib.sha256(
    canonical_json.encode("utf-8")
).hexdigest()


stored_json_hash = provenance[
    "json_hash"
]


json_hash_match = (
    calculated_json_hash
    ==
    stored_json_hash
)


print()
print("----------------------------------------------")
print("JSON HASH BAGLANTISI")
print("----------------------------------------------")

print(
    "Provenance JSON Hash :",
    stored_json_hash
)

print(
    "Hesaplanan JSON Hash :",
    calculated_json_hash
)


if json_hash_match:

    print("JSON HASH LINK        : MATCH")

else:

    print("JSON HASH LINK        : MISMATCH")


# ============================================================
# 3. PROVENANCE VERISINI CANONICAL HALE GETIR
# ============================================================

canonical_provenance = json.dumps(
    provenance,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)


provenance_hash = hashlib.sha256(
    canonical_provenance.encode("utf-8")
).digest()


# ============================================================
# 4. PUBLIC KEY'I YUKLE
# ============================================================

with open(
    PUBLIC_KEY_PATH,
    "rb"
) as f:

    public_key = serialization.load_pem_public_key(
        f.read()
    )


# ============================================================
# 5. DIJITAL IMZAYI OKU
# ============================================================

with open(
    SIGNATURE_PATH,
    "rb"
) as f:

    signature = f.read()


# ============================================================
# 6. PROVENANCE IMZASINI DOGRULA
# ============================================================

signature_valid = False


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

    signature_valid = True

except InvalidSignature:

    signature_valid = False


print()
print("----------------------------------------------")
print("PROVENANCE IMZA KONTROLU")
print("----------------------------------------------")


if signature_valid:

    print("PROVENANCE SIGNATURE  : VALID")

else:

    print("PROVENANCE SIGNATURE  : INVALID")


# ============================================================
# 7. FINAL RESULT
# ============================================================

print()
print("==============================================")
print("                 FINAL RESULT")
print("==============================================")


if (
    json_hash_match
    and
    signature_valid
):

    print("RESULT                : ACCEPTED")
    print()
    print(
        "Veri ile provenance kaydi uyumludur."
    )

    print(
        "Provenance kaydi yetkili private key ile imzalanmistir."
    )

else:

    print("RESULT                : REJECTED")

    print()
    print(
        "Provenance veya veri butunlugu dogrulanamadi."
    )


print()
print("==============================================")