import json
import os
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

SIGNATURES_DIR = os.path.join(
    BASE_DIR,
    "signatures"
)

os.makedirs(SIGNATURES_DIR, exist_ok=True)


# JSON dosyasını oku
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)


# Canonical JSON oluştur
canonical_json = json.dumps(
    data,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)


# SHA-256 hash hesapla
json_hash = hashlib.sha256(
    canonical_json.encode("utf-8")
).digest()


print("JSON dosyası:", JSON_PATH)
print("SHA-256:", json_hash.hex())


# Private key'i yükle
with open(PRIVATE_KEY_PATH, "rb") as f:
    private_key = serialization.load_pem_private_key(
        f.read(),
        password=None
    )


# Hash'i dijital olarak imzala
signature = private_key.sign(
    json_hash,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)


# İmzayı kaydet
signature_path = os.path.join(
    SIGNATURES_DIR,
    "00003.sig"
)

with open(signature_path, "wb") as f:
    f.write(signature)


print("Dijital imza başarıyla oluşturuldu.")
print("İmza dosyası:", signature_path)