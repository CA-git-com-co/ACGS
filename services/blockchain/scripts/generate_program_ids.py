#!/usr/bin/env python3
"""
Generate valid Solana program IDs for Quantumagi programs
"""
# Constitutional Hash: cdd01ef066bc6cf2

import hashlib
import os
import pathlib

import base58


def generate_program_id(program_name: str) -> str:
    """Generate a valid Solana program ID from a program name"""
    # Create a deterministic seed from the program name
    seed = f"quantumagi_{program_name}".encode()
    hash_obj = hashlib.sha256(seed)

    # Take first 32 bytes and ensure it's a valid program ID
    program_bytes = hash_obj.digest()

    # Convert to base58 (Solana address format)
    return base58.b58encode(program_bytes).decode("utf-8")


def main():
    programs = {
        "quantumagi_core": "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS",  # Keep existing  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        "appeals": generate_program_id("appeals"),
        "logging": generate_program_id("logging"),
    }

    for program, program_id in programs.items():
        pass

    # Update Anchor.toml
    anchor_toml_path = os.path.join(pathlib.Path(__file__).parent, "..", "Anchor.toml")

    with open(anchor_toml_path, encoding="utf-8") as f:
        content = f.read()

    # Replace program IDs in both localnet and devnet sections
    for program, program_id in programs.items():
        content = content.replace(
            f'{program} = "AppeaLs1111111111111111111111111111111111111"',  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            f'{program} = "{program_id}"',
        )
        content = content.replace(
            f'{program} = "Logg1ng1111111111111111111111111111111111111"',  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            f'{program} = "{program_id}"',
        )

    with open(anchor_toml_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Update program declarations
    program_files = {
        "appeals": "../programs/appeals/src/lib.rs",
        "logging": "../programs/logging/src/lib.rs",
    }

    for program, file_path in program_files.items():
        full_path = os.path.join(pathlib.Path(__file__).parent, file_path)
        if pathlib.Path(full_path).exists():
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            # Replace declare_id! statements
            old_id = (
                "AppeaLs1111111111111111111111111111111111111"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
                if program == "appeals"
                else "Logg1ng1111111111111111111111111111111111111"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            )
            content = content.replace(
                f'declare_id!("{old_id}");', f'declare_id!("{programs[program]}");'
            )

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)


if __name__ == "__main__":
    main()
