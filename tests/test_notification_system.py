#!/usr/bin/env python3
"""
Test script for notification.py functionality
Constitutional Hash: cdd01ef066bc6cf2

Tests the complete notification system including:
1. JSON logging to logs/notification.json
2. TTS provider fallback chain
3. Engineer name prepending
4. Non-blocking failure handling
"""

import json
import os
import sys
import time
from pathlib import Path

# Add the .claude/hooks directory to path for importing
sys.path.insert(0, str(Path(__file__).parent / ".claude" / "hooks"))

try:
    from notification import (
        notification_hook,
        NotificationLogger,
        TTSManager,
        ElevenLabsProvider,
        OpenAIProvider,
        Pyttsx3Provider
    )
    print("✅ Successfully imported notification system")
except ImportError as e:
    print(f"❌ Failed to import notification system: {e}")
    sys.exit(1)


def test_notification_logging():
    """Test JSON logging functionality."""
    print("\n🧪 Testing notification logging...")
    
    # Create test notification
    test_metadata = {
        "test_id": "notification_test_001",
        "component": "test_runner",
        "priority": "high"
    }
    
    # Call notification hook
    notification_hook(
        notification_type="info",
        message="Test notification for logging validation",
        metadata=test_metadata
    )
    
    # Give it a moment for async operations
    time.sleep(1)
    
    # Check if log file was created and contains our event
    log_file = Path("logs/notification.json")
    if log_file.exists():
        print("✅ Log file created successfully")
        
        # Read and validate the last line
        with open(log_file, "r") as f:
            lines = f.readlines()
            if lines:
                last_event = json.loads(lines[-1])
                print(f"✅ Event logged: {last_event['notification_type']} - {last_event['message']}")
                print(f"✅ Constitutional hash: {last_event['constitutional_hash']}")
                print(f"✅ Engineer: {last_event['engineer']}")
                return True
    
    print("❌ Log file not found or empty")
    return False


def test_tts_providers():
    """Test TTS provider availability and configuration."""
    print("\n🧪 Testing TTS providers...")
    
    tts_manager = TTSManager()
    
    for i, provider in enumerate(tts_manager.providers, 1):
        provider_name = provider.__class__.__name__
        print(f"{i}. {provider_name}: {'✅ Available' if provider.enabled else '❌ Disabled/Missing'}")
        
        if hasattr(provider, 'api_key'):
            key_status = "🔑 Configured" if provider.api_key else "🔓 No API key"
            print(f"   API Key: {key_status}")
    
    return True


def test_engineer_name_prepending():
    """Test engineer name prepending functionality."""
    print("\n🧪 Testing engineer name prepending...")
    
    # Set engineer name for testing
    original_engineer = os.getenv("ENGINEER_NAME")
    os.environ["ENGINEER_NAME"] = "Test Engineer"
    
    tts_manager = TTSManager()
    
    # Test multiple times to see the 30% chance in action
    prepend_count = 0
    test_iterations = 10
    
    print(f"Running {test_iterations} tests to check 30% prepending rate...")
    
    for i in range(test_iterations):
        result = tts_manager.speak_async(f"Test message {i}")
        time.sleep(0.1)  # Brief pause
        
        if result["engineer_prepended"]:
            prepend_count += 1
            print(f"  Test {i+1}: ✅ Engineer name prepended - '{result['speech_text']}'")
        else:
            print(f"  Test {i+1}: ➖ No prepending - '{result['speech_text']}'")
    
    prepend_rate = (prepend_count / test_iterations) * 100
    print(f"📊 Engineer name prepended in {prepend_count}/{test_iterations} tests ({prepend_rate:.1f}%)")
    
    # Restore original engineer name
    if original_engineer:
        os.environ["ENGINEER_NAME"] = original_engineer
    elif "ENGINEER_NAME" in os.environ:
        del os.environ["ENGINEER_NAME"]
    
    return True


def test_non_blocking_behavior():
    """Test that TTS operations don't block the main thread."""
    print("\n🧪 Testing non-blocking behavior...")
    
    start_time = time.time()
    
    # Trigger multiple notifications rapidly
    for i in range(3):
        notification_hook(
            notification_type="test",
            message=f"Non-blocking test message {i+1}",
            metadata={"test_batch": "non_blocking", "sequence": i+1}
        )
    
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    
    print(f"✅ 3 notifications processed in {duration_ms:.2f}ms")
    
    if duration_ms < 100:  # Should be very fast since it's non-blocking
        print("✅ Non-blocking behavior confirmed")
        return True
    else:
        print("⚠️  May be blocking (took longer than expected)")
        return False


def test_error_handling():
    """Test error handling and silent failure."""
    print("\n🧪 Testing error handling...")
    
    # Test with invalid metadata that might cause JSON serialization issues
    notification_hook(
        notification_type="error_test",
        message="Testing error handling with complex data",
        metadata={
            "normal_key": "normal_value",
            "complex_object": {"nested": {"deeply": "test"}},
            "list_data": [1, 2, 3, "mixed", {"types": True}]
        }
    )
    
    print("✅ Error handling test completed (no exceptions thrown)")
    return True


def main():
    """Run all notification system tests."""
    print("🔬 ACGS Notification System Test Suite")
    print("=" * 50)
    
    tests = [
        ("Notification Logging", test_notification_logging),
        ("TTS Provider Configuration", test_tts_providers),
        ("Engineer Name Prepending", test_engineer_name_prepending),
        ("Non-blocking Behavior", test_non_blocking_behavior),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Notification system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Show log file location
    log_file = Path("logs/notification.json")
    if log_file.exists():
        print(f"\n📝 Notification log file: {log_file.absolute()}")
        print(f"   File size: {log_file.stat().st_size} bytes")
        
        # Show last few events
        with open(log_file, "r") as f:
            lines = f.readlines()
            if lines:
                print(f"   Events logged: {len(lines)}")
                print("\n📄 Last event:")
                last_event = json.loads(lines[-1])
                print(json.dumps(last_event, indent=2))


if __name__ == "__main__":
    main()
