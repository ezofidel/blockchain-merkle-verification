import os
import json
import hashlib
from datetime import datetime, timezone

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


# ============================================================
# DOSYA YOLLARI
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

JSON_PATH = os.path.join(
    BASE_DIR,
    "orijinal_jsonlar",
    "00003.json"
)

PRIVATE_KEY_PATH = os.path.join(
    BASE_DIR,
    "keys",
    "private_key.pem"
)

PROVENANCE_DIR = os.path.join(
    BASE_DIR,
    "provenance_records"
)

SIGNATURE_DIR = os.path.join(
    BASE_DIR,
    "provenance_signatures"
)

os.makedirs(
    PROVENANCE_DIR,
    exist_ok=True
)

os.makedirs(
    SIGNATURE_DIR,
    exist_ok=True
)


# ============================================================
# ORIJINAL JSON HASH
# ============================================================

with open(
    JSON_PATH,
    "r",
    encoding="utf-8"
) as f:

    json_data = json.load(f)


canonical_json = json.dumps(
    json_data,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)


json_hash = hashlib.sha256(
    canonical_json.encode("utf-8")
).hexdigest()


# ============================================================
# PROVENANCE KAYDI
# ============================================================

provenance = {
    "image_id": "00003",
    "model": "YOLO",
    "model_version": "unknown",
    "timestamp": datetime.now(
        timezone.utc
    ).isoformat(),
    "batch_id": "BATCH_001",
    "json_hash": json_hash
}


# ============================================================
# PROVENANCE JSON KAYDET
# ============================================================

provenance_path = os.path.join(
    PROVENANCE_DIR,
    "00003_provenance.json"
)


with open(
    provenance_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        provenance,
        f,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# PROVENANCE VERISINI CANONICAL HALE GETIR
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
# PRIVATE KEY YUKLE
# ============================================================

with open(
    PRIVATE_KEY_PATH,
    "rb"
) as f:

    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


# ============================================================
# PROVENANCE HASH'INI IMZALA
# ============================================================

signature = private_key.sign(
    provenance_hash,
    padding.PSS(
        mgf=padding.MGF1(
            hashes.SHA256()
        ),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)


# ============================================================
# IMZAYI KAYDET
# ============================================================

signature_path = os.path.join(
    SIGNATURE_DIR,
    "00003_provenance.sig"
)


with open(
    signature_path,
    "wb"
) as f:

    f.write(signature)


# ============================================================
# SONUC
# ============================================================

print()
print("PROVENANCE KAYDI OLUSTURULDU.")
print()

print("Image ID        :", provenance["image_id"])
print("Model           :", provenance["model"])
print("Model Version   :", provenance["model_version"])
print("Timestamp       :", provenance["timestamp"])
print("Batch ID        :", provenance["batch_id"])
print("JSON Hash       :", provenance["json_hash"])

print()
print("Provenance dosyasi:")
print(provenance_path)

print()
print("Dijital imza:")
print(signature_path)

print()
print("PROVENANCE VERISI BASARIYLA IMZALANDI.")