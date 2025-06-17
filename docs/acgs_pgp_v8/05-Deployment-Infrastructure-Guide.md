# 5. Deployment & Infrastructure Guide (v8)

This guide outlines the deployment for the new QEC-SFT components.

## 5.1. Microservices Topology & Kubernetes

The v8 architecture introduces new, potentially resource-intensive services.

*   **`generation-engine`**: Deployment scaled based on the queue depth of LSU generation requests.
*   **`see` (Stabilizer Execution Environment)**: A critical component. May require a dedicated node pool with access to specialized tooling (e.g., licensed static analyzers, high-CPU nodes for model checkers). Deployed as a set of workers processing stabilization jobs.
*   **`sde` (Syndrome Diagnostic Engine)**: A standard Deployment. If using ML models, it may require GPU resources for inference.
*   **`certified-compiler`**: A standard Deployment that listens for signals from the SDE.

## 5.2. CI/CD Pipeline ("Semantic Verification" Stage)

The CI/CD pipeline for the ACGS-PGP system itself now includes a stage to verify the integrity of the core components.

1.  **Lint & Unit Test**: Standard code quality checks.
2.  **Build & Push**: Build container images for all services.
3.  **Semantic Verification**: A new, critical stage.
    *   Deploy the entire stack to a temporary namespace.
    *   Run a "golden path" test: Push a known-good LSU through the system.
    *   Assert that the SEE executes and the SDE produces a coherent (`all +1s`) syndrome.
    *   Run a "fault injection" test: Push a known-bad LSU.
    *   Assert that the SDE produces the expected `INCOHERENT` syndrome and diagnosis.
4.  **Deploy to Staging**: If semantic verification passes, deploy to the staging environment.
