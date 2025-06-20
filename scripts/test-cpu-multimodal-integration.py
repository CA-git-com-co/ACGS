#!/usr/bin/env python3
"""
ACGS-1 CPU-Only Multimodal Integration Test
Tests NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 model in CPU mode
"""

import os
import sys
import base64
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio

# Add the services directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "services" / "constitutional-document-analysis"))

try:
    from transformers import AutoImageProcessor, AutoModel, AutoTokenizer
    from PIL import Image
    import torch
    import numpy as np
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Please install: pip install transformers accelerate timm einops open-clip-torch pillow")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CPUMultimodalTester:
    """
    Test NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 model in CPU-only mode
    """
    
    def __init__(self):
        self.model_path = "nvidia/Llama-3.1-Nemotron-Nano-VL-8B-V1"
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.device = "cpu"
        
    def setup_model(self) -> bool:
        """
        Set up the multimodal model for CPU-only operation
        """
        try:
            logger.info("Setting up NVIDIA Llama-3.1-Nemotron-Nano-VL-8B-V1 model for CPU...")
            
            # Force CPU usage
            torch.cuda.is_available = lambda: False
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
            
            # Load tokenizer
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True
            )
            
            # Load image processor
            logger.info("Loading image processor...")
            self.image_processor = AutoImageProcessor.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                device=self.device
            )
            
            # Load model
            logger.info("Loading model (this may take several minutes)...")
            self.model = AutoModel.from_pretrained(
                self.model_path,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.float32  # Use float32 for CPU
            ).eval()
            
            logger.info("✅ Model setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Model setup failed: {str(e)}")
            return False
    
    def create_test_image(self) -> Image.Image:
        """
        Create a simple test image with constitutional text
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a white image
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # Add constitutional text
            constitutional_text = """
            ARTICLE II - EXECUTIVE BRANCH
            
            Section 1. The executive Power shall be vested in a 
            President of the United States of America. He shall 
            hold his Office during the Term of four Years, and, 
            together with the Vice President, chosen for the same 
            Term, be elected, as follows:
            
            Each State shall appoint, in such Manner as the 
            Legislature thereof may direct, a Number of Electors, 
            equal to the whole Number of Senators and 
            Representatives to which the State may be entitled 
            in the Congress.
            
            <watermark>OFFICIAL COPY</watermark>
            <page_number>1/5</page_number>
            """
            
            # Try to use a default font, fall back to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # Draw text
            y_position = 50
            for line in constitutional_text.strip().split('\n'):
                if line.strip():
                    draw.text((50, y_position), line.strip(), fill='black', font=font)
                    y_position += 25
            
            return img
            
        except Exception as e:
            logger.error(f"Failed to create test image: {str(e)}")
            # Return a simple colored image as fallback
            return Image.new('RGB', (400, 300), color='lightblue')
    
    def test_constitutional_ocr(self) -> Dict[str, Any]:
        """
        Test constitutional document OCR functionality
        """
        try:
            logger.info("Testing constitutional OCR functionality...")
            
            if not self.model:
                raise Exception("Model not initialized")
            
            # Create test image
            test_image = self.create_test_image()
            
            # Process image
            image_features = self.image_processor([test_image])
            
            # Create constitutional OCR prompt
            constitutional_prompt = """Extract the text from the above constitutional document as if you were reading it naturally. 

FORMATTING REQUIREMENTS:
- Return tables in HTML format with proper structure
- Return equations in LaTeX representation  
- Wrap watermarks in <watermark>TEXT</watermark> tags
- Wrap page numbers in <page_number>X</page_number> or <page_number>X/Y</page_number> tags
- Use ☐ for empty checkboxes and ☑ for checked boxes
- Preserve legal formatting including article numbers, section headers

CONSTITUTIONAL DOCUMENT SPECIFIC REQUIREMENTS:
- Identify and mark constitutional articles as <article number="X">content</article>
- Mark legal citations and wrap in <citation>text</citation>
- Identify rights and freedoms in <right>text</right> tags

QUALITY REQUIREMENTS:
- Maintain exact legal terminology and punctuation
- Preserve hierarchical structure (articles, sections, subsections)"""
            
            # Generate configuration
            generation_config = {
                'max_new_tokens': 1024,
                'do_sample': False,
                'eos_token_id': self.tokenizer.eos_token_id,
                'temperature': 0.0
            }
            
            start_time = time.time()
            
            # Generate response
            response = self.model.chat(
                tokenizer=self.tokenizer,
                question=constitutional_prompt,
                generation_config=generation_config,
                **image_features
            )
            
            processing_time = time.time() - start_time
            
            result = {
                "test_name": "constitutional_ocr",
                "status": "success",
                "processing_time": processing_time,
                "response": response,
                "response_length": len(response) if response else 0,
                "contains_watermark_tags": "<watermark>" in (response or ""),
                "contains_page_tags": "<page_number>" in (response or ""),
                "contains_article_tags": "<article" in (response or "")
            }
            
            logger.info(f"✅ Constitutional OCR test completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Constitutional OCR test failed: {str(e)}")
            return {
                "test_name": "constitutional_ocr",
                "status": "failed",
                "error": str(e),
                "processing_time": 0
            }
    
    def test_constitutional_qa(self) -> Dict[str, Any]:
        """
        Test constitutional Q&A functionality
        """
        try:
            logger.info("Testing constitutional Q&A functionality...")
            
            if not self.model:
                raise Exception("Model not initialized")
            
            # Create test image with constitutional content
            test_image = self.create_test_image()
            
            # Process image
            image_features = self.image_processor([test_image])
            
            # Constitutional question
            question = "What does Article II say about the executive power and presidential term?"
            
            # Generate configuration
            generation_config = {
                'max_new_tokens': 512,
                'do_sample': False,
                'eos_token_id': self.tokenizer.eos_token_id,
                'temperature': 0.1
            }
            
            start_time = time.time()
            
            # Generate response
            response = self.model.chat(
                tokenizer=self.tokenizer,
                question=question,
                generation_config=generation_config,
                **image_features
            )
            
            processing_time = time.time() - start_time
            
            result = {
                "test_name": "constitutional_qa",
                "status": "success",
                "question": question,
                "processing_time": processing_time,
                "response": response,
                "response_length": len(response) if response else 0,
                "mentions_executive_power": "executive" in (response or "").lower(),
                "mentions_president": "president" in (response or "").lower(),
                "mentions_term": "term" in (response or "").lower()
            }
            
            logger.info(f"✅ Constitutional Q&A test completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Constitutional Q&A test failed: {str(e)}")
            return {
                "test_name": "constitutional_qa",
                "status": "failed",
                "error": str(e),
                "processing_time": 0
            }
    
    def test_document_analysis(self) -> Dict[str, Any]:
        """
        Test document analysis capabilities
        """
        try:
            logger.info("Testing document analysis functionality...")
            
            if not self.model:
                raise Exception("Model not initialized")
            
            # Create test image
            test_image = self.create_test_image()
            
            # Process image
            image_features = self.image_processor([test_image])
            
            # Document analysis prompt
            analysis_prompt = """Analyze this constitutional document for:
1. Document structure and organization
2. Key constitutional principles mentioned
3. Any procedural requirements
4. Rights or powers described
5. Document authenticity indicators (watermarks, page numbers)

Provide a structured analysis with specific citations from the text."""
            
            # Generate configuration
            generation_config = {
                'max_new_tokens': 768,
                'do_sample': False,
                'eos_token_id': self.tokenizer.eos_token_id,
                'temperature': 0.0
            }
            
            start_time = time.time()
            
            # Generate response
            response = self.model.chat(
                tokenizer=self.tokenizer,
                question=analysis_prompt,
                generation_config=generation_config,
                **image_features
            )
            
            processing_time = time.time() - start_time
            
            result = {
                "test_name": "document_analysis",
                "status": "success",
                "processing_time": processing_time,
                "response": response,
                "response_length": len(response) if response else 0,
                "structured_analysis": "1." in (response or "") and "2." in (response or ""),
                "mentions_constitution": "constitution" in (response or "").lower(),
                "identifies_structure": "structure" in (response or "").lower()
            }
            
            logger.info(f"✅ Document analysis test completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Document analysis test failed: {str(e)}")
            return {
                "test_name": "document_analysis",
                "status": "failed",
                "error": str(e),
                "processing_time": 0
            }
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run all tests and compile results
        """
        logger.info("🚀 Starting comprehensive CPU-only multimodal integration tests...")
        
        start_time = time.time()
        
        # Setup model
        if not self.setup_model():
            return {
                "overall_status": "failed",
                "error": "Model setup failed",
                "total_time": time.time() - start_time
            }
        
        # Run tests
        test_results = []
        
        # Test 1: Constitutional OCR
        test_results.append(self.test_constitutional_ocr())
        
        # Test 2: Constitutional Q&A
        test_results.append(self.test_constitutional_qa())
        
        # Test 3: Document Analysis
        test_results.append(self.test_document_analysis())
        
        total_time = time.time() - start_time
        
        # Compile results
        successful_tests = [t for t in test_results if t.get("status") == "success"]
        failed_tests = [t for t in test_results if t.get("status") == "failed"]
        
        overall_result = {
            "overall_status": "success" if len(failed_tests) == 0 else "partial" if len(successful_tests) > 0 else "failed",
            "total_tests": len(test_results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(test_results) * 100,
            "total_time": total_time,
            "test_results": test_results,
            "system_info": {
                "device": self.device,
                "model_path": self.model_path,
                "torch_version": torch.__version__,
                "cpu_mode": True
            }
        }
        
        return overall_result

def main():
    """
    Main test execution function
    """
    print("🔬 ACGS-1 CPU-Only Multimodal Integration Test")
    print("=" * 60)
    
    tester = CPUMultimodalTester()
    results = tester.run_comprehensive_tests()
    
    # Print results
    print(f"\n📊 Test Results Summary:")
    print(f"Overall Status: {results['overall_status'].upper()}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Total Time: {results['total_time']:.2f} seconds")
    print(f"Tests: {results['successful_tests']}/{results['total_tests']} passed")
    
    print(f"\n📋 Individual Test Results:")
    for test in results['test_results']:
        status_icon = "✅" if test['status'] == 'success' else "❌"
        print(f"{status_icon} {test['test_name']}: {test['status']}")
        if test['status'] == 'success':
            print(f"   Processing time: {test['processing_time']:.2f}s")
            if 'response_length' in test:
                print(f"   Response length: {test['response_length']} characters")
        else:
            print(f"   Error: {test.get('error', 'Unknown error')}")
    
    # Save results to file
    results_file = Path(__file__).parent / "cpu_multimodal_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return results['overall_status'] == 'success'

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
