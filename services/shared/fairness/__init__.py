"""
Enhanced Fairness and Bias Detection Framework

This module integrates industry-standard fairness tools as recommended by the ACGE
technical validation report, replacing experimental approaches with proven solutions.

Key Components:
- Microsoft Fairlearn integration for bias detection and mitigation
- Google What-If Tool integration for model analysis
- Multi-algorithm fairness evaluation
- Production-ready bias monitoring
"""

from .enhanced_fairness_framework import EnhancedFairnessFramework
from .fairlearn_integration import FairlearnBiasDetector, FairnessMitigator
from .whatif_tool_integration import WhatIfToolAnalyzer

__all__ = [
    "FairlearnBiasDetector",
    "FairnessMitigator",
    "WhatIfToolAnalyzer",
    "EnhancedFairnessFramework",
]
