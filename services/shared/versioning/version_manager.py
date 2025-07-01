"""
ACGS-1 API Version Manager

Provides semantic versioning (SemVer) management with comprehensive version detection,
validation, and compatibility checking for all ACGS-1 services.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class VersionPolicy(str, Enum):
    """Version change policies following semantic versioning."""

    MAJOR = "major"  # Breaking changes
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, backward compatible


class VersionStatus(str, Enum):
    """API version lifecycle status."""

    DEVELOPMENT = "development"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


class VersionValidationError(Exception):
    """Raised when version validation fails."""

    pass


class UnsupportedVersionError(Exception):
    """Raised when an unsupported version is requested."""

    pass


class DeprecatedVersionError(Exception):
    """Raised when a deprecated version is accessed."""

    pass


@dataclass
class APIVersion:
    """
    Semantic version representation with comprehensive metadata.

    Follows SemVer specification: MAJOR.MINOR.PATCH
    """

    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build_metadata: Optional[str] = None

    def __post_init__(self):
        """Validate version components."""
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise VersionValidationError("Version components must be non-negative")

    @classmethod
    def from_string(cls, version_str: str) -> "APIVersion":
        """
        Parse version string into APIVersion object.

        Supports formats:
        - v1.2.3
        - 1.2.3
        - v1.2.3-beta.1
        - v1.2.3+build.123
        """
        # Remove 'v' prefix if present
        version_str = version_str.lstrip("v")

        # SemVer regex pattern
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
        match = re.match(pattern, version_str)

        if not match:
            raise VersionValidationError(f"Invalid version format: {version_str}")

        major, minor, patch, prerelease, build_metadata = match.groups()

        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build_metadata=build_metadata,
        )

    def to_string(self, include_prefix: bool = True) -> str:
        """Convert to string representation."""
        version = f"{self.major}.{self.minor}.{self.patch}"

        if self.prerelease:
            version += f"-{self.prerelease}"

        if self.build_metadata:
            version += f"+{self.build_metadata}"

        return f"v{version}" if include_prefix else version

    def __str__(self) -> str:
        return self.to_string()

    def __eq__(self, other) -> bool:
        if not isinstance(other, APIVersion):
            return False
        return (self.major, self.minor, self.patch, self.prerelease) == (
            other.major,
            other.minor,
            other.patch,
            other.prerelease,
        )

    def __lt__(self, other) -> bool:
        if not isinstance(other, APIVersion):
            return NotImplemented

        # Compare major.minor.patch first
        if (self.major, self.minor, self.patch) != (
            other.major,
            other.minor,
            other.patch,
        ):
            return (self.major, self.minor, self.patch) < (
                other.major,
                other.minor,
                other.patch,
            )

        # Handle prerelease comparison
        if self.prerelease is None and other.prerelease is None:
            return False
        if self.prerelease is None:
            return False  # Normal version > prerelease
        if other.prerelease is None:
            return True  # Prerelease < normal version

        return self.prerelease < other.prerelease

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return not self < other

    def is_compatible_with(self, other: "APIVersion") -> bool:
        """Check if this version is backward compatible with another."""
        if self.major != other.major:
            return False  # Major version changes break compatibility

        if self.minor < other.minor:
            return False  # Cannot be compatible with newer minor version

        return True

    def get_compatibility_level(self, other: "APIVersion") -> VersionPolicy:
        """Determine the type of change between versions."""
        if self.major != other.major:
            return VersionPolicy.MAJOR
        elif self.minor != other.minor:
            return VersionPolicy.MINOR
        else:
            return VersionPolicy.PATCH


@dataclass
class VersionCompatibility:
    """Version compatibility and deprecation information."""

    version: APIVersion
    status: VersionStatus
    supported_until: Optional[datetime] = None
    deprecated_since: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    migration_guide_url: Optional[str] = None
    breaking_changes: List[str] = field(default_factory=list)

    def is_supported(self) -> bool:
        """Check if version is currently supported."""
        if self.status == VersionStatus.SUNSET:
            return False

        if self.sunset_date and datetime.now(timezone.utc) >= self.sunset_date:
            return False

        return True

    def is_deprecated(self) -> bool:
        """Check if version is deprecated."""
        return self.status in [VersionStatus.DEPRECATED, VersionStatus.SUNSET]

    def days_until_sunset(self) -> Optional[int]:
        """Calculate days until version sunset."""
        if not self.sunset_date:
            return None

        delta = self.sunset_date - datetime.now(timezone.utc)
        return max(0, delta.days)


class VersionManager:
    """
    Comprehensive API version management system.

    Handles version detection, validation, compatibility checking,
    and lifecycle management for all ACGS-1 services.
    """

    def __init__(self, service_name: str, current_version: str = "v1.0.0"):
        self.service_name = service_name
        self.current_version = APIVersion.from_string(current_version)
        self.supported_versions: Dict[str, VersionCompatibility] = {}
        self.version_aliases: Dict[str, APIVersion] = {}

        # Default policies
        self.deprecation_period_days = 180  # 6 months
        self.sunset_notice_days = 30  # 30 days advance notice

        # Initialize with current version
        self._register_current_version()

        logger.info(
            f"VersionManager initialized for {service_name} with version {current_version}"
        )

    def _register_current_version(self):
        """Register the current version as stable."""
        compatibility = VersionCompatibility(
            version=self.current_version, status=VersionStatus.STABLE
        )
        self.supported_versions[str(self.current_version)] = compatibility

        # Add common aliases
        self.version_aliases["latest"] = self.current_version
        self.version_aliases[f"v{self.current_version.major}"] = self.current_version

    def register_version(
        self,
        version: Union[str, APIVersion],
        status: VersionStatus = VersionStatus.STABLE,
        migration_guide_url: Optional[str] = None,
        breaking_changes: Optional[List[str]] = None,
    ) -> VersionCompatibility:
        """Register a new API version."""
        if isinstance(version, str):
            version = APIVersion.from_string(version)

        # Calculate deprecation and sunset dates for older versions
        supported_until = None
        deprecated_since = None
        sunset_date = None

        if status == VersionStatus.DEPRECATED:
            deprecated_since = datetime.now(timezone.utc)
            sunset_date = deprecated_since + timedelta(days=self.sunset_notice_days)
        elif status == VersionStatus.STABLE and version < self.current_version:
            # Auto-deprecate older stable versions
            deprecated_since = datetime.now(timezone.utc)
            sunset_date = deprecated_since + timedelta(
                days=self.deprecation_period_days
            )
            status = VersionStatus.DEPRECATED

        compatibility = VersionCompatibility(
            version=version,
            status=status,
            supported_until=supported_until,
            deprecated_since=deprecated_since,
            sunset_date=sunset_date,
            migration_guide_url=migration_guide_url,
            breaking_changes=breaking_changes or [],
        )

        self.supported_versions[str(version)] = compatibility

        logger.info(f"Registered version {version} with status {status}")
        return compatibility

    def detect_version_from_request(
        self,
        request_headers: Dict[str, str],
        url_path: str,
        query_params: Dict[str, str],
    ) -> APIVersion:
        """
        Detect API version from multiple sources with priority order:
        1. API-Version header
        2. Accept header with version parameter
        3. URL path (/api/v1/, /api/v2/)
        4. Query parameter (?version=v1.2.3)
        5. Default to current version
        """
        # 1. Check API-Version header
        if "api-version" in request_headers:
            try:
                return APIVersion.from_string(request_headers["api-version"])
            except VersionValidationError:
                logger.warning(
                    f"Invalid API-Version header: {request_headers['api-version']}"
                )

        # 2. Check Accept header
        accept_header = request_headers.get("accept", "")
        if "version=" in accept_header:
            version_match = re.search(r"version=([^;,\s]+)", accept_header)
            if version_match:
                try:
                    return APIVersion.from_string(version_match.group(1))
                except VersionValidationError:
                    logger.warning(
                        f"Invalid version in Accept header: {version_match.group(1)}"
                    )

        # 3. Check URL path
        path_pattern = r"/api/v(\d+)(?:\.(\d+))?(?:\.(\d+))?/"
        path_match = re.search(path_pattern, url_path)
        if path_match:
            major = int(path_match.group(1))
            minor = int(path_match.group(2)) if path_match.group(2) else 0
            patch = int(path_match.group(3)) if path_match.group(3) else 0
            return APIVersion(major=major, minor=minor, patch=patch)

        # 4. Check query parameter
        if "version" in query_params:
            try:
                return APIVersion.from_string(query_params["version"])
            except VersionValidationError:
                logger.warning(
                    f"Invalid version query parameter: {query_params['version']}"
                )

        # 5. Default to current version
        return self.current_version

    def validate_version(self, version: Union[str, APIVersion]) -> VersionCompatibility:
        """
        Validate if a version is supported and return compatibility info.

        Raises:
            UnsupportedVersionError: If version is not supported
            DeprecatedVersionError: If version is deprecated (with warning)
        """
        if isinstance(version, str):
            version = APIVersion.from_string(version)

        version_str = str(version)

        # Check if version is registered
        if version_str not in self.supported_versions:
            # Try to find compatible version
            compatible_version = self._find_compatible_version(version)
            if compatible_version:
                version_str = str(compatible_version)
            else:
                raise UnsupportedVersionError(
                    f"Version {version} is not supported by {self.service_name}"
                )

        compatibility = self.supported_versions[version_str]

        # Check if version is still supported
        if not compatibility.is_supported():
            raise UnsupportedVersionError(f"Version {version} is no longer supported")

        # Warn if deprecated
        if compatibility.is_deprecated():
            days_left = compatibility.days_until_sunset()
            warning_msg = f"Version {version} is deprecated"
            if days_left is not None:
                warning_msg += f" and will be sunset in {days_left} days"
            if compatibility.migration_guide_url:
                warning_msg += f". Migration guide: {compatibility.migration_guide_url}"

            logger.warning(warning_msg)
            # Note: We don't raise DeprecatedVersionError here to allow use

        return compatibility

    def _find_compatible_version(
        self, requested_version: APIVersion
    ) -> Optional[APIVersion]:
        """Find a compatible version for the requested version."""
        compatible_versions = []

        for version_str, compatibility in self.supported_versions.items():
            version = compatibility.version
            if (
                version.is_compatible_with(requested_version)
                and compatibility.is_supported()
            ):
                compatible_versions.append(version)

        # Return the highest compatible version
        return max(compatible_versions) if compatible_versions else None

    def get_supported_versions(self) -> List[VersionCompatibility]:
        """Get all currently supported versions."""
        return [
            comp for comp in self.supported_versions.values() if comp.is_supported()
        ]

    def get_deprecated_versions(self) -> List[VersionCompatibility]:
        """Get all deprecated versions."""
        return [
            comp for comp in self.supported_versions.values() if comp.is_deprecated()
        ]

    def get_version_info(self) -> Dict[str, any]:
        """Get comprehensive version information for the service."""
        return {
            "service": self.service_name,
            "current_version": str(self.current_version),
            "supported_versions": [
                str(comp.version) for comp in self.get_supported_versions()
            ],
            "deprecated_versions": [
                {
                    "version": str(comp.version),
                    "deprecated_since": (
                        comp.deprecated_since.isoformat()
                        if comp.deprecated_since
                        else None
                    ),
                    "sunset_date": (
                        comp.sunset_date.isoformat() if comp.sunset_date else None
                    ),
                    "days_until_sunset": comp.days_until_sunset(),
                    "migration_guide": comp.migration_guide_url,
                }
                for comp in self.get_deprecated_versions()
            ],
            "version_aliases": {
                alias: str(version) for alias, version in self.version_aliases.items()
            },
            "policies": {
                "deprecation_period_days": self.deprecation_period_days,
                "sunset_notice_days": self.sunset_notice_days,
            },
        }

    def create_deprecation_headers(self, version: APIVersion) -> Dict[str, str]:
        """
        Create RFC 8594 compliant deprecation headers.

        Returns headers for deprecated versions including:
        - Deprecation: RFC 7234 deprecation date
        - Sunset: RFC 8594 sunset date
        - Link: Migration guide link
        """
        headers = {}

        version_str = str(version)
        if version_str not in self.supported_versions:
            return headers

        compatibility = self.supported_versions[version_str]

        if compatibility.is_deprecated():
            # Deprecation header (RFC 7234)
            if compatibility.deprecated_since:
                headers["Deprecation"] = compatibility.deprecated_since.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )

            # Sunset header (RFC 8594)
            if compatibility.sunset_date:
                headers["Sunset"] = compatibility.sunset_date.strftime(
                    "%a, %d %b %Y %H:%M:%S GMT"
                )

            # Link header for migration guide
            if compatibility.migration_guide_url:
                headers["Link"] = (
                    f'<{compatibility.migration_guide_url}>; rel="successor-version"'
                )

        return headers

    def bump_version(
        self, policy: VersionPolicy, prerelease: Optional[str] = None
    ) -> APIVersion:
        """
        Bump version according to semantic versioning rules.

        Args:
            policy: Type of version bump (MAJOR, MINOR, PATCH)
            prerelease: Optional prerelease identifier

        Returns:
            New version after bump
        """
        current = self.current_version

        if policy == VersionPolicy.MAJOR:
            new_version = APIVersion(
                major=current.major + 1, minor=0, patch=0, prerelease=prerelease
            )
        elif policy == VersionPolicy.MINOR:
            new_version = APIVersion(
                major=current.major,
                minor=current.minor + 1,
                patch=0,
                prerelease=prerelease,
            )
        else:  # PATCH
            new_version = APIVersion(
                major=current.major,
                minor=current.minor,
                patch=current.patch + 1,
                prerelease=prerelease,
            )

        logger.info(f"Version bumped from {current} to {new_version} ({policy.value})")
        return new_version
