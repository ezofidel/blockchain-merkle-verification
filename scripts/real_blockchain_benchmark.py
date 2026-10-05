import os
import json
import csv
import time
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
    "real_blockchain_benchmark_raw.csv"
)

SUMMARY_CSV_PATH = os.path.join(
    RESULT_DIR,
    "real_blockchain_benchmark_summary.csv"
)


RPC_URL = "http://127.0.0.1:7545"

CONTRACT_ADDRESS = (
    "0x050c1270b8410f94de1e22b4d7f3c524797882b1"
)


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
                "name": "recordId",
                "type": "string"
            },
            {
                "internalType": "bytes32",
                "name": "dataHash",
                "type": "bytes32"
            }
        ],
        "name": "storeIndividualHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
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
        "name": "storeMerkleRoot",
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
# MERKLE ROOT
# ============================================================

def build_merkle_root(hashes):

    if len(hashes) == 0:
        raise ValueError(
            "Merkle Tree icin en az bir hash gerekir."
        )

    current_level = hashes[:]

    while len(current_level) > 1:

        if len(current_level) % 2 == 1:
            current_level.append(
                current_level[-1]
            )

        next_level = []

        for i in range(
            0,
            len(current_level),
            2
        ):

            next_level.append(
                hash_pair(
                    current_level[i],
                    current_level[i + 1]
                )
            )

        current_level = next_level

    return current_level[0]


# ============================================================
# GANACHE BAGLANTISI
# ============================================================

print()
print("Ganache baglantisi kontrol ediliyor...")

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


# ============================================================
# TEST BOYUTLARI
# ============================================================
test_configs = [
    ("ALL", 2229)
]

# ============================================================
# BUTUN HASHLERI ONCEDEN HESAPLA
# ============================================================

print()
print(
    "JSON hashleri hesaplaniyor..."
)


all_hashes = []


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


print(
    "Hash hesaplama tamamlandi."
)


# ============================================================
# RAW SONUCLAR
# ============================================================

raw_results = []


# ============================================================
# TESTLER
# ============================================================

for config_name, n in test_configs:

    selected_files = json_files[:n]

    selected_hashes = all_hashes[:n]


    print()
    print(
        "===================================================="
    )

    print(
        "TEST:",
        config_name,
        "- JSON SAYISI:",
        n
    )

    print(
        "===================================================="
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
        # ESKI YONTEM
        # Her JSON icin 1 transaction
        # ====================================================

        old_total_gas = 0

        old_start = time.perf_counter()


        for index, file_hash in enumerate(
            selected_hashes
        ):

            # Her tekrarda benzersiz ID
            # Boylece daha onceki storage slot'u overwrite etmiyoruz.
            record_id = (
                f"{config_name}_"
                f"R{repeat}_"
                f"{index}_"
                f"{selected_files[index]}"
            )


            tx_hash = (
                contract.functions
                .storeIndividualHash(
                    record_id,
                    bytes.fromhex(
                        file_hash
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


            old_total_gas += (
                receipt.gasUsed
            )


        old_end = time.perf_counter()


        old_registration_time = (
            old_end
            -
            old_start
        )


        old_transaction_count = n


        print(
            "Eski yontem tamamlandi."
        )

        print(
            "Transaction:",
            old_transaction_count
        )

        print(
            "Toplam gasUsed:",
            old_total_gas
        )

        print(
            "Kayit suresi:",
            round(
                old_registration_time,
                4
            ),
            "s"
        )


        # ====================================================
        # MERKLE YONTEMI
        # ====================================================

        merkle_build_start = (
            time.perf_counter()
        )


        merkle_root = build_merkle_root(
            selected_hashes
        )


        merkle_build_end = (
            time.perf_counter()
        )


        merkle_build_time = (
            merkle_build_end
            -
            merkle_build_start
        )


        batch_id = (
            f"{config_name}_"
            f"MERKLE_R{repeat}"
        )


        merkle_tx_start = (
            time.perf_counter()
        )


        tx_hash = (
            contract.functions
            .storeMerkleRoot(
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


        merkle_tx_end = (
            time.perf_counter()
        )


        merkle_registration_time = (
            merkle_tx_end
            -
            merkle_tx_start
        )


        merkle_total_gas = (
            receipt.gasUsed
        )


        merkle_transaction_count = 1


        print(
            "Merkle yontemi tamamlandi."
        )

        print(
            "Transaction:",
            merkle_transaction_count
        )

        print(
            "Toplam gasUsed:",
            merkle_total_gas
        )

        print(
            "Blockchain kayit suresi:",
            round(
                merkle_registration_time,
                4
            ),
            "s"
        )

        print(
            "Merkle Tree olusturma suresi:",
            round(
                merkle_build_time,
                6
            ),
            "s"
        )


        # ====================================================
        # RAW RESULT - OLD
        # ====================================================

        raw_results.append({
            "Dataset":
                config_name,

            "JSON Count":
                n,

            "Method":
                "Old Individual Hash",

            "Repeat":
                repeat,

            "Transaction Count":
                old_transaction_count,

            "Total Gas Used":
                old_total_gas,

            "Blockchain Registration Time (s)":
                old_registration_time,

            "Merkle Build Time (s)":
                0.0
        })


        # ====================================================
        # RAW RESULT - MERKLE
        # ====================================================

        raw_results.append({
            "Dataset":
                config_name,

            "JSON Count":
                n,

            "Method":
                "Merkle Root",

            "Repeat":
                repeat,

            "Transaction Count":
                merkle_transaction_count,

            "Total Gas Used":
                merkle_total_gas,

            "Blockchain Registration Time (s)":
                merkle_registration_time,

            "Merkle Build Time (s)":
                merkle_build_time
        })


# ============================================================
# RAW CSV
# ============================================================

raw_fieldnames = [
    "Dataset",
    "JSON Count",
    "Method",
    "Repeat",
    "Transaction Count",
    "Total Gas Used",
    "Blockchain Registration Time (s)",
    "Merkle Build Time (s)"
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
# OZET SONUCLAR
# ============================================================

summary_results = []


for config_name, n in test_configs:

    for method in [
        "Old Individual Hash",
        "Merkle Root"
    ]:

        subset = [
            result

            for result
            in raw_results

            if (
                result["Dataset"]
                ==
                config_name
                and
                result["Method"]
                ==
                method
            )
        ]


        gas_values = [
            x["Total Gas Used"]
            for x
            in subset
        ]


        time_values = [
            x[
                "Blockchain Registration Time (s)"
            ]
            for x
            in subset
        ]


        merkle_build_values = [
            x["Merkle Build Time (s)"]
            for x
            in subset
        ]


        gas_mean = statistics.mean(
            gas_values
        )


        gas_std = (
            statistics.stdev(
                gas_values
            )
            if len(
                gas_values
            ) > 1
            else 0
        )


        time_mean = statistics.mean(
            time_values
        )


        time_std = (
            statistics.stdev(
                time_values
            )
            if len(
                time_values
            ) > 1
            else 0
        )


        build_mean = statistics.mean(
            merkle_build_values
        )


        build_std = (
            statistics.stdev(
                merkle_build_values
            )
            if len(
                merkle_build_values
            ) > 1
            else 0
        )


        summary_results.append({
            "Dataset":
                config_name,

            "JSON Count":
                n,

            "Method":
                method,

            "Repeat Count":
                REPEAT_COUNT,

            "Transaction Count":
                subset[0][
                    "Transaction Count"
                ],

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

            "Time Mean (s)":
                round(
                    time_mean,
                    6
                ),

            "Time Std (s)":
                round(
                    time_std,
                    6
                ),

            "Merkle Build Mean (s)":
                round(
                    build_mean,
                    6
                ),

            "Merkle Build Std (s)":
                round(
                    build_std,
                    6
                )
        })


# ============================================================
# SUMMARY CSV
# ============================================================

summary_fieldnames = [
    "Dataset",
    "JSON Count",
    "Method",
    "Repeat Count",
    "Transaction Count",
    "Gas Mean",
    "Gas Std",
    "Time Mean (s)",
    "Time Std (s)",
    "Merkle Build Mean (s)",
    "Merkle Build Std (s)"
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
# SON
# ============================================================

print()
print(
    "===================================================="
)

print(
    "GERCEK BLOCKCHAIN BENCHMARK TAMAMLANDI"
)

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