#!/usr/bin/env python3
"""
Simple test script for Microsoft Phi-4 reasoning model with ONNX Runtime GenAI
"""

import onnxruntime_genai as og
import argparse
import sys

def test_phi4_model(model_path, execution_provider="cpu"):
    """Test the Phi-4 model with a simple question"""
    
    print(f"🚀 Loading Phi-4 model from: {model_path}")
    print(f"📊 Execution provider: {execution_provider}")
    
    try:
        # Load model configuration
        config = og.Config(model_path)
        
        # Set execution provider
        if execution_provider != "follow_config":
            config.clear_providers()
            if execution_provider != "cpu":
                print(f"Setting execution provider to: {execution_provider}")
                config.append_provider(execution_provider)
        
        # Load the model
        model = og.Model(config)
        print("✅ Model loaded successfully!")
        
        # Create tokenizer
        tokenizer = og.Tokenizer(model)
        print("✅ Tokenizer created successfully!")
        
        # Test questions
        test_questions = [
            "What is 2 + 2?",
            "Explain the concept of artificial intelligence in one sentence.",
            "What is the capital of France?",
            "Solve this step by step: If a train travels 60 miles per hour for 2 hours, how far does it travel?"
        ]
        
        # Generation parameters
        search_options = {
            'max_length': 512,
            'temperature': 0.7,
            'top_p': 0.9,
            'do_sample': True
        }
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🤔 Question {i}: {question}")
            print("🧠 Thinking...")
            
            try:
                # Create input prompt (simple format for testing)
                input_tokens = tokenizer.encode(f"Question: {question}\nAnswer:")
                
                # Set up generator
                params = og.GeneratorParams(model)
                params.set_search_options(**search_options)
                generator = og.Generator(model, params)
                generator.append_tokens(input_tokens)
                
                # Generate response
                print("💭 Response: ", end='', flush=True)
                
                response_tokens = []
                while not generator.is_done():
                    generator.generate_next_token()
                    new_token = generator.get_next_tokens()[0]
                    response_tokens.append(new_token)
                    
                    # Decode and print token
                    token_text = tokenizer.decode([new_token])
                    print(token_text, end='', flush=True)
                    
                    # Stop if we hit a natural stopping point
                    if len(response_tokens) > 100:  # Limit response length for testing
                        break
                
                print("\n" + "="*60)
                
            except Exception as e:
                print(f"❌ Error generating response: {e}")
                continue
        
        print("\n🎉 Phi-4 model test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test Microsoft Phi-4 reasoning model")
    parser.add_argument('-m', '--model_path', type=str, required=True, 
                       help='Path to the ONNX model directory')
    parser.add_argument('-e', '--execution_provider', type=str, default='cpu',
                       choices=['cpu', 'cuda', 'dml'], 
                       help='Execution provider (default: cpu)')
    
    args = parser.parse_args()
    
    print("🔬 Microsoft Phi-4 Reasoning Model Test")
    print("="*50)
    
    success = test_phi4_model(args.model_path, args.execution_provider)
    
    if success:
        print("\n✅ All tests passed! Phi-4 model is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the model setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
