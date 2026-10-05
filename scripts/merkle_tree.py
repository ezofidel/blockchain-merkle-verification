import os
import json
import hashlib


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ORIGINAL_JSON_DIR = os.path.join(
    BASE_DIR,
    "orijinal_jsonlar"
)


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

    tree = [hashes]

    current_level = hashes

    while len(current_level) > 1:

        # Eleman sayısı tekse son hash'i kopyala
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


json_files = sorted(
    [
        file_name
        for file_name in os.listdir(ORIGINAL_JSON_DIR)
        if file_name.lower().endswith(".json")
    ]
)


print("Toplam JSON dosyası:", len(json_files))
print()


leaf_hashes = []

for file_name in json_files:

    file_path = os.path.join(
        ORIGINAL_JSON_DIR,
        file_name
    )

    file_hash = canonical_json_hash(
        file_path
    )

    leaf_hashes.append(
        file_hash
    )

    print(
        file_name,
        "->",
        file_hash
    )


print()
print("Merkle Tree oluşturuluyor...")


tree = build_merkle_tree(
    leaf_hashes
)


merkle_root = tree[-1][0]


print()
print("MERKLE ROOT:")
print(merkle_root)


print()
print("Merkle Tree seviye sayısı:", len(tree))