import json
import os
import hashlib

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JSON_PATH = os.path.join(
    BASE_DIR,
    "kontrol_jsonlar",
    "00003.json"
)

PUBLIC_KEY_PATH = os.path.join(
    BASE_DIR,
    "keys",
    "public_key.pem"
)

SIGNATURE_PATH = os.path.join(
    BASE_DIR,
    "signatures",
    "00003.sig"
)


# Kontrol JSON dosyasını oku
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


print("Kontrol edilen JSON:", JSON_PATH)
print("SHA-256:", json_hash.hex())


# Public key'i yükle
with open(PUBLIC_KEY_PATH, "rb") as f:
    public_key = serialization.load_pem_public_key(
        f.read()
    )


# Orijinal imza dosyasını oku
with open(SIGNATURE_PATH, "rb") as f:
    signature = f.read()


# Dijital imzayı doğrula
try:
    public_key.verify(
        signature,
        json_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    print("DİJİTAL İMZA GEÇERLİ.")
    print("Dosyada değişiklik tespit edilmedi.")

except InvalidSignature:
    print("DİJİTAL İMZA GEÇERSİZ.")
    print("UYARI: Dosya değiştirilmiş veya imza bu dosyaya ait değil.")