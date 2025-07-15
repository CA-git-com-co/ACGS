#!/usr/bin/env python3
"""
ACGS-2 Training Data Generation CLI

This script provides a command-line interface for generating and downloading
training data for the Autonomous Constitutional Governance System (ACGS-2).

Usage:
    python generate_training_data.py --help
    python generate_training_data.py --generate-all --size 5000
    python generate_training_data.py --download-external --categories constitutional_ai policy_governance
    python generate_training_data.py --constitutional-hash cdd01ef066bc6cf2 --validate

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.shared.training_data.training_data_generator import (
    TrainingDataGenerator,
    DatasetConfig,
    DatasetType,
    DataQuality
)
from services.shared.training_data.external_dataset_downloader import (
    ExternalDatasetDownloader
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingDataCLI:
    """Command-line interface for ACGS-2 training data generation."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.generator = None
        self.downloader = None
        
    def setup_generator(self, output_dir: str, config_file: Optional[str] = None):
        """Setup training data generator."""
        self.generator = TrainingDataGenerator(output_dir, config_file)
        logger.info(f"Training data generator initialized with output_dir: {output_dir}")
    
    def setup_downloader(self, download_dir: str, max_size_gb: float = 10.0):
        """Setup external dataset downloader."""
        self.downloader = ExternalDatasetDownloader(download_dir, max_size_gb)
        logger.info(f"External dataset downloader initialized with download_dir: {download_dir}")

    async def generate_all_datasets(
        self, 
        size: int = 1000, 
        quality: str = "synthetic",
        output_format: str = "json"
    ) -> dict:
        """Generate all types of training datasets."""
        if not self.generator:
            raise ValueError("Generator not initialized. Call setup_generator() first.")
        
        logger.info(f"🚀 Generating all ACGS-2 training datasets")
        logger.info(f"📊 Configuration: size={size}, quality={quality}, format={output_format}")
        logger.info(f"🔒 Constitutional Hash: {self.constitutional_hash}")
        
        # Create dataset configurations
        dataset_types = [
            DatasetType.CONSTITUTIONAL_AI,
            DatasetType.POLICY_GOVERNANCE,
            DatasetType.MULTI_AGENT_COORDINATION,
            DatasetType.PERFORMANCE_OPTIMIZATION,
            DatasetType.TRANSFORMER_EFFICIENCY,
            DatasetType.WINA_OPTIMIZATION
        ]
        
        configs = []
        for dataset_type in dataset_types:
            config = DatasetConfig(
                dataset_type=dataset_type,
                size=size,
                quality_level=DataQuality(quality),
                output_format=output_format,
                include_metadata=True,
                constitutional_compliance=True
            )
            configs.append(config)
        
        # Generate datasets
        start_time = time.time()
        results = await self.generator.generate_all_datasets(configs)
        generation_time = time.time() - start_time
        
        # Add timing information
        results["generation_time_seconds"] = generation_time
        results["constitutional_hash"] = self.constitutional_hash
        
        logger.info(f"✅ All datasets generated in {generation_time:.2f} seconds")
        return results

    async def generate_specific_dataset(
        self, 
        dataset_type: str, 
        size: int = 1000,
        quality: str = "synthetic",
        output_format: str = "json"
    ) -> dict:
        """Generate a specific type of dataset."""
        if not self.generator:
            raise ValueError("Generator not initialized. Call setup_generator() first.")
        
        try:
            dtype = DatasetType(dataset_type)
        except ValueError:
            raise ValueError(f"Invalid dataset type: {dataset_type}")
        
        logger.info(f"🎯 Generating {dataset_type} dataset (size: {size})")
        
        config = DatasetConfig(
            dataset_type=dtype,
            size=size,
            quality_level=DataQuality(quality),
            output_format=output_format,
            constitutional_compliance=True
        )
        
        start_time = time.time()
        results = await self.generator.generate_all_datasets([config])
        generation_time = time.time() - start_time
        
        results["generation_time_seconds"] = generation_time
        results["constitutional_hash"] = self.constitutional_hash
        
        logger.info(f"✅ {dataset_type} dataset generated in {generation_time:.2f} seconds")
        return results

    async def download_external_datasets(
        self, 
        categories: Optional[List[str]] = None
    ) -> dict:
        """Download external datasets."""
        if not self.downloader:
            raise ValueError("Downloader not initialized. Call setup_downloader() first.")
        
        logger.info(f"📥 Downloading external datasets")
        if categories:
            logger.info(f"📂 Categories: {', '.join(categories)}")
        else:
            logger.info(f"📂 Categories: all available")
        
        start_time = time.time()
        results = await self.downloader.download_all_datasets(categories)
        download_time = time.time() - start_time
        
        results["download_time_seconds"] = download_time
        results["constitutional_hash"] = self.constitutional_hash
        
        logger.info(f"✅ External datasets downloaded in {download_time:.2f} seconds")
        return results

    def validate_constitutional_compliance(self, data_dir: str) -> dict:
        """Validate constitutional compliance of generated data."""
        logger.info(f"🔍 Validating constitutional compliance in {data_dir}")
        
        data_path = Path(data_dir)
        if not data_path.exists():
            raise ValueError(f"Data directory does not exist: {data_dir}")
        
        validation_results = {
            "constitutional_hash": self.constitutional_hash,
            "validation_timestamp": time.time(),
            "total_files": 0,
            "compliant_files": 0,
            "non_compliant_files": 0,
            "validation_details": []
        }
        
        # Check all JSON files for constitutional hash
        for json_file in data_path.rglob("*.json"):
            validation_results["total_files"] += 1
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Check for constitutional hash in data
                has_hash = self._check_constitutional_hash(data)
                
                file_result = {
                    "file": str(json_file.relative_to(data_path)),
                    "compliant": has_hash,
                    "size_mb": json_file.stat().st_size / (1024 * 1024)
                }
                
                if has_hash:
                    validation_results["compliant_files"] += 1
                else:
                    validation_results["non_compliant_files"] += 1
                    file_result["issue"] = "Missing constitutional hash"
                
                validation_results["validation_details"].append(file_result)
                
            except Exception as e:
                validation_results["non_compliant_files"] += 1
                validation_results["validation_details"].append({
                    "file": str(json_file.relative_to(data_path)),
                    "compliant": False,
                    "error": str(e)
                })
        
        # Calculate compliance rate
        if validation_results["total_files"] > 0:
            compliance_rate = validation_results["compliant_files"] / validation_results["total_files"]
            validation_results["compliance_rate"] = compliance_rate
            
            if compliance_rate >= 0.95:
                logger.info(f"✅ Constitutional compliance: {compliance_rate:.1%} (PASS)")
            else:
                logger.warning(f"⚠️ Constitutional compliance: {compliance_rate:.1%} (NEEDS ATTENTION)")
        else:
            logger.warning("⚠️ No files found for validation")
        
        return validation_results

    def _check_constitutional_hash(self, data: any) -> bool:
        """Recursively check for constitutional hash in data structure."""
        if isinstance(data, dict):
            if "constitutional_hash" in data:
                return data["constitutional_hash"] == self.constitutional_hash
            return any(self._check_constitutional_hash(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._check_constitutional_hash(item) for item in data)
        return False

    def print_summary(self, results: dict):
        """Print a formatted summary of results."""
        print("\n" + "="*70)
        print("🎯 ACGS-2 Training Data Generation Summary")
        print("="*70)
        print(f"🔒 Constitutional Hash: {results.get('constitutional_hash', 'N/A')}")
        
        if "generation_time_seconds" in results:
            print(f"⏱️ Generation Time: {results['generation_time_seconds']:.2f} seconds")
        
        if "download_time_seconds" in results:
            print(f"📥 Download Time: {results['download_time_seconds']:.2f} seconds")
        
        if "summary_report" in results:
            print(f"📊 Summary Report: {results['summary_report']}")
        
        if "report_path" in results:
            print(f"📋 Download Report: {results['report_path']}")
        
        # Dataset-specific information
        if "test_results" in results:
            print("\n📈 Generated Datasets:")
            for dataset_type, path in results.items():
                if dataset_type not in ["constitutional_hash", "generation_time_seconds", "summary_report"]:
                    status = "✅" if not path.startswith("ERROR") else "❌"
                    print(f"  {status} {dataset_type}: {path}")
        
        # Download-specific information
        if "download_summary" in results:
            print("\n📥 Downloaded Datasets:")
            for category, info in results["download_summary"].items():
                success_rate = info["successful_downloads"] / info["total_datasets"] if info["total_datasets"] > 0 else 0
                status = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.5 else "❌"
                print(f"  {status} {category}: {info['successful_downloads']}/{info['total_datasets']} datasets ({info['total_size_mb']:.1f} MB)")
        
        # Validation information
        if "compliance_rate" in results:
            compliance_rate = results["compliance_rate"]
            status = "✅" if compliance_rate >= 0.95 else "⚠️" if compliance_rate >= 0.8 else "❌"
            print(f"\n🔍 Constitutional Compliance: {status} {compliance_rate:.1%} ({results['compliant_files']}/{results['total_files']} files)")
        
        print("="*70)


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="ACGS-2 Training Data Generation and Download Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Generate all datasets with 5000 examples each
  python {Path(__file__).name} --generate-all --size 5000

  # Generate only constitutional AI data
  python {Path(__file__).name} --generate constitutional_ai --size 2000

  # Download external datasets
  python {Path(__file__).name} --download-external --categories constitutional_ai policy_governance

  # Validate constitutional compliance
  python {Path(__file__).name} --validate --data-dir ./training_data

Constitutional Hash: {CONSTITUTIONAL_HASH}
        """
    )
    
    # Main action arguments
    parser.add_argument("--generate-all", action="store_true",
                       help="Generate all types of training datasets")
    parser.add_argument("--generate", type=str, metavar="DATASET_TYPE",
                       help="Generate specific dataset type")
    parser.add_argument("--download-external", action="store_true",
                       help="Download external datasets")
    parser.add_argument("--validate", action="store_true",
                       help="Validate constitutional compliance of existing data")
    
    # Configuration arguments
    parser.add_argument("--size", type=int, default=1000,
                       help="Number of examples to generate per dataset (default: 1000)")
    parser.add_argument("--quality", type=str, default="synthetic",
                       choices=["high", "medium", "low", "synthetic"],
                       help="Quality level of generated data (default: synthetic)")
    parser.add_argument("--output-format", type=str, default="json",
                       choices=["json", "csv", "parquet"],
                       help="Output format for generated data (default: json)")
    parser.add_argument("--output-dir", type=str, default="training_data",
                       help="Output directory for generated data (default: training_data)")
    parser.add_argument("--download-dir", type=str, default="external_datasets",
                       help="Download directory for external datasets (default: external_datasets)")
    parser.add_argument("--data-dir", type=str, default="training_data",
                       help="Data directory for validation (default: training_data)")
    parser.add_argument("--categories", type=str, nargs="+",
                       help="Categories of external datasets to download")
    parser.add_argument("--max-size-gb", type=float, default=10.0,
                       help="Maximum size in GB for external dataset downloads (default: 10.0)")
    parser.add_argument("--config-file", type=str,
                       help="Configuration file for training data generation")
    
    # Validation arguments
    parser.add_argument("--constitutional-hash", type=str, default=CONSTITUTIONAL_HASH,
                       help=f"Constitutional hash for validation (default: {CONSTITUTIONAL_HASH})")
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = TrainingDataCLI()
    
    # Validate constitutional hash
    if args.constitutional_hash != CONSTITUTIONAL_HASH:
        logger.error(f"❌ Invalid constitutional hash: {args.constitutional_hash}")
        logger.error(f"   Expected: {CONSTITUTIONAL_HASH}")
        sys.exit(1)
    
    try:
        results = {}
        
        # Generate all datasets
        if args.generate_all:
            cli.setup_generator(args.output_dir, args.config_file)
            results = await cli.generate_all_datasets(
                size=args.size,
                quality=args.quality,
                output_format=args.output_format
            )
        
        # Generate specific dataset
        elif args.generate:
            cli.setup_generator(args.output_dir, args.config_file)
            results = await cli.generate_specific_dataset(
                dataset_type=args.generate,
                size=args.size,
                quality=args.quality,
                output_format=args.output_format
            )
        
        # Download external datasets
        elif args.download_external:
            cli.setup_downloader(args.download_dir, args.max_size_gb)
            results = await cli.download_external_datasets(args.categories)
        
        # Validate constitutional compliance
        elif args.validate:
            results = cli.validate_constitutional_compliance(args.data_dir)
        
        else:
            parser.print_help()
            sys.exit(1)
        
        # Print summary
        cli.print_summary(results)
        
        # Save results
        results_file = Path(args.output_dir) / "generation_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📄 Results saved to: {results_file}")
        
    except Exception as e:
        logger.exception(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
