import os
import json
import csv
import time
import math
import hashlib
import statistics

from web3 import Web3


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
    "batch_size_benchmark_raw.csv"
)

SUMMARY_CSV_PATH = os.path.join(
    RESULT_DIR,
    "batch_size_benchmark_summary.csv"
)


RPC_URL = "http://127.0.0.1:7545"

CONTRACT_ADDRESS = (
    "0xeFD6a024FfAF50C094C8e4a43B93c85B0c2bE4e0"
)


# Hocanin istedigi batch buyuklukleri
BATCH_SIZES = [
    10,
    50,
    100,
    500,
    2229
]


# Her deney 5 kez tekrarlanacak
REPEAT_COUNT = 5


# ============================================================
# CONTRACT ABI
# ============================================================

ABI = [
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "batchId",
                "type": "string"
            },
            {
                "internalType": "bytes32",
                "name": "merkleRoot",
                "type": "bytes32"
            }
        ],
        "name": "storeBatchRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
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
# IKI HASH'I BIRLESTIR
# ============================================================

def hash_pair(
    left_hash,
    right_hash
):

    combined = (
        bytes.fromhex(left_hash)
        +
        bytes.fromhex(right_hash)
    )

    return hashlib.sha256(
        combined
    ).hexdigest()


# ============================================================
# TEK BATCH ICIN MERKLE ROOT
# ============================================================

def build_merkle_root(hashes):

    if len(hashes) == 0:

        raise ValueError(
            "Merkle Root icin en az bir hash gerekir."
        )

    current_level = hashes[:]

    while len(current_level) > 1:

        working_level = current_level[:]

        # Tek sayida hash varsa
        # son hash'i kopyala
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

            next_level.append(
                hash_pair(
                    working_level[i],
                    working_level[i + 1]
                )
            )

        current_level = next_level

    return current_level[0]


# ============================================================
# GANACHE BAGLANTISI
# ============================================================

print()
print(
    "Ganache baglantisi kontrol ediliyor..."
)


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


print(
    "GANACHE BAGLANTISI BASARILI."
)


accounts = web3.eth.accounts


if len(accounts) == 0:

    print(
        "Ganache hesabi bulunamadi."
    )

    raise SystemExit


sender_account = accounts[0]


print(
    "Kullanilan hesap:",
    sender_account
)


contract = web3.eth.contract(
    address=Web3.to_checksum_address(
        CONTRACT_ADDRESS
    ),
    abi=ABI
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


if total_json_count != 2229:

    print()
    print(
        "UYARI: Beklenen JSON sayisi 2229,"
        " ancak bulunan:",
        total_json_count
    )


# ============================================================
# TUM JSON HASHLERINI BIR KEZ HESAPLA
#
# Bu sure blockchain benchmarkina dahil edilmiyor.
# Batch buyuklugunun etkisini izole ediyoruz.
# ============================================================

print()
print(
    "Tum JSON hashleri onceden hesaplaniyor..."
)


all_hashes = []


for file_name in json_files:

    path = os.path.join(
        ORIGINAL_JSON_DIR,
        file_name
    )

    all_hashes.append(
        canonical_json_hash(
            path
        )
    )


print(
    "Hash hesaplama tamamlandi."
)


# ============================================================
# RAW SONUCLAR
# ============================================================

raw_results = []


# ============================================================
# BATCH SIZE TESTLERI
# ============================================================

for batch_size in BATCH_SIZES:

    expected_batch_count = math.ceil(
        total_json_count
        /
        batch_size
    )


    print()
    print(
        "======================================================"
    )

    print(
        "BATCH SIZE:",
        batch_size
    )

    print(
        "TOPLAM JSON:",
        total_json_count
    )

    print(
        "BEKLENEN BATCH / TRANSACTION:",
        expected_batch_count
    )

    print(
        "======================================================"
    )


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
        # 1. BATCH'LERE BOL VE MERKLE ROOT'LARI HESAPLA
        # ====================================================

        merkle_start = (
            time.perf_counter()
        )


        batch_roots = []


        for start_index in range(
            0,
            total_json_count,
            batch_size
        ):

            end_index = min(
                start_index + batch_size,
                total_json_count
            )


            batch_hashes = all_hashes[
                start_index:end_index
            ]


            merkle_root = build_merkle_root(
                batch_hashes
            )


            batch_roots.append(
                merkle_root
            )


        merkle_end = (
            time.perf_counter()
        )


        total_merkle_time = (
            merkle_end
            -
            merkle_start
        )


        actual_batch_count = len(
            batch_roots
        )


        # ====================================================
        # 2. TUM BATCH ROOT'LARINI BLOCKCHAIN'E YAZ
        # ====================================================

        total_gas_used = 0


        blockchain_start = (
            time.perf_counter()
        )


        for batch_index, merkle_root in enumerate(
            batch_roots,
            start=1
        ):

            # Tum testlerde benzer uzunlukta,
            # benzersiz batch ID kullaniyoruz.
            batch_id = (
                f"BS{batch_size:04d}_"
                f"R{repeat:02d}_"
                f"B{batch_index:04d}"
            )


            tx_hash = (
                contract.functions
                .storeBatchRoot(
                    batch_id,
                    bytes.fromhex(
                        merkle_root
                    )
                )
                .transact({
                    "from": sender_account
                })
            )


            receipt = (
                web3.eth
                .wait_for_transaction_receipt(
                    tx_hash
                )
            )


            total_gas_used += (
                receipt.gasUsed
            )


        blockchain_end = (
            time.perf_counter()
        )


        blockchain_time = (
            blockchain_end
            -
            blockchain_start
        )


        # ====================================================
        # 3. UCTAN UCA SURE
        #
        # Hash hesabi haric:
        # Merkle root olusturma + blockchain kaydi
        # ====================================================

        total_pipeline_time = (
            total_merkle_time
            +
            blockchain_time
        )


        # ====================================================
        # EKRAN CIKTISI
        # ====================================================

        print(
            "Batch sayisi / Transaction:",
            actual_batch_count
        )

        print(
            "Toplam gasUsed:",
            total_gas_used
        )

        print(
            "Toplam Merkle olusturma suresi:",
            round(
                total_merkle_time,
                6
            ),
            "s"
        )

        print(
            "Toplam blockchain kayit suresi:",
            round(
                blockchain_time,
                6
            ),
            "s"
        )

        print(
            "Toplam pipeline suresi:",
            round(
                total_pipeline_time,
                6
            ),
            "s"
        )


        # ====================================================
        # RAW KAYIT
        # ====================================================

        raw_results.append({
            "Total JSON Count":
                total_json_count,

            "Batch Size":
                batch_size,

            "Repeat":
                repeat,

            "Batch Count":
                actual_batch_count,

            "Transaction Count":
                actual_batch_count,

            "Total Gas Used":
                total_gas_used,

            "Merkle Build Total Time (s)":
                total_merkle_time,

            "Blockchain Registration Total Time (s)":
                blockchain_time,

            "Total Pipeline Time (s)":
                total_pipeline_time
        })


# ============================================================
# RAW CSV
# ============================================================

raw_fieldnames = [
    "Total JSON Count",
    "Batch Size",
    "Repeat",
    "Batch Count",
    "Transaction Count",
    "Total Gas Used",
    "Merkle Build Total Time (s)",
    "Blockchain Registration Total Time (s)",
    "Total Pipeline Time (s)"
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


for batch_size in BATCH_SIZES:

    subset = [
        row

        for row in raw_results

        if row[
            "Batch Size"
        ] == batch_size
    ]


    transaction_values = [
        row[
            "Transaction Count"
        ]

        for row in subset
    ]


    gas_values = [
        row[
            "Total Gas Used"
        ]

        for row in subset
    ]


    merkle_values = [
        row[
            "Merkle Build Total Time (s)"
        ]

        for row in subset
    ]


    blockchain_values = [
        row[
            "Blockchain Registration Total Time (s)"
        ]

        for row in subset
    ]


    pipeline_values = [
        row[
            "Total Pipeline Time (s)"
        ]

        for row in subset
    ]


    # Ortalama
    tx_mean = statistics.mean(
        transaction_values
    )

    gas_mean = statistics.mean(
        gas_values
    )

    merkle_mean = statistics.mean(
        merkle_values
    )

    blockchain_mean = statistics.mean(
        blockchain_values
    )

    pipeline_mean = statistics.mean(
        pipeline_values
    )


    # Standart sapma
    tx_std = statistics.stdev(
        transaction_values
    )

    gas_std = statistics.stdev(
        gas_values
    )

    merkle_std = statistics.stdev(
        merkle_values
    )

    blockchain_std = statistics.stdev(
        blockchain_values
    )

    pipeline_std = statistics.stdev(
        pipeline_values
    )


    summary_results.append({
        "Total JSON Count":
            total_json_count,

        "Batch Size":
            batch_size,

        "Repeat Count":
            REPEAT_COUNT,

        "Transaction Mean":
            round(
                tx_mean,
                2
            ),

        "Transaction Std":
            round(
                tx_std,
                2
            ),

        "Gas Mean":
            round(
                gas_mean,
                2
            ),

        "Gas Std":
            round(
                gas_std,
                2
            ),

        "Merkle Build Mean (s)":
            round(
                merkle_mean,
                6
            ),

        "Merkle Build Std (s)":
            round(
                merkle_std,
                6
            ),

        "Blockchain Time Mean (s)":
            round(
                blockchain_mean,
                6
            ),

        "Blockchain Time Std (s)":
            round(
                blockchain_std,
                6
            ),

        "Pipeline Time Mean (s)":
            round(
                pipeline_mean,
                6
            ),

        "Pipeline Time Std (s)":
            round(
                pipeline_std,
                6
            )
    })


# ============================================================
# SUMMARY CSV
# ============================================================

summary_fieldnames = [
    "Total JSON Count",
    "Batch Size",
    "Repeat Count",
    "Transaction Mean",
    "Transaction Std",
    "Gas Mean",
    "Gas Std",
    "Merkle Build Mean (s)",
    "Merkle Build Std (s)",
    "Blockchain Time Mean (s)",
    "Blockchain Time Std (s)",
    "Pipeline Time Mean (s)",
    "Pipeline Time Std (s)"
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
# SONUCLARI EKRANA YAZ
# ============================================================

print()
print(
    "======================================================"
)

print(
    "BATCH SIZE BENCHMARK TAMAMLANDI"
)

print(
    "======================================================"
)


for result in summary_results:

    print()

    print(
        "Batch Size:",
        result[
            "Batch Size"
        ]
    )

    print(
        "Transaction:",
        result[
            "Transaction Mean"
        ],
        "+/-",
        result[
            "Transaction Std"
        ]
    )

    print(
        "Gas:",
        result[
            "Gas Mean"
        ],
        "+/-",
        result[
            "Gas Std"
        ]
    )

    print(
        "Merkle Build:",
        result[
            "Merkle Build Mean (s)"
        ],
        "+/-",
        result[
            "Merkle Build Std (s)"
        ],
        "s"
    )

    print(
        "Blockchain Time:",
        result[
            "Blockchain Time Mean (s)"
        ],
        "+/-",
        result[
            "Blockchain Time Std (s)"
        ],
        "s"
    )

    print(
        "Pipeline Time:",
        result[
            "Pipeline Time Mean (s)"
        ],
        "+/-",
        result[
            "Pipeline Time Std (s)"
        ],
        "s"
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
    "======================================================"
)