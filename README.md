# Blockchain-Based Integrity Verification with Merkle Trees

This repository contains the smart contracts, verification scripts, security tests, and experimental results developed for a blockchain-based integrity verification system for object detection outputs.

## Project Overview

The proposed system aims to protect object detection results against unauthorized modification and provide verifiable data integrity using cryptographic and blockchain-based mechanisms.

The main components of the system are:

- SHA-256 hashing of JSON detection outputs
- RSA digital signatures
- Authorized signer verification
- Merkle Tree construction
- Merkle Proof generation and verification
- Blockchain-based Merkle Root registration
- Provenance metadata verification
- Manipulation and security attack tests
- Blockchain performance experiments
- Merkle Tree scalability experiments
- Batch size performance analysis

## Dataset Information

The experiments use object detection outputs derived from the DIOR remote sensing dataset.

The complete DIOR dataset contains 23,463 images.

In this study, **2,229 unique images** were processed and converted into JSON detection outputs.

The processed data contains:

- 2,229 JSON files
- 2,229 unique image records
- 12,210 object detection records
- 0 empty JSON files

Therefore, **N = 2229** represents the number of images whose object detection outputs were used in the blockchain verification experiments.

It does **not** represent the complete official DIOR test split.

The full DIOR dataset and the complete collection of 2,229 detection output files are not included in this repository.

Only a small number of sample JSON files are provided for reproducibility.

## Repository Structure

```text
blockchain-merkle-verification/
│
├── contracts/
│   ├── MerkleRegistry.sol
│   ├── SignerRegistry.sol
│   ├── BatchRegistry.sol
│   └── BenchmarkRegistry.sol
│
├── scripts/
│   ├── generate_keys.py
│   ├── sign_json.py
│   ├── verify_signature.py
│   ├── merkle_tree.py
│   ├── merkle_proof.py
│   ├── invalid_merkle_proof.py
│   ├── security_test_suite.py
│   ├── create_provenance.py
│   ├── verify_provenance.py
│   ├── provenance_attack_tests.py
│   ├── signer_lifecycle_test.py
│   ├── real_blockchain_benchmark.py
│   ├── merkle_scalability_test.py
│   └── batch_size_benchmark.py
│
├── sample_json/
│   ├── original/
│   │   └── 00003.json
│   │
│   └── modified/
│       └── 00003.json
│
├── results/
│   ├── security_test_results.csv
│   ├── real_blockchain_benchmark_raw.csv
│   ├── real_blockchain_benchmark_summary.csv
│   ├── merkle_scalability_raw.csv
│   ├── merkle_scalability_summary.csv
│   ├── provenance_attack_results.csv
│   ├── signer_lifecycle_results.csv
│   ├── batch_size_benchmark_raw.csv
│   └── batch_size_benchmark_summary.csv
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

The project requires Python 3.

The main Python packages used in the experiments are:

- `web3`
- `cryptography`
- `python-dotenv`
- `pandas`

For blockchain experiments, a local Ethereum-compatible blockchain environment such as Ganache can be used.

The Solidity smart contracts can be compiled and deployed using Remix IDE.

## Installation

Clone or download the repository and open a terminal in the project directory.

Install the required Python packages with:

```bash
pip install -r requirements.txt
```

A local Ethereum blockchain can be started using Ganache.

The smart contracts located in the `contracts/` directory can be compiled and deployed using Remix IDE.

When using Ganache, the RPC endpoint may typically be similar to:

```text
http://127.0.0.1:7545
```

Contract addresses may change whenever the contracts are redeployed.

Therefore, blockchain connection settings and contract addresses used by the Python scripts should be updated according to the local environment.

## Basic Verification Workflow

The basic integrity verification process consists of the following steps:

1. Read the original JSON object detection output.
2. Convert the JSON data into a canonical representation.
3. Calculate the SHA-256 hash of the canonical JSON data.
4. Sign the data using an RSA private key.
5. Verify the digital signature using the corresponding RSA public key.
6. Check whether the signer is authorized.
7. Construct a Merkle Tree from multiple detection outputs.
8. Generate a Merkle Proof for an individual JSON record.
9. Verify the Merkle Proof against the corresponding Merkle Root.
10. Retrieve or compare the Merkle Root registered on the blockchain.
11. Accept the record only if all verification stages are successful.

This architecture enables both individual integrity verification and efficient batch-based blockchain registration.

## JSON Hashing

The JSON detection outputs are transformed into a canonical representation before hashing.

Canonical representation is used to ensure that logically identical JSON data produces the same hash value regardless of formatting differences.

SHA-256 is then used to generate the hash value.

Any modification to fields such as:

- file name
- class ID
- confidence score
- bounding box coordinates

produces a different hash value.

This allows manipulated object detection outputs to be detected.

## Digital Signature Verification

RSA digital signatures are used to verify the authenticity of JSON detection outputs.

A private key is used to sign the data, while the corresponding public key is used for verification.

If the JSON file is modified after signing, the signature verification fails.

Private keys used during the experiments are intentionally excluded from this repository.

Users who want to reproduce the tests should generate their own test key pair locally.

## Authorized Signer Verification

The system also includes signer authorization control.

A signer fingerprint can be registered in the `SignerRegistry` smart contract.

The system supports:

- Signer authorization
- Signer revocation
- Authorized signer verification
- Rejection of never-authorized signers

This prevents a mathematically valid signature produced by an unauthorized attacker from being accepted by the system.

## Merkle Tree Verification

Instead of storing every JSON hash individually on the blockchain, multiple hashes can be combined using a Merkle Tree.

Each JSON hash represents a leaf node.

The hashes are recursively combined until a single value called the **Merkle Root** is produced.

The Merkle Root can then be registered on the blockchain using only one transaction.

This approach significantly reduces:

- Number of blockchain transactions
- Gas consumption
- Blockchain registration time

while still allowing individual records to be verified using Merkle Proofs.

## Merkle Proof

A Merkle Proof allows an individual JSON record to be verified without storing every record hash separately on the blockchain.

The verification process checks whether a specific JSON hash belongs to the Merkle Tree represented by the registered Merkle Root.

The experiments include both:

- Valid Merkle Proof verification
- Invalid Merkle Proof attack simulation

A modified or invalid proof is rejected.

## Blockchain Registration

The Merkle Root is registered on an Ethereum-compatible blockchain through Solidity smart contracts.

The repository contains the following smart contracts:

### MerkleRegistry.sol

Stores and retrieves Merkle Root values associated with batch identifiers.

### SignerRegistry.sol

Manages authorized signer fingerprints and supports signer authorization and revocation.

### BatchRegistry.sol

Stores Merkle Roots generated for different batches.

### BenchmarkRegistry.sol

Supports performance comparison between individual hash registration and Merkle Root registration.

## Security Tests

The project includes several security experiments designed to evaluate the proposed verification architecture.

The tested scenarios include:

- Normal unmodified JSON
- Modified JSON
- Invalid digital signature
- Unauthorized signer
- Invalid Merkle Proof
- Provenance metadata manipulation
- Authorized signer
- Never-authorized attacker
- Revoked signer

The main security test suite evaluates five fundamental scenarios:

1. Normal data
2. Modified JSON
3. Invalid signature
4. Unauthorized signer
5. Invalid Merkle Proof

The expected behavior is that only the original valid record is accepted.

All manipulated or unauthorized cases should be rejected.

The security test results are available in:

```text
results/security_test_results.csv
```

## Provenance Verification

The system also includes provenance metadata to provide additional information about the origin and processing history of the detection output.

Example provenance fields include:

- Image ID
- Model name
- Model version
- Timestamp
- Batch ID
- JSON hash

The provenance record is digitally signed.

Manipulation tests were performed by modifying individual provenance fields.

The tested manipulation scenarios include changes to:

- `image_id`
- `model`
- `model_version`
- `timestamp`
- `batch_id`
- `json_hash`

Modified provenance records are expected to fail verification.

The results are available in:

```text
results/provenance_attack_results.csv
```

## Signer Lifecycle Tests

Signer authorization lifecycle experiments were also performed.

The tested cases include:

1. Authorized signer
2. Never-authorized attacker
3. Revoked signer

The expected results are:

- Authorized signer → ACCEPTED
- Never-authorized attacker → REJECTED
- Revoked signer → REJECTED

The results are available in:

```text
results/signer_lifecycle_results.csv
```

## Performance Experiments

The repository contains performance experiments comparing two blockchain registration approaches.

### Individual Blockchain Registration

In the traditional approach, each object detection output hash is registered using a separate blockchain transaction.

For example:

```text
100 records  → 100 blockchain transactions
1000 records → 1000 blockchain transactions
2229 records → 2229 blockchain transactions
```

### Merkle-Based Blockchain Registration

In the proposed Merkle-based approach, multiple JSON hashes are combined into a single Merkle Root.

Only one Merkle Root is registered on the blockchain.

For example:

```text
100 records  → 1 blockchain transaction
1000 records → 1 blockchain transaction
2229 records → 1 blockchain transaction
```

This significantly reduces blockchain transaction overhead.

## Blockchain Benchmark

Real blockchain transaction experiments were performed using the following dataset sizes:

- N = 100
- N = 1000
- N = 2229

Each experiment was repeated multiple times.

The following measurements were collected:

- Number of blockchain transactions
- Total gas consumption
- Blockchain registration time
- Merkle Tree construction time

The results are available in:

```text
results/real_blockchain_benchmark_raw.csv
results/real_blockchain_benchmark_summary.csv
```

## Merkle Scalability Experiment

Merkle Tree scalability was evaluated using:

- N = 100
- N = 1000
- N = 2229

The following metrics were measured:

- Merkle Tree construction time
- Merkle Proof generation time
- Merkle Proof verification time
- Merkle Proof length
- Proof verification success rate

Multiple random proofs were generated and verified for each dataset size.

The results are available in:

```text
results/merkle_scalability_raw.csv
results/merkle_scalability_summary.csv
```

## Batch Size Experiment

The effect of different batch sizes on blockchain performance was also evaluated.

The tested batch sizes were:

- 10
- 50
- 100
- 500
- 2229

For each batch size, separate Merkle Roots were generated and registered on the blockchain.

The following metrics were measured:

- Number of blockchain transactions
- Total gas consumption
- Merkle Tree construction time
- Blockchain registration time
- Total pipeline time

Smaller batch sizes require more blockchain transactions.

Larger batch sizes reduce the number of transactions and overall gas consumption.

The results are available in:

```text
results/batch_size_benchmark_raw.csv
results/batch_size_benchmark_summary.csv
```

## Experimental Results

The `results/` directory contains both raw and summarized experimental outputs.

Included result files:

```text
security_test_results.csv
real_blockchain_benchmark_raw.csv
real_blockchain_benchmark_summary.csv
merkle_scalability_raw.csv
merkle_scalability_summary.csv
provenance_attack_results.csv
signer_lifecycle_results.csv
batch_size_benchmark_raw.csv
batch_size_benchmark_summary.csv
```

These files allow the main experimental results to be reviewed without distributing the complete dataset.

## Sample Data

The complete object detection output dataset is not included in the repository.

Instead, a small number of sample JSON files are provided.

Example:

```text
sample_json/
├── original/
│   └── 00003.json
│
└── modified/
    └── 00003.json
```

The original JSON file represents an unmodified detection output.

The modified JSON file can be used to demonstrate integrity verification and manipulation detection.

## Reproducibility

The repository is designed to allow the fundamental verification and security experiments to be reproduced without publishing the entire DIOR dataset or all 2,229 JSON detection outputs.

A typical reproduction workflow is:

1. Install the required Python packages.
2. Generate a local RSA key pair.
3. Use the sample JSON file.
4. Generate its SHA-256 hash.
5. Sign the JSON data.
6. Verify the digital signature.
7. Construct a Merkle Tree.
8. Generate and verify a Merkle Proof.
9. Deploy the required Solidity contract using Remix.
10. Connect to a local blockchain such as Ganache.
11. Register the Merkle Root.
12. Run the available security and performance scripts.

Some scripts may require local paths, blockchain addresses, or environment-specific parameters to be updated before execution.

## Security Notice

Sensitive credentials are intentionally excluded from this repository.

The repository does **not** contain:

- RSA private keys
- Attacker private keys
- MetaMask private keys
- Ganache account private keys
- Wallet seed phrases
- Real wallet credentials
- `.env` credential files
- Complete DIOR dataset
- Complete collection of 2,229 JSON detection outputs

Private credentials should never be committed to a public GitHub repository.

Test keys should be generated locally.

## .gitignore

The `.gitignore` file prevents sensitive or unnecessary files from being committed.

Excluded data includes:

- Environment files
- Private key files
- Generated signatures
- Full dataset directories
- Full JSON output directories
- Python cache files
- Local virtual environments
- IDE configuration files

## Important Notes

- Contract addresses may change after every deployment.
- Ganache account addresses may change if a new workspace is created.
- Users should generate their own test RSA keys.
- Users should deploy their own local smart contracts.
- Private keys and wallet credentials must not be uploaded to GitHub.
- The complete DIOR dataset is intentionally not distributed through this repository.
- Only limited sample data is provided for reproducibility.

## Author

**Ezo Fidel Aytekin**

Electronics and Communication Engineering