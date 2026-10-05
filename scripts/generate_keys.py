from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS_DIR = os.path.join(BASE_DIR, "keys")

os.makedirs(KEYS_DIR, exist_ok=True)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key = private_key.public_key()

public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

private_path = os.path.join(KEYS_DIR, "private_key.pem")
public_path = os.path.join(KEYS_DIR, "public_key.pem")

with open(private_path, "wb") as f:
    f.write(private_pem)

with open(public_path, "wb") as f:
    f.write(public_pem)

print("Anahtarlar başarıyla oluşturuldu.")
print("Private key:", private_path)
print("Public key:", public_path)