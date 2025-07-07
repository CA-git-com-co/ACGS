#!/bin/bash
# ACGS Scheduled Validation
# Constitutional Hash: cdd01ef066bc6cf2

cd "/home/dislove/ACGS-2/scripts/continuous-improvement/../.."
./scripts/continuous-improvement/metrics-collector.sh
./scripts/continuous-improvement/ci-cd-integration.sh
