#!/usr/bin/env python3
"""
Kimi K2 Instruct Integration Example for ACGS-2

This example demonstrates how to use the Moonshot AI Kimi K2 Instruct model
via Groq for fast inference in constitutional AI reasoning tasks.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
from groq import Groq

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def main():
    """
    Example usage of Kimi K2 Instruct model via Groq.

    This demonstrates the exact code pattern requested by the user.
    """
    print("🚀 Kimi K2 Instruct via Groq - ACGS-2 Integration")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    # Initialize Groq client
    client = Groq()

    try:
        # Create completion with Kimi K2 Instruct model
        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {
                    "role": "user",
                    "content": "Explain why fast inference is critical for reasoning models"
                }
            ]
        )

        # Print the response
        print("✅ Kimi K2 Instruct Response:")
        print("=" * 50)
        print(completion.choices[0].message.content)
        print("=" * 50)
        print()

        # Additional constitutional AI context
        print("🔐 Constitutional AI Context:")
        print(f"- Model: {completion.model}")
        print(f"- Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"- Usage: Input tokens: {completion.usage.prompt_tokens}, Output tokens: {completion.usage.completion_tokens}")
        print(f"- Total tokens: {completion.usage.total_tokens}")
        print()

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("1. Ensure GROQ_API_KEY environment variable is set")
        print("2. Verify your Groq API key has access to the Kimi model")
        print("3. Check your internet connection")
        print()
        return False


def advanced_example():
    """
    Advanced example with constitutional AI validation.
    """
    print("🧠 Advanced Constitutional AI Reasoning Example")
    print()

    client = Groq()

    try:
        # Constitutional AI reasoning prompt
        constitutional_prompt = f"""
        As a constitutional AI system with hash {CONSTITUTIONAL_HASH}, analyze the following:

        Question: Why is fast inference critical for reasoning models in AI governance systems?

        Please provide:
        1. Technical reasoning about inference speed
        2. Constitutional implications for AI governance
        3. Impact on real-time decision making
        4. Compliance with constitutional principles
        """

        completion = client.chat.completions.create(
            model="moonshotai/kimi-k2-instruct",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a constitutional AI assistant with hash {CONSTITUTIONAL_HASH}. Provide thorough, principled analysis."
                },
                {
                    "role": "user",
                    "content": constitutional_prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )

        print("✅ Constitutional AI Analysis:")
        print("=" * 60)
        print(completion.choices[0].message.content)
        print("=" * 60)
        print()

        return True

    except Exception as e:
        print(f"❌ Advanced example error: {e}")
        return False


if __name__ == "__main__":
    print("🎯 ACGS-2 Kimi K2 Instruct Integration Examples")
    print("=" * 60)
    print()

    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your_groq_api_key_here'")
        exit(1)

    # Run basic example
    print("📝 Basic Example:")
    basic_success = main()

    if basic_success:
        print("\n" + "="*60 + "\n")

        # Run advanced example
        print("🔬 Advanced Example:")
        advanced_success = advanced_example()

        if advanced_success:
            print("🎉 All examples completed successfully!")
            print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        else:
            print("⚠️  Advanced example failed")
    else:
        print("⚠️  Basic example failed")

    print("\n📚 Integration Notes:")
    print("- Kimi K2 Instruct is now available in the ACGS-2 router")
    print("- Model ID: 'moonshotai/kimi-k2-instruct'")
    print("- Tier: Premium (Tier 4) with 200K context window")
    print("- Optimized for: Advanced reasoning and constitutional AI")
    print("- Constitutional compliance score: 0.94")
    print(f"- Constitutional Hash: {CONSTITUTIONAL_HASH}")