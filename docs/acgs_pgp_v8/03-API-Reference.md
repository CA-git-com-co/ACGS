# 3. API Reference (v8)

This document provides the API specifications for the ACGS-PGP v8 services. External APIs remain stable, while internal APIs reflect the new QEC-SFT workflow.

## 3.1. AC Repository API (`/ac-repo`)

_(No significant changes from v7. This API continues to manage the lifecycle of Principles/LSUs.)_

### `POST /v1/principles`

- **Description**: Creates a new Constitutional Principle (Logical Semantic Unit).

---

## 3.2. SDE Internal API (`/sde-internal`)

This is a new internal API used for managing the diagnostic process. Access is restricted to system components.

### `POST /v1/diagnose`

- **Description**: Submits a Semantic Syndrome Vector for diagnosis.
- **Auth**: Internal mTLS.
- **Request Body**:
  ```json
  {
    "lsu_id": "principle-a1b2c3",
    "representations_hash": "sha256:abcdef...",
    "syndrome_vector": [-1, 1, 1, -1]
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "diagnosis_id": "diag-xyz789",
    "status": "INCOHERENT",
    "probable_fault_location": "Test Suite Generation",
    "confidence": 0.85,
    "recommended_action": "TRIGGER_REGENERATE_TESTS"
  }
  ```

### `GET /v1/certificate/{lsu_id}`

- **Description**: Retrieves the latest Certificate of Semantic Integrity for an LSU.
- **Response (200 OK / 404 Not Found)**:
  ```json
  {
    "lsu_id": "principle-a1b2c3",
    "status": "COHERENT",
    "certified_at": "2025-06-16T14:00:00Z",
    "syndrome_vector":,
    "sde_version": "v1.2.0"
  }
  ```
