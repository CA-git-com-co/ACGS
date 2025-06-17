# 2. Detailed Component Specifications (v8 QEC-SFT)

This document details the components of the ACGS-PGP v8 architecture.

## 2.1. Generation Engine

*   **Purpose**: To encode a Logical Semantic Unit (LSU) into a diverse set of physical representations.
*   **Responsibilities**:
    *   Consume LSU definitions from the AC Repository.
    *   Utilize multiple generation techniques (templates, LLMs) to produce a heterogeneous set of artifacts.
    *   Ensure generated artifacts are stored and versioned together, linked to the parent LSU.
*   **Data Models (Output)**: A collection of artifacts, e.g.:
    *   `code.py`: Python implementation.
    *   `spec.tla`: TLA+ formal specification.
    *   `tests.py`: Pytest test suite.
    *   `docs.md`: Structured natural language description.
*   **Interfaces**: Consumes events from the AC Repository; writes artifacts to a shared workspace for the SEE.

## 2.2. Stabilizer Execution Environment (SEE)

*   **Purpose**: To orchestrate the execution of Semantic Stabilizers and generate the Semantic Syndrome Vector.
*   **Responsibilities**:
    *   Manage a registry of available Semantic Stabilizers.
    *   For a given set of representations, determine the applicable stabilizers.
    *   Invoke the necessary tools (compilers, test runners, model checkers, static analyzers) for each check.
    *   Collect the binary pass/fail (+1/-1) outcome from each stabilizer.
    *   Assemble the outcomes into the final Semantic Syndrome Vector.
*   **Algorithms & Workflows**:
    ```mermaid
    sequenceDiagram
        participant GenEngine
        participant SEE
        participant SDE
        participant Tools as Tooling (Pytest, TLC, etc.)
        GenEngine->>SEE: Trigger Check for LSU-123
        SEE->>+Tools: Run S_test(code, tests)
        Tools-->>-SEE: Return -1 (Fail)
        SEE->>+Tools: Run S_model(code, spec)
        Tools-->>-SEE: Return +1 (Pass)
        SEE->>SEE: Assemble Syndrome Vector [-1, +1, ...]
        SEE->>SDE: Submit Syndrome for LSU-123
    ```

## 2.3. Syndrome Diagnostic Engine (SDE)

*   **Purpose**: To interpret the Semantic Syndrome Vector and provide an actionable diagnosis of the system's semantic health.
*   **Responsibilities**:
    *   Receive a syndrome vector from the SEE.
    *   Map the syndrome pattern to a known fault type.
    *   Generate a diagnostic report specifying the likely location and nature of the semantic error.
    *   Issue a "Certificate of Semantic Integrity" for coherent states.
    *   Trigger automated recovery actions (e.g., targeted regeneration, flagging for human review).
*   **Algorithms**:
    *   **Level 1 (Lookup Table)**: A map of critical syndromes to hard-coded diagnoses.
    *   **Level 2 (Rule-Based System)**: An expert system to reason about patterns (e.g., `IF S_test fails AND S_coverage fails THEN fault is likely in test generation`).
    *   **Level 3 (ML Classifier)**: A trained model to diagnose novel syndrome patterns.

## 2.4. Certified Artifact Compiler

*   **Purpose**: To compile, sign, and publish an artifact *only after* it has been certified as semantically coherent by the SDE.
*   **Responsibilities**:
    *   Receive a "go-ahead" signal from the SDE, which includes the certificate of integrity.
    *   Compile the primary artifact (e.g., the Rego policy from the Python code).
    *   Create a final package containing the artifact and its certificate (which includes the syndrome).
    *   Cryptographically sign the entire package.
    *   Publish the signed package to the Artifact Store.
