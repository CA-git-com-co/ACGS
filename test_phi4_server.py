#!/usr/bin/env python3
"""
Test script for Phi-4 reasoning model running on llama.cpp server
"""

import json
import time

import requests


def test_server_connection(base_url="http://localhost:8080"):
    """Test if the server is running and responsive"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def chat_with_phi4(message, base_url="http://localhost:8080", stream=True):
    """Send a chat message to Phi-4 and get response"""

    # Official system prompt for Phi-4-reasoning-plus
    system_prompt = """You are Phi, a language model trained by Microsoft to help users. Your role as an assistant involves thoroughly exploring questions through a systematic thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered thinking process. Please structure your response into two main sections: Thought and Solution using the specified format: <think> {Thought section} </think> {Solution section}. In the Thought section, detail your reasoning process in steps. Each step should include detailed considerations such as analysing questions, summarizing relevant findings, brainstorming new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. In the Solution section, based on various attempts, explorations, and reflections from the Thought section, systematically present the final solution that you deem correct. The Solution section should be logical, accurate, and concise and detail necessary steps needed to reach the conclusion. Now, try to solve the following question through the above guidelines:"""

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "temperature": 0.8,
        "top_k": 50,
        "top_p": 0.95,
        "max_tokens": 4096,
        "stream": stream,
    }

    try:
        if stream:
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=300,
            )

            if response.status_code == 200:
                print(f"🤔 Question: {message}")
                print("🧠 Phi-4 Response:")
                print("-" * 60)

                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data.strip() == "[DONE]":
                                break
                            try:
                                json_data = json.loads(data)
                                if (
                                    "choices" in json_data
                                    and len(json_data["choices"]) > 0
                                ):
                                    delta = json_data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        print(content, end="", flush=True)
                            except json.JSONDecodeError:
                                continue

                print("\n" + "-" * 60)
                return True
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300,
        )

        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"🤔 Question: {message}")
            print("🧠 Phi-4 Response:")
            print("-" * 60)
            print(content)
            print("-" * 60)
            return True
        print(f"❌ Error: HTTP {response.status_code}")
        print(response.text)
        return False

    except Exception as e:
        print(f"❌ Error communicating with server: {e}")
        return False


def main():
    base_url = "http://localhost:8080"

    print("🔬 Phi-4 Reasoning Plus Model Test via llama.cpp Server")
    print("=" * 70)

    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    max_wait = 300  # 5 minutes
    wait_time = 0

    while wait_time < max_wait:
        if test_server_connection(base_url):
            print("✅ Server is ready!")
            break
        print(f"⏳ Still waiting... ({wait_time}s/{max_wait}s)")
        time.sleep(10)
        wait_time += 10
    else:
        print("❌ Server failed to start within timeout period")
        return 1

    # Test questions for reasoning capabilities
    test_questions = [
        "What is the derivative of x^2?",
        "Solve this step by step: If a train travels 60 miles per hour for 2 hours, how far does it travel?",
        "What is 15 * 23? Show your work step by step.",
        "Explain the concept of artificial intelligence in simple terms.",
        "If I have 5 apples and give away 2, then buy 3 more, how many apples do I have?",
    ]

    print("\n🧪 Running test questions...")

    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}/{len(test_questions)}")
        success = chat_with_phi4(question, base_url, stream=True)

        if not success:
            print(f"❌ Test {i} failed")
            continue

        print("\n✅ Test completed successfully!")

        # Small delay between tests
        if i < len(test_questions):
            print("⏳ Waiting 2 seconds before next test...")
            time.sleep(2)

    print("\n🎉 All tests completed!")
    print("\n💡 You can now interact with the model at:")
    print(f"   • API: {base_url}/v1/chat/completions")
    print(f"   • Web UI: {base_url}")

    return 0


if __name__ == "__main__":
    exit(main())
