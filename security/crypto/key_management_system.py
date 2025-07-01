#!/usr/bin/env python3
"""
ACGS Enterprise Cryptographic Key Management System
Implements PKI infrastructure, key rotation, and certificate management
"""

import logging
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.x509.oid import NameOID

logger = logging.getLogger(__name__)


@dataclass
class CryptographicKey:
    """Cryptographic key metadata"""

    key_id: str
    key_type: str  # "RSA", "AES", "ECDSA"
    key_size: int
    purpose: str  # "encryption", "signing", "authentication"
    created_at: str
    expires_at: str
    status: str  # "active", "expired", "revoked", "pending"
    rotation_count: int
    constitutional_hash: str


@dataclass
class Certificate:
    """X.509 Certificate metadata"""

    cert_id: str
    subject: str
    issuer: str
    serial_number: str
    not_before: str
    not_after: str
    key_usage: list[str]
    status: str  # "valid", "expired", "revoked"
    certificate_pem: str


class EnterpriseKeyManagementSystem:
    """Enterprise-grade cryptographic key management system"""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.keys = {}
        self.certificates = {}
        self.key_rotation_policy = {
            "RSA": timedelta(days=365),  # 1 year
            "AES": timedelta(days=90),  # 3 months
            "ECDSA": timedelta(days=365),  # 1 year
        }
        self.ca_private_key = None
        self.ca_certificate = None
        self.initialize_ca()

    def initialize_ca(self):
        """Initialize Certificate Authority"""
        print("🏛️ Initializing ACGS Certificate Authority")

        # Generate CA private key
        self.ca_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096
        )

        # Create CA certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ACGS"),
                x509.NameAttribute(NameOID.COMMON_NAME, "ACGS Root CA"),
            ]
        )

        self.ca_certificate = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(self.ca_private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=3650))  # 10 years
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("acgs.local"),
                    ]
                ),
                critical=False,
            )
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=False,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            .sign(self.ca_private_key, hashes.SHA256())
        )

        print("  ✅ Certificate Authority initialized")
        print(f"  📋 CA Subject: {self.ca_certificate.subject}")
        print(f"  🔑 CA Serial: {self.ca_certificate.serial_number}")

    def generate_key(self, key_type: str, key_size: int, purpose: str) -> str:
        """Generate a new cryptographic key"""
        key_id = f"{key_type.lower()}_{purpose}_{int(time.time())}"

        if key_type == "RSA":
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=key_size
            )
            key_data = private_key  # Store the key object, not bytes
        elif key_type == "AES":
            key_data = secrets.token_bytes(key_size // 8)
        else:
            raise ValueError(f"Unsupported key type: {key_type}")

        # Store key metadata
        key_metadata = CryptographicKey(
            key_id=key_id,
            key_type=key_type,
            key_size=key_size,
            purpose=purpose,
            created_at=datetime.now(timezone.utc).isoformat(),
            expires_at=(
                datetime.now(timezone.utc) + self.key_rotation_policy[key_type]
            ).isoformat(),
            status="active",
            rotation_count=0,
            constitutional_hash=self.constitutional_hash,
        )

        self.keys[key_id] = {"metadata": key_metadata, "key_data": key_data}

        return key_id

    def rotate_key(self, key_id: str) -> str:
        """Rotate an existing key"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        old_key = self.keys[key_id]
        old_metadata = old_key["metadata"]

        # Mark old key as expired
        old_metadata.status = "expired"

        # Generate new key with same parameters
        new_key_id = self.generate_key(
            old_metadata.key_type, old_metadata.key_size, old_metadata.purpose
        )

        # Update rotation count
        self.keys[new_key_id]["metadata"].rotation_count = (
            old_metadata.rotation_count + 1
        )

        return new_key_id

    def issue_certificate(
        self, subject_name: str, key_usage: list[str], validity_days: int = 365
    ) -> str:
        """Issue a new X.509 certificate"""
        # Generate key pair for certificate
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Create certificate subject
        subject = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "ACGS"),
                x509.NameAttribute(NameOID.COMMON_NAME, subject_name),
            ]
        )

        # Build certificate
        cert_builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.ca_certificate.subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
        )

        # Add key usage extension
        key_usage_obj = x509.KeyUsage(
            digital_signature="digital_signature" in key_usage,
            content_commitment="content_commitment" in key_usage,
            key_encipherment="key_encipherment" in key_usage,
            data_encipherment="data_encipherment" in key_usage,
            key_agreement="key_agreement" in key_usage,
            key_cert_sign="key_cert_sign" in key_usage,
            crl_sign="crl_sign" in key_usage,
            encipher_only=False,
            decipher_only=False,
        )

        cert_builder = cert_builder.add_extension(key_usage_obj, critical=True)

        # Sign certificate with CA
        certificate = cert_builder.sign(self.ca_private_key, hashes.SHA256())

        # Store certificate
        cert_id = f"cert_{int(time.time())}"
        cert_pem = certificate.public_bytes(serialization.Encoding.PEM).decode()

        cert_metadata = Certificate(
            cert_id=cert_id,
            subject=str(certificate.subject),
            issuer=str(certificate.issuer),
            serial_number=str(certificate.serial_number),
            not_before=certificate.not_valid_before.isoformat(),
            not_after=certificate.not_valid_after.isoformat(),
            key_usage=key_usage,
            status="valid",
            certificate_pem=cert_pem,
        )

        self.certificates[cert_id] = {
            "metadata": cert_metadata,
            "certificate": certificate,
            "private_key": private_key,
        }

        return cert_id

    def revoke_certificate(self, cert_id: str, reason: str = "unspecified") -> bool:
        """Revoke a certificate"""
        if cert_id not in self.certificates:
            return False

        self.certificates[cert_id]["metadata"].status = "revoked"

        # In production, this would update the Certificate Revocation List (CRL)
        logger.info(f"Certificate {cert_id} revoked: {reason}")

        return True

    def encrypt_data(self, data: bytes, key_id: str) -> bytes:
        """Encrypt data using specified key"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        key_info = self.keys[key_id]
        key_metadata = key_info["metadata"]

        if key_metadata.status != "active":
            raise ValueError(f"Key {key_id} is not active")

        if key_metadata.key_type == "AES":
            # AES encryption
            iv = secrets.token_bytes(16)
            cipher = Cipher(algorithms.AES(key_info["key_data"]), modes.CBC(iv))
            encryptor = cipher.encryptor()

            # Pad data to block size
            padding_length = 16 - (len(data) % 16)
            padded_data = data + bytes([padding_length] * padding_length)

            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            return iv + ciphertext

        if key_metadata.key_type == "RSA":
            # RSA encryption
            public_key = key_info["key_data"].public_key()
            ciphertext = public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return ciphertext

        raise ValueError(
            f"Encryption not supported for key type: {key_metadata.key_type}"
        )

    def decrypt_data(self, ciphertext: bytes, key_id: str) -> bytes:
        """Decrypt data using specified key"""
        if key_id not in self.keys:
            raise ValueError(f"Key {key_id} not found")

        key_info = self.keys[key_id]
        key_metadata = key_info["metadata"]

        if key_metadata.key_type == "AES":
            # AES decryption
            iv = ciphertext[:16]
            actual_ciphertext = ciphertext[16:]

            cipher = Cipher(algorithms.AES(key_info["key_data"]), modes.CBC(iv))
            decryptor = cipher.decryptor()

            padded_data = decryptor.update(actual_ciphertext) + decryptor.finalize()

            # Remove padding
            padding_length = padded_data[-1]
            return padded_data[:-padding_length]

        if key_metadata.key_type == "RSA":
            # RSA decryption
            plaintext = key_info["key_data"].decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return plaintext

        raise ValueError(
            f"Decryption not supported for key type: {key_metadata.key_type}"
        )

    def check_key_expiration(self) -> list[str]:
        """Check for keys that need rotation"""
        expiring_keys = []
        current_time = datetime.now(timezone.utc)

        for key_id, key_info in self.keys.items():
            metadata = key_info["metadata"]
            if metadata.status == "active":
                expires_at = datetime.fromisoformat(
                    metadata.expires_at.replace("Z", "+00:00")
                )
                if expires_at <= current_time + timedelta(days=30):  # 30 days warning
                    expiring_keys.append(key_id)

        return expiring_keys

    def get_key_inventory(self) -> dict[str, Any]:
        """Get inventory of all keys and certificates"""
        key_stats = {
            "total_keys": len(self.keys),
            "active_keys": len(
                [k for k in self.keys.values() if k["metadata"].status == "active"]
            ),
            "expired_keys": len(
                [k for k in self.keys.values() if k["metadata"].status == "expired"]
            ),
            "revoked_keys": len(
                [k for k in self.keys.values() if k["metadata"].status == "revoked"]
            ),
        }

        cert_stats = {
            "total_certificates": len(self.certificates),
            "valid_certificates": len(
                [
                    c
                    for c in self.certificates.values()
                    if c["metadata"].status == "valid"
                ]
            ),
            "expired_certificates": len(
                [
                    c
                    for c in self.certificates.values()
                    if c["metadata"].status == "expired"
                ]
            ),
            "revoked_certificates": len(
                [
                    c
                    for c in self.certificates.values()
                    if c["metadata"].status == "revoked"
                ]
            ),
        }

        return {
            "constitutional_hash": self.constitutional_hash,
            "ca_initialized": self.ca_certificate is not None,
            "key_statistics": key_stats,
            "certificate_statistics": cert_stats,
            "expiring_keys": self.check_key_expiration(),
            "inventory_timestamp": datetime.now(timezone.utc).isoformat(),
        }


def test_key_management_system():
    """Test the key management system"""
    print("🔐 Testing ACGS Key Management System")
    print("=" * 40)

    kms = EnterpriseKeyManagementSystem()

    # Test key generation
    print("\n🔑 Testing key generation...")
    rsa_key_id = kms.generate_key("RSA", 2048, "encryption")
    aes_key_id = kms.generate_key("AES", 256, "encryption")
    print(f"  ✅ Generated RSA key: {rsa_key_id}")
    print(f"  ✅ Generated AES key: {aes_key_id}")

    # Test certificate issuance
    print("\n📜 Testing certificate issuance...")
    cert_id = kms.issue_certificate(
        "acgs-service.local", ["digital_signature", "key_encipherment"], 365
    )
    print(f"  ✅ Issued certificate: {cert_id}")

    # Test encryption/decryption
    print("\n🔒 Testing encryption/decryption...")
    test_data = (
        b"This is sensitive ACGS data with constitutional hash: cdd01ef066bc6cf2"
    )

    # Test AES encryption
    aes_ciphertext = kms.encrypt_data(test_data, aes_key_id)
    aes_decrypted = kms.decrypt_data(aes_ciphertext, aes_key_id)
    print(
        f"  ✅ AES encryption/decryption: {'PASS' if aes_decrypted == test_data else 'FAIL'}"
    )

    # Test RSA encryption (with smaller data due to RSA limitations)
    small_data = b"ACGS test data"
    rsa_ciphertext = kms.encrypt_data(small_data, rsa_key_id)
    rsa_decrypted = kms.decrypt_data(rsa_ciphertext, rsa_key_id)
    print(
        f"  ✅ RSA encryption/decryption: {'PASS' if rsa_decrypted == small_data else 'FAIL'}"
    )

    # Test key rotation
    print("\n🔄 Testing key rotation...")
    new_aes_key_id = kms.rotate_key(aes_key_id)
    print(f"  ✅ Rotated AES key: {aes_key_id} -> {new_aes_key_id}")

    # Test certificate revocation
    print("\n❌ Testing certificate revocation...")
    revoked = kms.revoke_certificate(cert_id, "testing")
    print(f"  ✅ Certificate revocation: {'PASS' if revoked else 'FAIL'}")

    # Get inventory
    print("\n📊 Key Management Inventory:")
    inventory = kms.get_key_inventory()
    print(f"  Total Keys: {inventory['key_statistics']['total_keys']}")
    print(f"  Active Keys: {inventory['key_statistics']['active_keys']}")
    print(
        f"  Total Certificates: {inventory['certificate_statistics']['total_certificates']}"
    )
    print(
        f"  Valid Certificates: {inventory['certificate_statistics']['valid_certificates']}"
    )
    print(f"  CA Initialized: {inventory['ca_initialized']}")
    print(f"  Constitutional Hash: {inventory['constitutional_hash']}")

    print("\n✅ Key Management System: OPERATIONAL")


if __name__ == "__main__":
    test_key_management_system()
