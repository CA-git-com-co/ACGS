# 8. Testing Strategy (v8)

The testing strategy for v8 focuses on validating the correctness of the fault tolerance framework itself.

## 8.1. Unit & Integration Tests

*(Standard tests for each microservice remain essential.)*

## 8.2. Semantic Stabilizer Validation

*   **Scope**: Each Semantic Stabilizer is a critical piece of software and must be tested rigorously.
*   **Process**: For each stabilizer (e.g., `S_cfg`), we must create pairs of inputs that are known to be consistent and inconsistent, and assert that the stabilizer returns `+1` and `-1` respectively.

## 8.3. Syndrome-based Fault Injection Testing

*   **Scope**: This is the most critical end-to-end test for the QEC-SFT framework. It tests the diagnostic capability of the entire system.
*   **Tooling**: A dedicated fault injection harness.
*   **Process**:
    1.  Define a library of common semantic faults (e.g., "off-by-one error," "incorrect boolean logic," "failure to handle null input").
    2.  The harness programmatically injects one of these faults into one of the physical representations (e.g., modifies the generated Python code).
    3.  The full stabilization and diagnosis pipeline is run.
    4.  The test asserts that the resulting Semantic Syndrome Vector matches the expected pattern for that specific fault.
    5.  The test asserts that the SDE's final diagnosis correctly identifies the type and location of the injected fault.
*   **Goal**: To build confidence that the system can not only detect but accurately diagnose errors.

## 8.4. Red-Teaming & Adversarial Tests

*   **Scope**: The focus shifts from bypassing a single rule to creating a **coherent but incorrect** set of artifacts.
*   **Scenario**: Can an adversary craft an LSU so cleverly ambiguous that it leads the Generation Engine to produce a set of *different but equally flawed* representations that still pass all the stabilizer checks? This tests the completeness and diversity of the stabilizer set itself.
