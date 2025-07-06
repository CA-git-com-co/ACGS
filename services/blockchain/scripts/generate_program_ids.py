#!/usr/bin/env python3
"""
Generate valid Solana program IDs for Quantumagi programs
"""
# Constitutional Hash: cdd01ef066bc6cf2

import hashlib
import os

import base58


def generate_program_id(program_name: str) -> str:
    """Generate a valid Solana program ID from a program name"""
    # Create a deterministic seed from the program name
    seed = f"quantumagi_{program_name}".encode()
    hash_obj = hashlib.sha256(seed)

    # Take first 32 bytes and ensure it's a valid program ID
    program_bytes = hash_obj.digest()

    # Convert to base58 (Solana address format)
    program_id = base58.b58encode(program_bytes).decode("utf-8")

    return program_id


def main():
    programs = {
        "quantumagi_core": "Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS",  # Keep existing
        "appeals": generate_program_id("appeals"),
        "logging": generate_program_id("logging"),
    }

    print("Generated Program IDs:")
    print("=" * 50)
    for program, program_id in programs.items():
        print(f"{program}: {program_id}")

    # Update Anchor.toml
    anchor_toml_path = os.path.join(os.path.dirname(__file__), "..", "Anchor.toml")

    with open(anchor_toml_path) as f:
        content = f.read()

    # Replace program IDs in both localnet and devnet sections
    for program, program_id in programs.items():
        content = content.replace(
            f'{program} = "AppeaLs1111111111111111111111111111111111111"',
            f'{program} = "{program_id}"',
        )
        content = content.replace(
            f'{program} = "Logg1ng1111111111111111111111111111111111111"',
            f'{program} = "{program_id}"',
        )

    with open(anchor_toml_path, "w") as f:
        f.write(content)

    print(f"\nUpdated {anchor_toml_path}")

    # Update program declarations
    program_files = {
        "appeals": "../programs/appeals/src/lib.rs",
        "logging": "../programs/logging/src/lib.rs",
    }

    for program, file_path in program_files.items():
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            with open(full_path) as f:
                content = f.read()

            # Replace declare_id! statements
            old_id = (
                "AppeaLs1111111111111111111111111111111111111"
                if program == "appeals"
                else "Logg1ng1111111111111111111111111111111111111"
            )
            content = content.replace(
                f'declare_id!("{old_id}");', f'declare_id!("{programs[program]}");'
            )

            with open(full_path, "w") as f:
                f.write(content)

            print(f"Updated {full_path}")


if __name__ == "__main__":
    main()
