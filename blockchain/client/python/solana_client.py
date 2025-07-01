#!/usr/bin/env python3
"""
Quantumagi Solana Client
Interfaces with the on-chain Quantumagi programs
Handles policy deployment and compliance checking
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

# Import our GS Engine
from gs_engine.governance_synthesis import (
    PolicyCategory,
    QuantumagiGSEngine,
    SolanaPolicy,
)
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey


@dataclass
class ConstitutionAccount:
    """Represents the on-chain Constitution account"""

    authority: Pubkey
    hash: bytes
    version: int
    is_active: bool
    created_at: int
    updated_at: int | None


@dataclass
class PolicyAccount:
    """Represents the on-chain Policy account"""

    id: int
    rule: str
    category: str
    priority: str
    is_active: bool
    proposed_at: int
    proposed_by: Pubkey
    enacted_at: int | None
    enacted_by: Pubkey | None
    votes_for: int
    votes_against: int


class QuantumagiSolanaClient:
    """
    Client for interacting with Quantumagi on-chain programs
    Bridges off-chain GS Engine with on-chain enforcement
    """

    def __init__(self, rpc_url: str, program_id: str, payer_keypair: Keypair):
        self.rpc_url = rpc_url
        self.program_id = Pubkey.from_string(program_id)
        self.payer_keypair = payer_keypair
        self.client = AsyncClient(rpc_url)
        self.logger = logging.getLogger(__name__)

        # Initialize Anchor program (would need actual IDL)
        self.program = None  # Will be initialized when IDL is available

        # Initialize GS Engine
        self.gs_engine = QuantumagiGSEngine(
            {
                "llm_model": "gpt-4",
                "validation_threshold": 0.85,
                "solana_cluster": "devnet",
            }
        )

    async def initialize_constitution(self, constitution_hash: bytes) -> str:
        """Initialize the constitutional governance system"""
        try:
            # Derive Constitution PDA
            constitution_pda, bump = Pubkey.find_program_address(
                [b"constitution"], self.program_id
            )

            self.logger.info(f"Initializing constitution at PDA: {constitution_pda}")

            # Create instruction data (simplified - would use Anchor in production)
            self._create_initialize_instruction(constitution_hash)

            # Build and send transaction
            transaction = Transaction()
            # Add instruction (simplified)

            # Send transaction
            signature = await self.client.send_transaction(
                transaction, [self.payer_keypair], opts={"commitment": Confirmed}
            )

            self.logger.info(f"Constitution initialized. Signature: {signature}")
            return str(signature)

        except Exception as e:
            self.logger.error(f"Failed to initialize constitution: {e}")
            raise

    async def propose_policy_from_principle(
        self,
        principle_id: str,
        principle_content: str,
        category: PolicyCategory = PolicyCategory.GOVERNANCE,
    ) -> str:
        """
        Generate and propose a policy from a constitutional principle
        Uses the GS Engine for policy synthesis
        """
        try:
            # Create mock principle for GS Engine
            from integrations.alphaevolve_engine.core import ConstitutionalPrinciple

            principle = ConstitutionalPrinciple(
                id=principle_id,
                title=f"Principle {principle_id}",
                content=principle_content,
                category=category.value,
                rationale="Generated for Quantumagi deployment",
            )

            # Synthesize policy using GS Engine
            self.logger.info(f"Synthesizing policy from principle: {principle_id}")
            policy = await self.gs_engine.synthesize_policy_from_principle(
                principle, category
            )

            # Deploy policy to Solana
            signature = await self._deploy_policy_to_solana(policy)

            self.logger.info(
                f"Policy {policy.id} proposed successfully. Signature: {signature}"
            )
            return signature

        except Exception as e:
            self.logger.error(f"Failed to propose policy: {e}")
            raise

    async def _deploy_policy_to_solana(self, policy: SolanaPolicy) -> str:
        """Deploy a synthesized policy to the Solana blockchain"""

        # Derive Policy PDA
        policy_pda, bump = Pubkey.find_program_address(
            [b"policy", policy.id.to_bytes(8, "little")], self.program_id
        )

        self.logger.info(f"Deploying policy {policy.id} to PDA: {policy_pda}")

        # Create instruction data
        self._create_propose_policy_instruction(policy)

        # Build transaction (simplified)
        transaction = Transaction()
        # Add instruction with proper accounts and data

        # Send transaction
        signature = await self.client.send_transaction(
            transaction, [self.payer_keypair], opts={"commitment": Confirmed}
        )

        return str(signature)

    async def enact_policy(self, policy_id: int) -> str:
        """Enact a previously proposed policy"""
        try:
            # Derive PDAs
            policy_pda, _ = Pubkey.find_program_address(
                [b"policy", policy_id.to_bytes(8, "little")], self.program_id
            )
            constitution_pda, _ = Pubkey.find_program_address(
                [b"constitution"], self.program_id
            )

            # Create instruction
            self._create_enact_policy_instruction()

            # Build and send transaction
            transaction = Transaction()
            # Add instruction

            signature = await self.client.send_transaction(
                transaction, [self.payer_keypair], opts={"commitment": Confirmed}
            )

            self.logger.info(f"Policy {policy_id} enacted. Signature: {signature}")
            return str(signature)

        except Exception as e:
            self.logger.error(f"Failed to enact policy {policy_id}: {e}")
            raise

    async def check_compliance(
        self, policy_id: int, action: str, action_context: dict[str, Any]
    ) -> bool:
        """
        Check if an action complies with a specific policy
        This is the core PGC (Prompt Governance Compiler) function
        """
        try:
            # Derive Policy PDA
            policy_pda, _ = Pubkey.find_program_address(
                [b"policy", policy_id.to_bytes(8, "little")], self.program_id
            )

            # Create instruction data
            self._create_compliance_check_instruction(action, action_context)

            # Build transaction
            transaction = Transaction()
            # Add instruction

            # Send transaction and check result
            try:
                await self.client.send_transaction(
                    transaction, [self.payer_keypair], opts={"commitment": Confirmed}
                )

                self.logger.info(f"Compliance check PASSED for action: {action}")
                return True

            except Exception as tx_error:
                # If transaction fails, compliance check failed
                self.logger.warning(
                    f"Compliance check FAILED for action: {action}. Error: {tx_error}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error during compliance check: {e}")
            return False

    async def get_constitution(self) -> ConstitutionAccount | None:
        """Fetch the current constitution from the blockchain"""
        try:
            constitution_pda, _ = Pubkey.find_program_address(
                [b"constitution"], self.program_id
            )

            account_info = await self.client.get_account_info(constitution_pda)

            if account_info.value is None:
                return None

            # Decode account data (simplified - would use Anchor in production)
            data = account_info.value.data
            return self._decode_constitution_account(data)

        except Exception as e:
            self.logger.error(f"Failed to fetch constitution: {e}")
            return None

    async def get_policy(self, policy_id: int) -> PolicyAccount | None:
        """Fetch a specific policy from the blockchain"""
        try:
            policy_pda, _ = Pubkey.find_program_address(
                [b"policy", policy_id.to_bytes(8, "little")], self.program_id
            )

            account_info = await self.client.get_account_info(policy_pda)

            if account_info.value is None:
                return None

            # Decode account data
            data = account_info.value.data
            return self._decode_policy_account(data)

        except Exception as e:
            self.logger.error(f"Failed to fetch policy {policy_id}: {e}")
            return None

    async def list_active_policies(self) -> list[PolicyAccount]:
        """List all active policies"""
        # This would require scanning all policy accounts
        # Simplified implementation
        active_policies = []

        # In production, would use getProgramAccounts or maintain an index
        for policy_id in range(1, 100):  # Check first 100 policies
            policy = await self.get_policy(policy_id)
            if policy and policy.is_active:
                active_policies.append(policy)

        return active_policies

    def _create_initialize_instruction(self, constitution_hash: bytes) -> bytes:
        """Create instruction data for initializing constitution"""
        # Simplified instruction encoding
        # In production, would use Anchor's instruction encoding
        return b"initialize" + constitution_hash

    def _create_propose_policy_instruction(self, policy: SolanaPolicy) -> bytes:
        """Create instruction data for proposing a policy"""
        # Simplified encoding
        data = {
            "policy_id": policy.id,
            "rule": policy.rule,
            "category": policy.category.value,
            "priority": policy.priority.value,
        }
        return json.dumps(data).encode()

    def _create_enact_policy_instruction(self) -> bytes:
        """Create instruction data for enacting a policy"""
        return b"enact_policy"

    def _create_compliance_check_instruction(self, action: str, context: dict) -> bytes:
        """Create instruction data for compliance checking"""
        data = {"action": action, "context": context}
        return json.dumps(data).encode()

    def _decode_constitution_account(self, data: bytes) -> ConstitutionAccount:
        """Decode constitution account data"""
        # Simplified decoding - would use Anchor's account decoder
        return ConstitutionAccount(
            authority=Pubkey.from_bytes(data[8:40]),
            hash=data[40:72],
            version=int.from_bytes(data[72:76], "little"),
            is_active=bool(data[76]),
            created_at=int.from_bytes(data[77:85], "little"),
            updated_at=None,  # Simplified
        )

    def _decode_policy_account(self, data: bytes) -> PolicyAccount:
        """Decode policy account data"""
        # Simplified decoding
        return PolicyAccount(
            id=int.from_bytes(data[8:16], "little"),
            rule="decoded_rule",  # Would decode properly
            category="governance",
            priority="high",
            is_active=bool(data[16]),
            proposed_at=int.from_bytes(data[17:25], "little"),
            proposed_by=Pubkey.from_bytes(data[25:57]),
            enacted_at=None,
            enacted_by=None,
            votes_for=0,
            votes_against=0,
        )


# Example usage
async def main():
    """Example of using the Quantumagi Solana Client"""

    # Initialize client (would use real keypair and program ID)
    payer = Keypair()  # Generate or load keypair
    client = QuantumagiSolanaClient(
        rpc_url="https://api.devnet.solana.com",
        program_id="Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS",
        payer_keypair=payer,
    )

    try:
        # Initialize constitution
        constitution_hash = b"constitutional_document_hash_here_32_bytes"
        await client.initialize_constitution(constitution_hash)

        # Propose a policy from a principle
        principle_content = "AI systems must obtain proper authorization before modifying critical state"
        signature = await client.propose_policy_from_principle(
            "PC-001", principle_content, PolicyCategory.PROMPT_CONSTITUTION
        )
        print(f"Policy proposed: {signature}")

        # Enact the policy
        await client.enact_policy(1)

        # Check compliance
        is_compliant = await client.check_compliance(
            1,
            "authorized state modification",
            {"requires_governance": False, "has_approval": True},
        )
        print(f"Compliance check result: {is_compliant}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
