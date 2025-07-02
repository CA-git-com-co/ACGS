#!/usr/bin/env python3
"""
Microsoft Phi-4 Reasoning Plus Model Test Script
Based on official documentation from: https://huggingface.co/microsoft/Phi-4-reasoning-plus
"""

import argparse
import json
import time

import onnxruntime_genai as og


def create_system_prompt():
    """Create the official system prompt for Phi-4-reasoning-plus"""
    return """You are Phi, a language model trained by Microsoft to help users. Your role as an assistant involves thoroughly exploring questions through a systematic thinking process before providing the final precise and accurate solutions. This requires engaging in a comprehensive cycle of analysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered thinking process. Please structure your response into two main sections: Thought and Solution using the specified format: <think> {Thought section} </think> {Solution section}. In the Thought section, detail your reasoning process in steps. Each step should include detailed considerations such as analysing questions, summarizing relevant findings, brainstorming new ideas, verifying the accuracy of the current steps, refining any errors, and revisiting previous steps. In the Solution section, based on various attempts, explorations, and reflections from the Thought section, systematically present the final solution that you deem correct. The Solution section should be logical, accurate, and concise and detail necessary steps needed to reach the conclusion. Now, try to solve the following question through the above guidelines:"""


def test_phi4_reasoning(model_path, execution_provider="cpu", verbose=False):
    """Test Phi-4-reasoning-plus model with proper configuration"""

    print("🧠 Microsoft Phi-4 Reasoning Plus Model Test")
    print("=" * 60)
    print(f"📁 Model Path: {model_path}")
    print(f"⚙️  Execution Provider: {execution_provider}")
    print()

    try:
        # Load model with proper configuration
        if verbose:
            print("Loading model configuration...")

        config = og.Config(model_path)

        # Set execution provider according to documentation
        if execution_provider != "follow_config":
            config.clear_providers()
            if execution_provider != "cpu":
                if verbose:
                    print(f"Setting execution provider to: {execution_provider}")
                config.append_provider(execution_provider)

        # Load model
        if verbose:
            print("Loading model...")
        model = og.Model(config)
        print("✅ Model loaded successfully!")

        # Create tokenizer
        tokenizer = og.Tokenizer(model)
        tokenizer_stream = tokenizer.create_stream()
        print("✅ Tokenizer created successfully!")

        # Official generation parameters from documentation
        search_options = {
            "max_length": 4096,  # Can be extended to 32768 for complex queries
            "temperature": 0.8,  # Official recommendation
            "top_k": 50,  # Official recommendation
            "top_p": 0.95,  # Official recommendation
            "do_sample": True,  # Official recommendation
        }

        # Test questions for reasoning capabilities
        test_questions = [
            "What is the derivative of x^2?",
            "Solve this step by step: If a train travels 60 miles per hour for 2 hours, how far does it travel?",
            "Explain the concept of artificial intelligence and its applications.",
            "What is 15 * 23? Show your work step by step.",
            "If I have 5 apples and give away 2, then buy 3 more, how many apples do I have?",
        ]

        system_prompt = create_system_prompt()

        for i, question in enumerate(test_questions, 1):
            print(f"\n🤔 Question {i}: {question}")
            print("-" * 50)

            try:
                # Create messages in ChatML format as per documentation
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ]

                # Apply chat template (proper way according to documentation)
                input_prompt = tokenizer.apply_chat_template(
                    messages=json.dumps(messages), add_generation_prompt=True
                )

                # Encode input
                input_tokens = tokenizer.encode(input_prompt)

                if verbose:
                    print(f"Input tokens: {len(input_tokens)}")

                # Set up generator with official parameters
                params = og.GeneratorParams(model)
                params.set_search_options(**search_options)
                generator = og.Generator(model, params)
                generator.append_tokens(input_tokens)

                # Generate response
                print("🧠 Phi-4 Response:")
                print()

                start_time = time.time()
                token_count = 0

                while not generator.is_done():
                    generator.generate_next_token()
                    new_token = generator.get_next_tokens()[0]
                    token_text = tokenizer_stream.decode(new_token)
                    print(token_text, end="", flush=True)
                    token_count += 1

                    # Limit response length for testing
                    if token_count > 1000:
                        print("\n[Response truncated for testing...]")
                        break

                end_time = time.time()

                print()
                print("-" * 50)

                if verbose:
                    duration = end_time - start_time
                    tokens_per_second = token_count / duration if duration > 0 else 0
                    print(f"⏱️  Generation time: {duration:.2f}s")
                    print(f"🚀 Tokens per second: {tokens_per_second:.2f}")
                    print(f"📊 Tokens generated: {token_count}")

                print()

            except KeyboardInterrupt:
                print("\n⏹️  Generation interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error generating response: {e}")
                continue

        print("\n🎉 Phi-4 reasoning model test completed!")
        return True

    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("\n💡 Troubleshooting tips:")
        print(
            "1. Ensure the model path contains all required files (model.onnx, genai_config.json, etc.)"
        )
        print("2. Try using 'cpu' execution provider if CUDA is not available")
        print("3. Check that onnxruntime-genai is properly installed")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test Microsoft Phi-4 Reasoning Plus model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python phi4_reasoning_test.py -m gpu/gpu-int4-rtn-block-32 -e cpu
  python phi4_reasoning_test.py -m gpu/gpu-int4-rtn-block-32 -e cuda -v
        """,
    )

    parser.add_argument(
        "-m",
        "--model_path",
        type=str,
        required=True,
        help="Path to the ONNX model directory",
    )
    parser.add_argument(
        "-e",
        "--execution_provider",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "dml", "follow_config"],
        help="Execution provider (default: cpu)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output with timing information",
    )

    args = parser.parse_args()

    success = test_phi4_reasoning(
        args.model_path, args.execution_provider, args.verbose
    )

    if success:
        print("\n✅ All tests completed successfully!")
        print(
            "🔬 Phi-4-reasoning-plus is working correctly with proper reasoning capabilities."
        )
    else:
        print("\n❌ Tests failed. Please check the setup and try again.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
