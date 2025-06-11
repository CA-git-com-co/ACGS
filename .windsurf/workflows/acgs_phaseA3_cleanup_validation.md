---
description: ACGS-1 Phase A3 – Comprehensive Cleanup & Validation Workflow
---

Follow this workflow to bring the ACGS-1 repository fully in-spec with Phase A3 development standards.  Each numbered step is self-contained and can be run independently; however, best results are obtained by running them in order.

Prerequisites
- Python 3.10+ and `pip` available
- Node 18+ and `npm`/`npx` available (for Prettier)
- Rust tool-chain with `rustfmt`
- Anchor & Solana CLI installed and configured for devnet
- Docker available for service orchestration & monitoring stack
- Activate the project virtual-env if one exists: `source .venv/bin/activate`

Steps

1. Generate a baseline health & security snapshot
   ```bash
   python comprehensive_system_health_check.py --output acgs_health_report_pre_cleanup.json
   ```
   This gives you a before/after diff for later comparison.

// turbo
2. Standardise code formatting & clean imports
   ```bash
   python code_quality_cleanup.py
   ```
   - Runs Black (88 cols), isort, Prettier and rustfmt
   - Removes unused imports & large commented blocks

// turbo
3. Consolidate & clean dependency manifests
   ```bash
   python dependency_cleanup.py
   ```
   - Merges duplicate `requirements*.txt`
   - Sorts & dedups `package.json`, `Cargo.toml`
   - Produces `dependency_cleanup_report.json`

4. Update OS-level & language-level dependencies (manual confirmation required)
   Update requires human review – check `dependency_cleanup_report.json` then run:
   ```bash
   # example – adapt as needed
   pip install -r requirements.txt --upgrade
   npm install && npm audit fix
   cargo update
   ```

5. Run security scanners to ensure **zero HIGH/CRITICAL findings**
   ```bash
   bandit -r acgs-core -o bandit_security_report_post_cleanup.json -f json
   npm audit --json > npm_audit_post_cleanup.json
   cargo audit -q --json > cargo_audit_post_cleanup.json
   ```
   Inspect the JSON reports and fix any flagged items.

// turbo
6. Execute unit test suites for the 7 core services
   ```bash
   ./run_tests.sh --unit
   ```
   Expect ≥80 % coverage/pass.

// turbo
7. Run Anchor program tests on Solana devnet
   ```bash
   anchor test --provider.cluster devnet
   ```

// turbo
8. Run integration + end-to-end workflows
   ```bash
   python comprehensive_integration_test_runner.py --mode full
   ```

// turbo
9. Validate monitoring, load-balancing & caching infrastructure
   ```bash
   python validate_phase3_monitoring.py && \
   python service_mesh_health_check.py
   ```

10. Performance regression check (response-time, throughput, cost)
   ```bash
   python performance_optimization.py --check-only
   ```
   Ensure: <500 ms p95 latency, >99.5 % availability, <0.01 SOL action cost, ≥1000 conc. users.

11. Post-cleanup health snapshot & diff
   ```bash
   python comprehensive_system_health_check.py --output acgs_health_report_post_cleanup.json
   python post_cleanup_validation.py --before acgs_health_report_pre_cleanup.json --after acgs_health_report_post_cleanup.json
   ```

12. Commit & push using conventional commits
   ```bash
   git add -A
   git commit -m "chore(cleanup): phase-A3 comprehensive codebase cleanup & validation"
   git push origin <branch>
   ```

Success checklist
- [ ] All tests pass, ≥80 % coverage
- [ ] `bandit`, `npm audit`, `cargo audit` reports show 0 HIGH/CRITICAL
- [ ] "ACGS System healthy" message from `post_cleanup_validation.py`
- [ ] Monitoring dashboard (Grafana) shows green across 163 alert rules
- [ ] Anchor program functions on Quantumagi devnet
- [ ] p95 latency < 500 ms, availability > 99.5 %, cost < 0.01 SOL
