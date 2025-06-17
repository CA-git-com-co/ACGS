# 4. Data & Policy Formats (v8)

This document defines the key data structures for the QEC-SFT framework.

## 4.1. Logical Semantic Unit (LSU) / Principle

*(The schema for a Principle remains largely unchanged from v7, but its conceptual role is elevated to that of an LSU.)*

## 4.2. Semantic Syndrome Vector

*   **Format**: JSON
*   **Description**: The data structure representing the output of the SEE. It's an ordered list of stabilizer outcomes.
```json
{
  "lsu_id": "principle-a1b2c3",
  "stabilizer_map": [
    { "name": "S_test(Code_Py, Tests_Pytest)", "outcome": -1 },
    { "name": "S_cfg(Code_Py, Code_Java)", "outcome": 1 },
    { "name": "S_model(Code_Java, Formal_TLA+)", "outcome": 1 },
    { "name": "S_coverage(NL_Desc, Tests_Pytest)", "outcome": -1 }
  ],
  "vector": [-1, 1, 1, -1]
}
```

## 4.3. Certified Artifact Package

*   **Format**: JSON
*   **Description**: The final, signed object stored in the Artifact Store. It bundles the operational artifact with its proof of semantic integrity.

```json
{
  "payload": {
    "artifact_id": "rego-financial-advice-v3",
    "artifact_type": "rego_policy",
    "artifact_body": "deny[msg] { contains(input.prompt, \"stocks to buy\") ... }",
    "lsu_id": "principle-a1b2c3"
  },
  "certificate_of_semantic_integrity": {
    "diagnosis_id": "diag-pqr456",
    "certified_at": "2025-06-16T14:00:00Z",
    "syndrome_vector":,
    "sde_version": "v1.2.0"
  },
  "signature": {
    "key_id": "kms-key-prod-02",
    "value": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A..."
  }
}
```
*   **Signature Details**: The signature covers a canonicalized JSON string of both the `payload` and the `certificate_of_semantic_integrity`, binding the artifact to its verification process.
