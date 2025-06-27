#!/usr/bin/env python3
"""
Quick test for production dashboard functionality
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/home/ubuntu/ACGS')

async def test_dashboard_metrics():
    """Test that the production dashboard can collect metrics."""
    
    try:
        # Import the dashboard
        from services.monitoring.production_dashboard import ProductionDashboard
        
        print("🚀 Testing Production Dashboard...")
        
        # Create dashboard instance
        dashboard = ProductionDashboard()
        
        # Initialize dashboard
        await dashboard.initialize()
        print("✅ Dashboard initialized successfully")
        
        # Collect metrics
        metrics = await dashboard.collect_real_time_metrics()
        print("✅ Metrics collected successfully")
        
        # Print metrics summary
        print("\n📊 Metrics Summary:")
        print(f"  - Timestamp: {metrics.get('timestamp', 'N/A')}")
        print(f"  - Uptime: {metrics.get('uptime_formatted', 'N/A')}")
        print(f"  - Constitutional Hash: {metrics.get('constitutional_hash', 'N/A')}")
        
        # Check service metrics
        service_metrics = metrics.get('service_metrics', {})
        if service_metrics:
            print(f"  - Total Requests: {service_metrics.get('total_requests', 0)}")
            print(f"  - Model Usage: {service_metrics.get('model_usage', {})}")
            
            performance = service_metrics.get('performance', {})
            if performance:
                print(f"  - Avg Response Time: {performance.get('avg_response_time_ms', 0):.2f}ms")
                
            quality = service_metrics.get('quality', {})
            if quality:
                print(f"  - Constitutional Compliance: {quality.get('constitutional_compliance_rate', 0):.2%}")
                print(f"  - Cache Hit Rate: {quality.get('cache_hit_rate', 0):.2%}")
        
        # Check cache metrics
        cache_metrics = metrics.get('cache_metrics', {})
        if cache_metrics and 'error' not in cache_metrics:
            print(f"  - Cache Hit Rate: {cache_metrics.get('hit_rate', 0):.2%}")
            print(f"  - Cache Requests: {cache_metrics.get('total_requests', 0)}")
        
        # Test cost analysis
        cost_analysis = await dashboard.generate_cost_analysis()
        print("\n💰 Cost Analysis:")
        print(f"  - Total Cost: ${cost_analysis.get('total_cost_estimate', 0):.4f}")
        print(f"  - Cost per Request: ${cost_analysis.get('cost_per_request', 0):.6f}")
        
        # Test dashboard data generation
        dashboard_data = await dashboard.generate_dashboard_data()
        print("\n📈 Dashboard Data Generated Successfully")
        print(f"  - Constitutional Hash: {dashboard_data.get('constitutional_hash', 'N/A')}")
        print(f"  - Last Updated: {dashboard_data.get('last_updated', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    
    print("🔧 Testing ACGS-PGP Production Dashboard")
    print("=" * 50)
    
    success = await test_dashboard_metrics()
    
    if success:
        print("\n✅ All dashboard tests passed!")
        print("🎉 Production monitoring dashboard is fully operational")
        return 0
    else:
        print("\n❌ Dashboard tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
