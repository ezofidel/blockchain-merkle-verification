import os
import json
import csv
import time
import hashlib
import random
import statistics


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

RESULT_DIR = os.path.join(
    BASE_DIR,
    "sonuc"
)

os.makedirs(
    RESULT_DIR,
    exist_ok=True
)


RAW_CSV_PATH = os.path.join(
    RESULT_DIR,
    "merkle_scalability_raw.csv"
)

SUMMARY_CSV_PATH = os.path.join(
    RESULT_DIR,
    "merkle_scalability_summary.csv"
)


TEST_SIZES = [
    100,
    1000,
    2229
]


# Her veri boyutu için 5 tekrar
REPEAT_COUNT = 5


# Her tekrarda 10 farklı rastgele JSON proof'u
RANDOM_PROOFS_PER_REPEAT = 10


# Deneylerin tekrarlanabilir olması için
RANDOM_SEED = 42

random.seed(
    RANDOM_SEED
)


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

    tree = [
        hashes[:]
    ]

    current_level = hashes[:]

    while len(current_level) > 1:

        working_level = current_level[:]

        # Tek sayida eleman varsa
        # son elemani kopyala
        if len(working_level) % 2 == 1:

            working_level.append(
                working_level[-1]
            )

        next_level = []

        for i in range(
            0,
            len(working_level),
            2
        ):

            parent_hash = hash_pair(
                working_level[i],
                working_level[i + 1]
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
# MERKLE PROOF OLUSTUR
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
            sibling_position = "right"

        else:

            sibling_index = index - 1
            sibling_position = "left"

        sibling_hash = working_level[
            sibling_index
        ]

        proof.append({
            "position": sibling_position,
            "hash": sibling_hash
        })

        index = index // 2

    return proof


# ============================================================
# MERKLE PROOF DOGRULA
# ============================================================

def verify_merkle_proof(
    leaf_hash,
    proof,
    expected_root
):

    current_hash = leaf_hash

    for item in proof:

        sibling_hash = item[
            "hash"
        ]

        position = item[
            "position"
        ]

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

    return (
        current_hash
        ==
        expected_root
    )


# ============================================================
# JSON DOSYALARINI BUL
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


total_json_count = len(
    json_files
)


print()
print(
    "Toplam JSON dosyasi:",
    total_json_count
)


if total_json_count < max(
    TEST_SIZES
):

    raise ValueError(
        "Test icin yeterli JSON bulunamadi."
    )


# ============================================================
# HASHLERI ONCEDEN HESAPLA
# ============================================================

print()
print(
    "Tum JSON hashleri hesaplaniyor..."
)


all_hashes = []


hash_start = time.perf_counter()


for file_name in json_files:

    file_path = os.path.join(
        ORIGINAL_JSON_DIR,
        file_name
    )

    all_hashes.append(
        canonical_json_hash(
            file_path
        )
    )


hash_end = time.perf_counter()


print(
    "Hash hesaplama tamamlandi."
)

print(
    "Toplam hash hesaplama suresi:",
    round(
        hash_end - hash_start,
        6
    ),
    "s"
)


# ============================================================
# RAW SONUCLAR
# ============================================================

raw_results = []


# ============================================================
# TESTLER
# ============================================================

for n in TEST_SIZES:

    print()
    print(
        "===================================================="
    )

    print(
        "TEST BOYUTU:",
        n
    )

    print(
        "===================================================="
    )


    selected_files = json_files[
        :n
    ]

    selected_hashes = all_hashes[
        :n
    ]


    for repeat in range(
        1,
        REPEAT_COUNT + 1
    ):

        print()
        print(
            "Tekrar:",
            repeat,
            "/",
            REPEAT_COUNT
        )


        # ====================================================
        # MERKLE TREE OLUSTURMA SURESI
        # ====================================================

        tree_start = (
            time.perf_counter_ns()
        )


        tree = build_merkle_tree(
            selected_hashes
        )


        tree_end = (
            time.perf_counter_ns()
        )


        tree_time_ns = (
            tree_end
            -
            tree_start
        )


        tree_time_ms = (
            tree_time_ns
            /
            1_000_000
        )


        merkle_root = tree[-1][0]


        print(
            "Merkle Tree suresi:",
            round(
                tree_time_ms,
                6
            ),
            "ms"
        )


        # ====================================================
        # 10 RASTGELE JSON SEC
        # ====================================================

        random_indices = random.sample(
            range(
                n
            ),
            RANDOM_PROOFS_PER_REPEAT
        )


        for sample_number, target_index in enumerate(
            random_indices,
            start=1
        ):

            target_file = (
                selected_files[
                    target_index
                ]
            )

            target_hash = (
                selected_hashes[
                    target_index
                ]
            )


            # ================================================
            # PROOF OLUSTURMA SURESI
            # ================================================

            proof_start = (
                time.perf_counter_ns()
            )


            proof = generate_merkle_proof(
                tree,
                target_index
            )


            proof_end = (
                time.perf_counter_ns()
            )


            proof_generation_ns = (
                proof_end
                -
                proof_start
            )


            proof_generation_us = (
                proof_generation_ns
                /
                1000
            )


            # ================================================
            # PROOF DOGRULAMA SURESI
            # ================================================

            verification_start = (
                time.perf_counter_ns()
            )


            is_valid = verify_merkle_proof(
                target_hash,
                proof,
                merkle_root
            )


            verification_end = (
                time.perf_counter_ns()
            )


            verification_ns = (
                verification_end
                -
                verification_start
            )


            verification_us = (
                verification_ns
                /
                1000
            )


            # ================================================
            # PROOF UZUNLUGU
            # ================================================

            proof_length = len(
                proof
            )


            raw_results.append({
                "JSON Count":
                    n,

                "Repeat":
                    repeat,

                "Sample":
                    sample_number,

                "Target Index":
                    target_index,

                "Target File":
                    target_file,

                "Tree Build Time (ms)":
                    tree_time_ms,

                "Proof Generation Time (us)":
                    proof_generation_us,

                "Proof Verification Time (us)":
                    verification_us,

                "Proof Length":
                    proof_length,

                "Verification Result":
                    (
                        "VALID"
                        if is_valid
                        else
                        "INVALID"
                    )
            })


            print(
                "  JSON:",
                target_file,
                "| Proof Length:",
                proof_length,
                "| Generate:",
                round(
                    proof_generation_us,
                    3
                ),
                "us",
                "| Verify:",
                round(
                    verification_us,
                    3
                ),
                "us",
                "|",
                "VALID"
                if is_valid
                else
                "INVALID"
            )


# ============================================================
# RAW CSV
# ============================================================

raw_fieldnames = [
    "JSON Count",
    "Repeat",
    "Sample",
    "Target Index",
    "Target File",
    "Tree Build Time (ms)",
    "Proof Generation Time (us)",
    "Proof Verification Time (us)",
    "Proof Length",
    "Verification Result"
]


with open(
    RAW_CSV_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=raw_fieldnames,
        delimiter=";"
    )

    writer.writeheader()

    writer.writerows(
        raw_results
    )


# ============================================================
# SUMMARY
# ============================================================

summary_results = []


for n in TEST_SIZES:

    subset = [
        result

        for result
        in raw_results

        if result[
            "JSON Count"
        ] == n
    ]


    # Tree süresi her tekrarda
    # 10 defa raw CSV'ye yazildi.
    # Her tekrar icin tek degeri aliyoruz.
    tree_times = []


    for repeat in range(
        1,
        REPEAT_COUNT + 1
    ):

        repeat_subset = [
            x

            for x
            in subset

            if x[
                "Repeat"
            ] == repeat
        ]

        tree_times.append(
            repeat_subset[0][
                "Tree Build Time (ms)"
            ]
        )


    proof_generation_times = [
        x[
            "Proof Generation Time (us)"
        ]

        for x
        in subset
    ]


    proof_verification_times = [
        x[
            "Proof Verification Time (us)"
        ]

        for x
        in subset
    ]


    proof_lengths = [
        x[
            "Proof Length"
        ]

        for x
        in subset
    ]


    valid_count = sum(
        1

        for x
        in subset

        if x[
            "Verification Result"
        ] == "VALID"
    )


    summary_results.append({
        "JSON Count":
            n,

        "Tree Repeat Count":
            REPEAT_COUNT,

        "Random Proof Count":
            len(
                subset
            ),

        "Tree Build Mean (ms)":
            round(
                statistics.mean(
                    tree_times
                ),
                6
            ),

        "Tree Build Std (ms)":
            round(
                statistics.stdev(
                    tree_times
                ),
                6
            ),

        "Proof Generation Mean (us)":
            round(
                statistics.mean(
                    proof_generation_times
                ),
                6
            ),

        "Proof Generation Std (us)":
            round(
                statistics.stdev(
                    proof_generation_times
                ),
                6
            ),

        "Proof Verification Mean (us)":
            round(
                statistics.mean(
                    proof_verification_times
                ),
                6
            ),

        "Proof Verification Std (us)":
            round(
                statistics.stdev(
                    proof_verification_times
                ),
                6
            ),

        "Proof Length Mean":
            round(
                statistics.mean(
                    proof_lengths
                ),
                2
            ),

        "Proof Length Min":
            min(
                proof_lengths
            ),

        "Proof Length Max":
            max(
                proof_lengths
            ),

        "Valid Proof Count":
            valid_count,

        "Total Proof Count":
            len(
                subset
            )
    })


# ============================================================
# SUMMARY CSV
# ============================================================

summary_fieldnames = [
    "JSON Count",
    "Tree Repeat Count",
    "Random Proof Count",
    "Tree Build Mean (ms)",
    "Tree Build Std (ms)",
    "Proof Generation Mean (us)",
    "Proof Generation Std (us)",
    "Proof Verification Mean (us)",
    "Proof Verification Std (us)",
    "Proof Length Mean",
    "Proof Length Min",
    "Proof Length Max",
    "Valid Proof Count",
    "Total Proof Count"
]


with open(
    SUMMARY_CSV_PATH,
    "w",
    newline="",
    encoding="utf-8-sig"
) as csv_file:

    writer = csv.DictWriter(
        csv_file,
        fieldnames=summary_fieldnames,
        delimiter=";"
    )

    writer.writeheader()

    writer.writerows(
        summary_results
    )


# ============================================================
# EKRANA OZET YAZ
# ============================================================

print()
print(
    "===================================================="
)

print(
    "MERKLE OLCEKLENEBILIRLIK TESTI TAMAMLANDI"
)

print(
    "===================================================="
)


for result in summary_results:

    print()

    print(
        "JSON SAYISI:",
        result[
            "JSON Count"
        ]
    )

    print(
        "Tree Build:",
        result[
            "Tree Build Mean (ms)"
        ],
        "+/-",
        result[
            "Tree Build Std (ms)"
        ],
        "ms"
    )

    print(
        "Proof Generation:",
        result[
            "Proof Generation Mean (us)"
        ],
        "+/-",
        result[
            "Proof Generation Std (us)"
        ],
        "us"
    )

    print(
        "Proof Verification:",
        result[
            "Proof Verification Mean (us)"
        ],
        "+/-",
        result[
            "Proof Verification Std (us)"
        ],
        "us"
    )

    print(
        "Proof Length:",
        result[
            "Proof Length Mean"
        ]
    )

    print(
        "Valid Proof:",
        result[
            "Valid Proof Count"
        ],
        "/",
        result[
            "Total Proof Count"
        ]
    )


print()
print(
    "RAW CSV:"
)

print(
    RAW_CSV_PATH
)


print()
print(
    "SUMMARY CSV:"
)

print(
    SUMMARY_CSV_PATH
)

print(
    "===================================================="
)