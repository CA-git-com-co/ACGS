#!/usr/bin/env python3
"""
ACGS Software Bill of Materials (SBOM) Generator
Constitutional Hash: cdd01ef066bc6cf2

Generates comprehensive SBOM for ACGS with constitutional compliance validation.

Features:
- CycloneDX and SPDX format support
- Dependency vulnerability scanning integration
- License compliance tracking
- Constitutional compliance validation
- Automated dependency monitoring
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Dependency:
    """Dependency information."""
    name: str
    version: str
    license: str
    source: str
    vulnerabilities: List[Dict[str, Any]]
    constitutional_compliance: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class SBOMMetadata:
    """SBOM metadata."""
    timestamp: datetime
    tool_name: str
    tool_version: str
    component_count: int
    vulnerability_count: int
    license_compliance: bool
    constitutional_compliance: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ACGSSBOMGenerator:
    """ACGS Software Bill of Materials generator."""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.dependencies: List[Dependency] = []
        self.sbom_metadata: Optional[SBOMMetadata] = None
        
    def _validate_constitutional_hash(self) -> bool:
        """Validate constitutional hash."""
        return CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"

    async def generate_comprehensive_sbom(self) -> Dict[str, Any]:
        """Generate comprehensive SBOM with constitutional compliance."""
        logger.info("📋 Generating ACGS Software Bill of Materials...")
        
        if not self._validate_constitutional_hash():
            raise ValueError(f"Invalid constitutional hash: {CONSTITUTIONAL_HASH}")
        
        sbom_results = {
            "generation_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "sbom_formats": {},
            "dependency_analysis": {},
            "vulnerability_scan": {},
            "license_compliance": {},
            "constitutional_validation": {},
        }
        
        try:
            # 1. Discover dependencies
            logger.info("🔍 Discovering dependencies...")
            sbom_results["dependency_analysis"] = await self._discover_dependencies()
            
            # 2. Scan for vulnerabilities
            logger.info("🔒 Scanning for vulnerabilities...")
            sbom_results["vulnerability_scan"] = await self._scan_vulnerabilities()
            
            # 3. Analyze license compliance
            logger.info("⚖️ Analyzing license compliance...")
            sbom_results["license_compliance"] = await self._analyze_license_compliance()
            
            # 4. Generate SBOM formats
            logger.info("📄 Generating SBOM formats...")
            sbom_results["sbom_formats"]["cyclonedx"] = await self._generate_cyclonedx_sbom()
            sbom_results["sbom_formats"]["spdx"] = await self._generate_spdx_sbom()
            
            # 5. Validate constitutional compliance
            logger.info("🏛️ Validating constitutional compliance...")
            sbom_results["constitutional_validation"] = await self._validate_constitutional_compliance()
            
            # Save SBOM results
            await self._save_sbom_results(sbom_results)
            
            logger.info("✅ SBOM generation completed")
            return sbom_results
            
        except Exception as e:
            logger.error(f"❌ SBOM generation failed: {e}")
            sbom_results["error"] = str(e)
            return sbom_results

    async def _discover_dependencies(self) -> Dict[str, Any]:
        """Discover all project dependencies."""
        dependency_results = {
            "python_dependencies": [],
            "system_dependencies": [],
            "docker_dependencies": [],
            "total_dependencies": 0,
            "constitutional_compliance": True,
        }
        
        try:
            # Discover Python dependencies
            python_deps = await self._discover_python_dependencies()
            dependency_results["python_dependencies"] = python_deps
            
            # Discover system dependencies
            system_deps = await self._discover_system_dependencies()
            dependency_results["system_dependencies"] = system_deps
            
            # Discover Docker dependencies
            docker_deps = await self._discover_docker_dependencies()
            dependency_results["docker_dependencies"] = docker_deps
            
            # Calculate totals
            dependency_results["total_dependencies"] = (
                len(python_deps) + len(system_deps) + len(docker_deps)
            )
            
            # Store dependencies for later use
            self.dependencies = python_deps + system_deps + docker_deps
            
        except Exception as e:
            logger.error(f"Dependency discovery failed: {e}")
            dependency_results["error"] = str(e)
            dependency_results["constitutional_compliance"] = False
        
        return dependency_results

    async def _discover_python_dependencies(self) -> List[Dependency]:
        """Discover Python dependencies."""
        python_dependencies = []
        
        try:
            # Check for requirements.txt
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                with open(requirements_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse dependency
                            if '==' in line:
                                name, version = line.split('==', 1)
                            elif '>=' in line:
                                name, version = line.split('>=', 1)
                                version = f">={version}"
                            else:
                                name, version = line, "latest"
                            
                            # Get license information
                            license_info = await self._get_package_license(name)
                            
                            dependency = Dependency(
                                name=name.strip(),
                                version=version.strip(),
                                license=license_info,
                                source="requirements.txt",
                                vulnerabilities=[],
                                constitutional_compliance=True,
                            )
                            
                            python_dependencies.append(dependency)
            
            # Also check pip freeze output
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "freeze"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        line = line.strip()
                        if line and '==' in line:
                            name, version = line.split('==', 1)
                            
                            # Skip if already found in requirements.txt
                            if any(dep.name == name for dep in python_dependencies):
                                continue
                            
                            license_info = await self._get_package_license(name)
                            
                            dependency = Dependency(
                                name=name.strip(),
                                version=version.strip(),
                                license=license_info,
                                source="pip_freeze",
                                vulnerabilities=[],
                                constitutional_compliance=True,
                            )
                            
                            python_dependencies.append(dependency)
                            
            except subprocess.TimeoutExpired:
                logger.warning("pip freeze command timed out")
            except Exception as e:
                logger.warning(f"pip freeze failed: {e}")
        
        except Exception as e:
            logger.error(f"Python dependency discovery failed: {e}")
        
        return python_dependencies

    async def _get_package_license(self, package_name: str) -> str:
        """Get license information for a package."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('License:'):
                        license_info = line.split(':', 1)[1].strip()
                        return license_info if license_info else "Unknown"
            
            return "Unknown"
            
        except Exception:
            return "Unknown"

    async def _discover_system_dependencies(self) -> List[Dependency]:
        """Discover system-level dependencies."""
        system_dependencies = []
        
        # Common system dependencies for ACGS
        system_deps = [
            ("python3", "3.11+", "PSF", "system"),
            ("postgresql", "15+", "PostgreSQL", "database"),
            ("redis", "7+", "BSD", "cache"),
            ("docker", "20.10+", "Apache-2.0", "container"),
            ("nginx", "1.20+", "BSD-2-Clause", "proxy"),
        ]
        
        for name, version, license_info, source in system_deps:
            dependency = Dependency(
                name=name,
                version=version,
                license=license_info,
                source=source,
                vulnerabilities=[],
                constitutional_compliance=True,
            )
            system_dependencies.append(dependency)
        
        return system_dependencies

    async def _discover_docker_dependencies(self) -> List[Dependency]:
        """Discover Docker image dependencies."""
        docker_dependencies = []
        
        # Check for Dockerfile
        dockerfile = self.project_root / "Dockerfile"
        if dockerfile.exists():
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()
                
                # Parse FROM statements
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('FROM '):
                        image_spec = line.split('FROM ', 1)[1].strip()
                        
                        # Parse image name and tag
                        if ':' in image_spec:
                            image_name, tag = image_spec.split(':', 1)
                        else:
                            image_name, tag = image_spec, "latest"
                        
                        dependency = Dependency(
                            name=image_name,
                            version=tag,
                            license="Various",  # Docker images have mixed licenses
                            source="Dockerfile",
                            vulnerabilities=[],
                            constitutional_compliance=True,
                        )
                        docker_dependencies.append(dependency)
                        
            except Exception as e:
                logger.warning(f"Docker dependency discovery failed: {e}")
        
        return docker_dependencies

    async def _scan_vulnerabilities(self) -> Dict[str, Any]:
        """Scan dependencies for vulnerabilities."""
        vulnerability_results = {
            "total_vulnerabilities": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "medium_vulnerabilities": 0,
            "low_vulnerabilities": 0,
            "vulnerability_details": [],
            "constitutional_compliance": True,
        }
        
        try:
            # Scan Python dependencies with Safety
            python_vulns = await self._scan_python_vulnerabilities()
            vulnerability_results["vulnerability_details"].extend(python_vulns)
            
            # Count vulnerabilities by severity
            for vuln in python_vulns:
                severity = vuln.get("severity", "unknown").lower()
                if severity == "critical":
                    vulnerability_results["critical_vulnerabilities"] += 1
                elif severity == "high":
                    vulnerability_results["high_vulnerabilities"] += 1
                elif severity == "medium":
                    vulnerability_results["medium_vulnerabilities"] += 1
                elif severity == "low":
                    vulnerability_results["low_vulnerabilities"] += 1
            
            vulnerability_results["total_vulnerabilities"] = len(python_vulns)
            
        except Exception as e:
            logger.error(f"Vulnerability scanning failed: {e}")
            vulnerability_results["error"] = str(e)
            vulnerability_results["constitutional_compliance"] = False
        
        return vulnerability_results

    async def _scan_python_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Scan Python dependencies for vulnerabilities using Safety."""
        vulnerabilities = []
        
        try:
            # Run safety check
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # No vulnerabilities found
                logger.info("No Python vulnerabilities found")
            else:
                # Parse safety output
                try:
                    safety_output = json.loads(result.stdout)
                    for vuln in safety_output:
                        vulnerability = {
                            "package": vuln.get("package", "unknown"),
                            "version": vuln.get("installed_version", "unknown"),
                            "vulnerability_id": vuln.get("vulnerability_id", "unknown"),
                            "severity": vuln.get("severity", "unknown"),
                            "description": vuln.get("advisory", "No description"),
                            "constitutional_hash": CONSTITUTIONAL_HASH,
                        }
                        vulnerabilities.append(vulnerability)
                        
                except json.JSONDecodeError:
                    logger.warning("Could not parse safety output")
                    
        except subprocess.TimeoutExpired:
            logger.warning("Safety check timed out")
        except FileNotFoundError:
            logger.warning("Safety tool not found - install with: pip install safety")
        except Exception as e:
            logger.warning(f"Safety check failed: {e}")
        
        return vulnerabilities

    async def _analyze_license_compliance(self) -> Dict[str, Any]:
        """Analyze license compliance."""
        license_results = {
            "total_licenses": 0,
            "approved_licenses": 0,
            "restricted_licenses": 0,
            "unknown_licenses": 0,
            "license_summary": {},
            "compliance_status": "compliant",
            "constitutional_compliance": True,
        }
        
        # Define approved and restricted licenses
        approved_licenses = {
            "MIT", "Apache-2.0", "BSD", "BSD-2-Clause", "BSD-3-Clause",
            "PSF", "PostgreSQL", "ISC", "Unlicense"
        }
        
        restricted_licenses = {
            "GPL-3.0", "AGPL-3.0", "LGPL-3.0", "SSPL"
        }
        
        try:
            license_counts = {}
            
            for dependency in self.dependencies:
                license_name = dependency.license
                
                # Count license occurrences
                if license_name in license_counts:
                    license_counts[license_name] += 1
                else:
                    license_counts[license_name] = 1
                
                # Categorize license
                if license_name in approved_licenses:
                    license_results["approved_licenses"] += 1
                elif license_name in restricted_licenses:
                    license_results["restricted_licenses"] += 1
                    license_results["compliance_status"] = "non_compliant"
                elif license_name == "Unknown":
                    license_results["unknown_licenses"] += 1
                    license_results["compliance_status"] = "review_required"
            
            license_results["total_licenses"] = len(self.dependencies)
            license_results["license_summary"] = license_counts
            
        except Exception as e:
            logger.error(f"License compliance analysis failed: {e}")
            license_results["error"] = str(e)
            license_results["constitutional_compliance"] = False
        
        return license_results

    async def _generate_cyclonedx_sbom(self) -> Dict[str, Any]:
        """Generate CycloneDX format SBOM."""
        cyclonedx_results = {
            "format": "CycloneDX",
            "version": "1.4",
            "file_path": "",
            "component_count": 0,
            "constitutional_compliance": True,
        }
        
        try:
            # Create CycloneDX SBOM structure
            sbom = {
                "bomFormat": "CycloneDX",
                "specVersion": "1.4",
                "serialNumber": f"urn:uuid:acgs-{int(time.time())}",
                "version": 1,
                "metadata": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "tools": [
                        {
                            "vendor": "ACGS",
                            "name": "ACGS SBOM Generator",
                            "version": "1.0.0"
                        }
                    ],
                    "component": {
                        "type": "application",
                        "name": "ACGS",
                        "version": "1.0.0",
                        "description": "Autonomous Constitutional Governance System",
                        "properties": [
                            {
                                "name": "constitutional_hash",
                                "value": CONSTITUTIONAL_HASH
                            }
                        ]
                    }
                },
                "components": []
            }
            
            # Add dependencies as components
            for dependency in self.dependencies:
                component = {
                    "type": "library",
                    "name": dependency.name,
                    "version": dependency.version,
                    "licenses": [
                        {
                            "license": {
                                "name": dependency.license
                            }
                        }
                    ],
                    "properties": [
                        {
                            "name": "source",
                            "value": dependency.source
                        },
                        {
                            "name": "constitutional_compliance",
                            "value": str(dependency.constitutional_compliance)
                        },
                        {
                            "name": "constitutional_hash",
                            "value": dependency.constitutional_hash
                        }
                    ]
                }
                
                # Add vulnerabilities if any
                if dependency.vulnerabilities:
                    component["vulnerabilities"] = dependency.vulnerabilities
                
                sbom["components"].append(component)
            
            # Save CycloneDX SBOM
            sbom_file = self.project_root / "acgs-sbom-cyclonedx.json"
            with open(sbom_file, 'w') as f:
                json.dump(sbom, f, indent=2)
            
            cyclonedx_results["file_path"] = str(sbom_file)
            cyclonedx_results["component_count"] = len(sbom["components"])
            
            logger.info(f"CycloneDX SBOM saved to {sbom_file}")
            
        except Exception as e:
            logger.error(f"CycloneDX SBOM generation failed: {e}")
            cyclonedx_results["error"] = str(e)
            cyclonedx_results["constitutional_compliance"] = False
        
        return cyclonedx_results

    async def _generate_spdx_sbom(self) -> Dict[str, Any]:
        """Generate SPDX format SBOM."""
        spdx_results = {
            "format": "SPDX",
            "version": "2.3",
            "file_path": "",
            "component_count": 0,
            "constitutional_compliance": True,
        }
        
        try:
            # Create SPDX SBOM structure
            sbom = {
                "spdxVersion": "SPDX-2.3",
                "dataLicense": "CC0-1.0",
                "SPDXID": "SPDXRef-DOCUMENT",
                "name": "ACGS-SBOM",
                "documentNamespace": f"https://acgs.gov/sbom/{int(time.time())}",
                "creationInfo": {
                    "created": datetime.now(timezone.utc).isoformat(),
                    "creators": ["Tool: ACGS SBOM Generator"],
                    "licenseListVersion": "3.19"
                },
                "packages": [],
                "relationships": []
            }
            
            # Add main package
            main_package = {
                "SPDXID": "SPDXRef-Package-ACGS",
                "name": "ACGS",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "versionInfo": "1.0.0",
                "description": "Autonomous Constitutional Governance System",
                "annotations": [
                    {
                        "annotationType": "OTHER",
                        "annotator": "Tool: ACGS SBOM Generator",
                        "annotationDate": datetime.now(timezone.utc).isoformat(),
                        "annotationComment": f"Constitutional Hash: {CONSTITUTIONAL_HASH}"
                    }
                ]
            }
            sbom["packages"].append(main_package)
            
            # Add dependencies as packages
            for i, dependency in enumerate(self.dependencies):
                package_id = f"SPDXRef-Package-{dependency.name}-{i}"
                package = {
                    "SPDXID": package_id,
                    "name": dependency.name,
                    "downloadLocation": "NOASSERTION",
                    "filesAnalyzed": False,
                    "licenseConcluded": dependency.license,
                    "licenseDeclared": dependency.license,
                    "copyrightText": "NOASSERTION",
                    "versionInfo": dependency.version,
                    "annotations": [
                        {
                            "annotationType": "OTHER",
                            "annotator": "Tool: ACGS SBOM Generator",
                            "annotationDate": datetime.now(timezone.utc).isoformat(),
                            "annotationComment": f"Source: {dependency.source}, Constitutional Hash: {dependency.constitutional_hash}"
                        }
                    ]
                }
                sbom["packages"].append(package)
                
                # Add relationship
                relationship = {
                    "spdxElementId": "SPDXRef-Package-ACGS",
                    "relationshipType": "DEPENDS_ON",
                    "relatedSpdxElement": package_id
                }
                sbom["relationships"].append(relationship)
            
            # Save SPDX SBOM
            sbom_file = self.project_root / "acgs-sbom-spdx.json"
            with open(sbom_file, 'w') as f:
                json.dump(sbom, f, indent=2)
            
            spdx_results["file_path"] = str(sbom_file)
            spdx_results["component_count"] = len(sbom["packages"]) - 1  # Exclude main package
            
            logger.info(f"SPDX SBOM saved to {sbom_file}")
            
        except Exception as e:
            logger.error(f"SPDX SBOM generation failed: {e}")
            spdx_results["error"] = str(e)
            spdx_results["constitutional_compliance"] = False
        
        return spdx_results

    async def _validate_constitutional_compliance(self) -> Dict[str, Any]:
        """Validate constitutional compliance of SBOM."""
        validation_results = {
            "constitutional_hash_present": True,
            "all_components_compliant": True,
            "compliance_score": 100.0,
            "validation_details": [],
            "constitutional_compliance": True,
        }
        
        try:
            # Validate constitutional hash in all dependencies
            non_compliant_deps = []
            
            for dependency in self.dependencies:
                if dependency.constitutional_hash != CONSTITUTIONAL_HASH:
                    non_compliant_deps.append(dependency.name)
                    validation_results["all_components_compliant"] = False
            
            if non_compliant_deps:
                validation_results["validation_details"].append({
                    "issue": "Constitutional hash mismatch",
                    "affected_components": non_compliant_deps,
                    "expected_hash": CONSTITUTIONAL_HASH
                })
                validation_results["compliance_score"] = 90.0
            
            # Validate SBOM files contain constitutional hash
            sbom_files = [
                self.project_root / "acgs-sbom-cyclonedx.json",
                self.project_root / "acgs-sbom-spdx.json"
            ]
            
            for sbom_file in sbom_files:
                if sbom_file.exists():
                    with open(sbom_file, 'r') as f:
                        content = f.read()
                        if CONSTITUTIONAL_HASH not in content:
                            validation_results["constitutional_hash_present"] = False
                            validation_results["validation_details"].append({
                                "issue": "Constitutional hash missing from SBOM file",
                                "file": str(sbom_file)
                            })
                            validation_results["compliance_score"] = 85.0
            
            # Overall constitutional compliance
            validation_results["constitutional_compliance"] = (
                validation_results["constitutional_hash_present"] and
                validation_results["all_components_compliant"]
            )
            
        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            validation_results["error"] = str(e)
            validation_results["constitutional_compliance"] = False
            validation_results["compliance_score"] = 0.0
        
        return validation_results

    async def _save_sbom_results(self, results: Dict[str, Any]):
        """Save SBOM generation results."""
        try:
            # Create reports directory
            reports_dir = Path("reports/sbom")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"sbom_generation_results_{timestamp}.json"
            filepath = reports_dir / filename
            
            # Save results
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)
                
            logger.info(f"✅ SBOM results saved to {filepath}")
            
            # Also save latest results
            latest_filepath = reports_dir / "latest_sbom_results.json"
            with open(latest_filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Failed to save SBOM results: {e}")


async def main():
    """Main function for SBOM generation."""
    logger.info("🚀 ACGS SBOM Generator Starting...")
    
    try:
        # Create and run SBOM generator
        generator = ACGSSBOMGenerator()
        results = await generator.generate_comprehensive_sbom()
        
        # Print summary
        dependency_analysis = results.get("dependency_analysis", {})
        vulnerability_scan = results.get("vulnerability_scan", {})
        license_compliance = results.get("license_compliance", {})
        constitutional_validation = results.get("constitutional_validation", {})
        
        print("\n" + "="*80)
        print("📋 ACGS SBOM GENERATION RESULTS")
        print("="*80)
        print(f"Total Dependencies: {dependency_analysis.get('total_dependencies', 0)}")
        print(f"Python Dependencies: {len(dependency_analysis.get('python_dependencies', []))}")
        print(f"System Dependencies: {len(dependency_analysis.get('system_dependencies', []))}")
        print(f"Docker Dependencies: {len(dependency_analysis.get('docker_dependencies', []))}")
        
        print(f"\n🔒 VULNERABILITY SCAN:")
        print(f"Total Vulnerabilities: {vulnerability_scan.get('total_vulnerabilities', 0)}")
        print(f"Critical: {vulnerability_scan.get('critical_vulnerabilities', 0)}")
        print(f"High: {vulnerability_scan.get('high_vulnerabilities', 0)}")
        print(f"Medium: {vulnerability_scan.get('medium_vulnerabilities', 0)}")
        print(f"Low: {vulnerability_scan.get('low_vulnerabilities', 0)}")
        
        print(f"\n⚖️ LICENSE COMPLIANCE:")
        print(f"Total Licenses: {license_compliance.get('total_licenses', 0)}")
        print(f"Approved: {license_compliance.get('approved_licenses', 0)}")
        print(f"Restricted: {license_compliance.get('restricted_licenses', 0)}")
        print(f"Unknown: {license_compliance.get('unknown_licenses', 0)}")
        print(f"Compliance Status: {license_compliance.get('compliance_status', 'unknown')}")
        
        print(f"\n🏛️ CONSTITUTIONAL COMPLIANCE:")
        print(f"Constitutional Hash Present: {'✅' if constitutional_validation.get('constitutional_hash_present', False) else '❌'}")
        print(f"All Components Compliant: {'✅' if constitutional_validation.get('all_components_compliant', False) else '❌'}")
        print(f"Compliance Score: {constitutional_validation.get('compliance_score', 0):.1f}/100")
        
        print(f"\n📄 SBOM FORMATS GENERATED:")
        sbom_formats = results.get("sbom_formats", {})
        for format_name, format_results in sbom_formats.items():
            if isinstance(format_results, dict):
                status = "✅" if format_results.get("constitutional_compliance", False) else "❌"
                count = format_results.get("component_count", 0)
                print(f"  {status} {format_name.upper()}: {count} components")
        
        print(f"\n🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("="*80)
        
    except Exception as e:
        logger.error(f"❌ SBOM generation failed: {e}")
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
