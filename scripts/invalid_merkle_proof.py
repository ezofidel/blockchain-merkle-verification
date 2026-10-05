import os
import json
import hashlib


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ORIGINAL_JSON_DIR = os.path.join(
    BASE_DIR,
    "orijinal_jsonlar"
)

TARGET_FILE = "00003.json"


def canonical_json_hash(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
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


def hash_pair(left_hash, right_hash):
    combined = bytes.fromhex(left_hash) + bytes.fromhex(right_hash)

    return hashlib.sha256(
        combined
    ).hexdigest()


def build_merkle_tree(hashes):
    if len(hashes) == 0:
        raise ValueError("Merkle Tree oluşturmak için en az bir hash gerekir.")

    tree = [hashes[:]]
    current_level = hashes[:]

    while len(current_level) > 1:

        if len(current_level) % 2 == 1:
            current_level = current_level + [current_level[-1]]

        next_level = []

        for i in range(0, len(current_level), 2):

            parent_hash = hash_pair(
                current_level[i],
                current_level[i + 1]
            )

            next_level.append(parent_hash)

        tree.append(next_level)
        current_level = next_level

    return tree


def generate_merkle_proof(tree, leaf_index):
    proof = []
    index = leaf_index

    for level in tree[:-1]:

        if len(level) % 2 == 1:
            level = level + [level[-1]]

        if index % 2 == 0:
            sibling_index = index + 1
            sibling_position = "right"
        else:
            sibling_index = index - 1
            sibling_position = "left"

        sibling_hash = level[sibling_index]

        proof.append({
            "position": sibling_position,
            "hash": sibling_hash
        })

        index = index // 2

    return proof


def verify_merkle_proof(leaf_hash, proof, expected_root):
    current_hash = leaf_hash

    for item in proof:

        sibling_hash = item["hash"]
        position = item["position"]

        if position == "left":
            current_hash = hash_pair(
                sibling_hash,
                current_hash
            )

        elif position == "right":
            current_hash = hash_pair(
                current_hash,
                sibling_hash
            )

        else:
            return False

    return current_hash == expected_root


json_files = sorted(
    [
        file_name
        for file_name in os.listdir(ORIGINAL_JSON_DIR)
        if file_name.lower().endswith(".json")
    ]
)


if TARGET_FILE not in json_files:
    raise FileNotFoundError(
        f"{TARGET_FILE} orijinal_jsonlar klasöründe bulunamadı."
    )


leaf_hashes = []

for file_name in json_files:

    file_path = os.path.join(
        ORIGINAL_JSON_DIR,
        file_name
    )

    file_hash = canonical_json_hash(
        file_path
    )

    leaf_hashes.append(file_hash)


tree = build_merkle_tree(
    leaf_hashes
)


merkle_root = tree[-1][0]


target_index = json_files.index(
    TARGET_FILE
)


target_hash = leaf_hashes[
    target_index
]


proof = generate_merkle_proof(
    tree,
    target_index
)


print("HEDEF DOSYA:")
print(TARGET_FILE)

print()

print("ORİJİNAL MERKLE ROOT:")
print(merkle_root)

print()

print("ORİJİNAL PROOF İLE KONTROL:")

original_result = verify_merkle_proof(
    target_hash,
    proof,
    merkle_root
)

if original_result:
    print("MERKLE PROOF GEÇERLİ.")
else:
    print("MERKLE PROOF GEÇERSİZ.")


print()
print("------------------------------------")
print("HATALI MERKLE PROOF OLUŞTURULUYOR")
print("------------------------------------")
print()


# Proof'un bir kopyasını oluştur
fake_proof = []

for item in proof:
    fake_proof.append({
        "position": item["position"],
        "hash": item["hash"]
    })


# İlk proof elemanının hash'ini kasıtlı olarak değiştir
original_proof_hash = fake_proof[0]["hash"]

fake_hash = (
    "0" * 64
)

fake_proof[0]["hash"] = fake_hash


print("Orijinal ilk proof hash:")
print(original_proof_hash)

print()

print("Değiştirilmiş ilk proof hash:")
print(fake_hash)

print()


# Hatalı proof'u doğrula
fake_result = verify_merkle_proof(
    target_hash,
    fake_proof,
    merkle_root
)


if fake_result:

    print("HATA:")
    print("Bozuk Merkle Proof yanlışlıkla geçerli kabul edildi.")

else:

    print("MERKLE PROOF GEÇERSİZ.")
    print("HATALI MERKLE PROOF TESPİT EDİLDİ.")
    print("SONUÇ: DOSYA REDDEDİLDİ.")