"""
Cryptographic service implementation for ACGS Integrity Service.
Constitutional Hash: cdd01ef066bc6cf2
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class CryptoService:
    """Cryptographic operations service."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.supported_algorithms = ["SHA-256", "SHA-512", "SHA3-256", "SHA3-512"]
    
    async def generate_hash(self, data: str, algorithm: str = "SHA-256") -> str:
        """Generate hash of data using specified algorithm."""
        try:
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            data_bytes = data.encode('utf-8')
            
            if algorithm == "SHA-256":
                hash_obj = hashlib.sha256(data_bytes)
            elif algorithm == "SHA-512":
                hash_obj = hashlib.sha512(data_bytes)
            elif algorithm == "SHA3-256":
                hash_obj = hashlib.sha3_256(data_bytes)
            elif algorithm == "SHA3-512":
                hash_obj = hashlib.sha3_512(data_bytes)
            else:
                raise ValueError(f"Algorithm {algorithm} not implemented")
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"Hash generation failed: {e}")
            raise
    
    async def sign_data(self, data: str, key_id: str, algorithm: str = "SHA-256") -> Dict[str, Any]:
        """Sign data with specified key."""
        try:
            # Generate content hash
            content_hash = await self.generate_hash(data, algorithm)
            
            # For now, create a mock signature (in production, use actual cryptographic signing)
            signature_data = f"{key_id}:{content_hash}:{algorithm}:{datetime.now(timezone.utc).isoformat()}"
            signature = await self.generate_hash(signature_data, algorithm)
            
            return {
                "signature": signature,
                "key_id": key_id,
                "algorithm": algorithm,
                "content_hash": content_hash,
                "timestamp": datetime.now(timezone.utc),
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Data signing failed: {e}")
            raise
    
    async def verify_signature(
        self, 
        data: str, 
        signature: str, 
        key_id: str, 
        algorithm: str = "SHA-256"
    ) -> Dict[str, Any]:
        """Verify signature of data."""
        try:
            # Generate content hash
            content_hash = await self.generate_hash(data, algorithm)
            
            # For now, mock verification (in production, use actual cryptographic verification)
            # This is a simplified verification for demonstration
            is_valid = len(signature) == 64 and all(c in '0123456789abcdef' for c in signature.lower())
            
            return {
                "is_valid": is_valid,
                "key_id": key_id,
                "algorithm": algorithm,
                "content_hash": content_hash,
                "verified_at": datetime.now(timezone.utc),
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            raise


class MerkleService:
    """Merkle tree operations service."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.trees: Dict[str, Dict[str, Any]] = {}
    
    async def build_tree(self, data_items: List[str], algorithm: str = "SHA-256") -> Dict[str, Any]:
        """Build Merkle tree from data items."""
        try:
            if not data_items:
                raise ValueError("Data items cannot be empty")
            
            crypto_service = CryptoService()
            
            # Generate leaf hashes
            leaves = []
            for item in data_items:
                leaf_hash = await crypto_service.generate_hash(item, algorithm)
                leaves.append(leaf_hash)
            
            # Build tree bottom-up
            current_level = leaves[:]
            tree_levels = [current_level[:]]
            
            while len(current_level) > 1:
                next_level = []
                for i in range(0, len(current_level), 2):
                    left = current_level[i]
                    right = current_level[i + 1] if i + 1 < len(current_level) else left
                    
                    combined = left + right
                    parent_hash = await crypto_service.generate_hash(combined, algorithm)
                    next_level.append(parent_hash)
                
                tree_levels.append(next_level[:])
                current_level = next_level
            
            root_hash = current_level[0]
            tree_id = await crypto_service.generate_hash(f"{root_hash}:{len(data_items)}:{algorithm}", algorithm)
            
            # Store tree
            tree_data = {
                "tree_id": tree_id,
                "root_hash": root_hash,
                "leaf_count": len(data_items),
                "depth": len(tree_levels) - 1,
                "algorithm": algorithm,
                "levels": tree_levels,
                "data_items": data_items,
                "created_at": datetime.now(timezone.utc),
                "constitutional_hash": self.constitutional_hash,
            }
            
            self.trees[tree_id] = tree_data
            
            return {
                "tree_id": tree_id,
                "root_hash": root_hash,
                "leaf_count": len(data_items),
                "depth": len(tree_levels) - 1,
                "created_at": tree_data["created_at"],
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Merkle tree building failed: {e}")
            raise
    
    async def generate_proof(self, tree_id: str, leaf_data: str) -> Dict[str, Any]:
        """Generate Merkle proof for leaf data."""
        try:
            if tree_id not in self.trees:
                raise ValueError(f"Tree {tree_id} not found")
            
            tree = self.trees[tree_id]
            
            # Find leaf index
            crypto_service = CryptoService()
            leaf_hash = await crypto_service.generate_hash(leaf_data, tree["algorithm"])
            
            leaf_index = -1
            for i, item in enumerate(tree["data_items"]):
                item_hash = await crypto_service.generate_hash(item, tree["algorithm"])
                if item_hash == leaf_hash:
                    leaf_index = i
                    break
            
            if leaf_index == -1:
                raise ValueError("Leaf data not found in tree")
            
            # Generate proof path
            proof_path = []
            current_index = leaf_index
            
            for level in range(len(tree["levels"]) - 1):
                current_level = tree["levels"][level]
                
                if current_index % 2 == 0:
                    # Left node, need right sibling
                    sibling_index = current_index + 1
                else:
                    # Right node, need left sibling
                    sibling_index = current_index - 1
                
                if sibling_index < len(current_level):
                    proof_path.append(current_level[sibling_index])
                else:
                    proof_path.append(current_level[current_index])
                
                current_index = current_index // 2
            
            return {
                "is_valid": True,
                "proof_path": proof_path,
                "leaf_index": leaf_index,
                "root_hash": tree["root_hash"],
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Merkle proof generation failed: {e}")
            raise
    
    async def verify_proof(
        self, 
        leaf_data: str, 
        proof_path: List[str], 
        root_hash: str, 
        leaf_index: int,
        algorithm: str = "SHA-256"
    ) -> Dict[str, Any]:
        """Verify Merkle proof."""
        try:
            crypto_service = CryptoService()
            
            # Start with leaf hash
            current_hash = await crypto_service.generate_hash(leaf_data, algorithm)
            current_index = leaf_index
            
            # Traverse up the tree
            for sibling_hash in proof_path:
                if current_index % 2 == 0:
                    # Current is left, sibling is right
                    combined = current_hash + sibling_hash
                else:
                    # Current is right, sibling is left
                    combined = sibling_hash + current_hash
                
                current_hash = await crypto_service.generate_hash(combined, algorithm)
                current_index = current_index // 2
            
            is_valid = current_hash == root_hash
            
            return {
                "is_valid": is_valid,
                "computed_root": current_hash,
                "expected_root": root_hash,
                "constitutional_hash": self.constitutional_hash,
            }
            
        except Exception as e:
            logger.error(f"Merkle proof verification failed: {e}")
            raise


# Global service instances
crypto_service = CryptoService()
merkle_service = MerkleService()
