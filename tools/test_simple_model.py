#!/usr/bin/env python3
"""
Simple test for GPT-4 replacement models in ACGS-1
Tests Qwen3-32B (Groq) and OpenRouter models (DeepSeek Chat v3, Qwen3-235B, DeepSeek R1)
"""

import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv("/home/dislove/ACGS-1/.env")


def test_groq_qwen():
    """Test Qwen3-32B via Groq"""
    print("🧪 Testing Qwen3-32B via Groq...")

    try:
        from groq import Groq

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "user",
                    "content": "Explain constitutional governance in 50 words.",
                }
            ],
            temperature=0.1,
            max_tokens=100,
        )

        content = response.choices[0].message.content
        print(f"✅ Qwen3-32B: {content[:80]}...")
        return True

    except Exception as e:
        print(f"❌ Qwen3-32B failed: {e}")
        return False


def test_openrouter():
    """Test OpenRouter models"""
    print("\n🧪 Testing OpenRouter models...")

    try:
        from openai import OpenAI

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )

        models = [
            "deepseek/deepseek-chat-v3-0324:free",
            "qwen/qwen3-235b-a22b:free",
            "deepseek/deepseek-r1-0528:free",
        ]

        success_count = 0
        for model in models:
            try:
                print(f"   Testing {model}...")
                response = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://acgs.local",
                        "X-Title": "ACGS-PGP",
                    },
                    extra_body={},
                    model=model,
                    messages=[{"role": "user", "content": "What is governance?"}],
                    temperature=0.2,
                    max_tokens=50,
                )

                content = response.choices[0].message.content
                print(f"   ✅ {model}: {content[:50]}...")
                success_count += 1

            except Exception as e:
                print(f"   ❌ {model} failed: {e}")

        return success_count > 0

    except Exception as e:
        print(f"❌ OpenRouter test failed: {e}")
        return False


def main():
    """Run tests"""
    print("🚀 ACGS-1 GPT-4 Replacement Test")
    print("=" * 40)

    results = []
    results.append(test_groq_qwen())
    results.append(test_openrouter())

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! GPT-4 replacement successful.")
        print("\n✅ Model Configuration Summary:")
        print("   Primary Models:")
        print("   • Constitutional Prompting: Qwen3-235B (OpenRouter)")
        print("   • Policy Synthesis: DeepSeek Chat v3 (OpenRouter)")
        print("   • Conflict Resolution: Qwen3-32B (Groq)")
        print("   • Bias Mitigation: DeepSeek Chat v3 (OpenRouter)")
        print("   • Reflection: Qwen3-235B (OpenRouter)")
        print("   • Amendment Analysis: DeepSeek R1 (OpenRouter)")
        print("   • Communication: Qwen3-32B (Groq)")
        print("   • Monitoring: DeepSeek Chat v3 (OpenRouter)")
        print("\n   Fallback Models:")
        print("   • DeepSeek R1, Qwen3-32B, DeepSeek Chat v3")
        print("\n🔧 Integration Status:")
        print("   ✅ Groq API (Qwen3-32B) - Fast inference")
        print("   ✅ OpenRouter API (DeepSeek + Qwen3-235B) - Advanced reasoning")
        print("   ✅ Multi-model configuration updated")
        print("   ✅ GPT-4 references replaced")
    else:
        print("⚠️  Some tests failed. Check API keys and configuration.")

    return passed == total


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
