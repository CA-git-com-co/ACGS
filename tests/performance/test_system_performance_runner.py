import pytest
import json
from tests.performance.test_system_performance import PerformanceTestSuite


@pytest.mark.asyncio
async def test_system_performance():
    test_suite = PerformanceTestSuite()
    results = await test_suite.test_run_comprehensive_test_suite()
    with open("baseline_performance_report.json", "w") as f:
        json.dump(results, f, indent=4)
    assert results["overall_assessment"]["system_ready_for_production"] is True
