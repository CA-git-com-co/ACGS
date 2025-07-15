# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS-1 Quantumagi Key Management and Authority Control
# Secure key generation, rotation, and authority management for constitutional governance

set -eo pipefail

# Colors for output
GREEN=$(tput setaf 2 2>/dev/null || echo "")
RED=$(tput setaf 1 2>/dev/null || echo "")
YELLOW=$(tput setaf 3 2>/dev/null || echo "")
BLUE=$(tput setaf 4 2>/dev/null || echo "")
RESET=$(tput sgr0 2>/dev/null || echo "")

KEYS_DIR="./keys"
BACKUP_DIR="./keys/backup"

echo "${BLUE}🔐 ACGS-1 Quantumagi Key Management System${RESET}"
echo "============================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo ""

# Create secure key directories
create_key_directories() {
    echo "${BLUE}📁 Creating secure key directories...${RESET}"
    
    mkdir -p "$KEYS_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Set secure permissions
    chmod 700 "$KEYS_DIR"
    chmod 700 "$BACKUP_DIR"
    
    echo "${GREEN}✅ Key directories created with secure permissions${RESET}"
}

# Generate new keypair with secure naming
generate_keypair() {
    local key_name="$1"
    local key_purpose="$2"
    
    if [[ -z "$key_name" ]]; then
        echo "${RED}❌ Key name required${RESET}"
        return 1
    fi
    
    local key_path="$KEYS_DIR/${key_name}-keypair.json"
    
    if [[ -f "$key_path" ]]; then
        echo "${YELLOW}⚠️  Key $key_name already exists at $key_path${RESET}"
        read -p "Overwrite? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Key generation cancelled"
            return 1
        fi
        
        # Backup existing key
        backup_key "$key_name"
    fi
    
    echo "${BLUE}🔑 Generating new keypair: $key_name${RESET}"
    
    # Generate keypair
    solana-keygen new --no-bip39-passphrase --silent --outfile "$key_path"
    
    # Set secure permissions
    chmod 600 "$key_path"
    
    # Get public key
    local pubkey=$(solana-keygen pubkey "$key_path")
    
    echo "${GREEN}✅ Keypair generated successfully${RESET}"
    echo "   Name: $key_name"
    echo "   Purpose: $key_purpose"
    echo "   Public Key: $pubkey"
    echo "   Private Key: $key_path"
    echo ""
    
    # Log key generation
    echo "$(date): Generated keypair $key_name ($key_purpose) - $pubkey" >> "$KEYS_DIR/key_generation.log"
}

# Backup existing key
backup_key() {
    local key_name="$1"
    local key_path="$KEYS_DIR/${key_name}-keypair.json"
    
    if [[ -f "$key_path" ]]; then
        local backup_path="$BACKUP_DIR/${key_name}-keypair-$(date +%Y%m%d_%H%M%S).json"
        cp "$key_path" "$backup_path"
        chmod 600 "$backup_path"
        echo "${GREEN}✅ Key backed up to $backup_path${RESET}"
    fi
}

# Generate program upgrade authority keys
generate_program_authorities() {
    echo "${BLUE}🏛️ Generating program upgrade authority keys...${RESET}"
    
    generate_keypair "quantumagi-upgrade-authority" "Quantumagi Core program upgrade authority"
    generate_keypair "appeals-upgrade-authority" "Appeals program upgrade authority"
    generate_keypair "logging-upgrade-authority" "Logging program upgrade authority"
    
    echo "${GREEN}✅ All program upgrade authority keys generated${RESET}"
}

# Generate governance authority keys
generate_governance_authorities() {
    echo "${BLUE}⚖️ Generating governance authority keys...${RESET}"
    
    generate_keypair "constitution-authority" "Constitutional governance authority"
    generate_keypair "emergency-authority" "Emergency governance authority"
    generate_keypair "policy-authority" "Policy creation and management authority"
    generate_keypair "appeal-reviewer" "Appeal review authority"
    
    echo "${GREEN}✅ All governance authority keys generated${RESET}"
}

# Generate multi-signature setup
generate_multisig_setup() {
    echo "${BLUE}🔐 Generating multi-signature setup...${RESET}"
    
    # Generate individual signer keys
    for i in {1..3}; do
        generate_keypair "multisig-signer-$i" "Multi-signature signer $i for constitutional changes"
    done
    
    echo "${YELLOW}📋 Multi-signature setup requires manual configuration${RESET}"
    echo "   Use the generated signer keys to create a multi-signature account"
    echo "   Recommended threshold: 2 of 3 signers for constitutional changes"
    echo ""
}

# Display key information
display_key_info() {
    echo "${BLUE}📊 Current Key Information${RESET}"
    echo "=========================="
    
    if [[ ! -d "$KEYS_DIR" ]]; then
        echo "${YELLOW}⚠️  No keys directory found${RESET}"
        return 1
    fi
    
    for key_file in "$KEYS_DIR"/*-keypair.json; do
        if [[ -f "$key_file" ]]; then
            local key_name=$(basename "$key_file" -keypair.json)
            local pubkey=$(solana-keygen pubkey "$key_file" 2>/dev/null || echo "ERROR")
            local balance=$(solana balance "$pubkey" 2>/dev/null || echo "0 SOL")
            
            echo "Key: $key_name"
            echo "  Public Key: $pubkey"
            echo "  Balance: $balance"
            echo "  File: $key_file"
            echo ""
        fi
    done
}

# Transfer program upgrade authority
transfer_program_authority() {
    local program_id="$1"
    local new_authority_key="$2"
    local current_authority_key="$3"
    
    if [[ -z "$program_id" || -z "$new_authority_key" || -z "$current_authority_key" ]]; then
        echo "${RED}❌ Usage: transfer_program_authority <program_id> <new_authority_key> <current_authority_key>${RESET}"
        return 1
    fi
    
    echo "${BLUE}🔄 Transferring program upgrade authority...${RESET}"
    echo "   Program: $program_id"
    echo "   New Authority: $(solana-keygen pubkey "$new_authority_key")"
    echo "   Current Authority: $(solana-keygen pubkey "$current_authority_key")"
    
    read -p "Confirm authority transfer? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Authority transfer cancelled"
        return 1
    fi
    
    # Execute authority transfer
    solana program set-upgrade-authority \
        "$program_id" \
        --upgrade-authority "$current_authority_key" \
        --new-upgrade-authority "$(solana-keygen pubkey "$new_authority_key")"
    
    echo "${GREEN}✅ Program upgrade authority transferred successfully${RESET}"
    
    # Log authority transfer
    echo "$(date): Transferred upgrade authority for $program_id to $(solana-keygen pubkey "$new_authority_key")" >> "$KEYS_DIR/authority_transfers.log"
}

# Revoke program upgrade authority (make immutable)
revoke_program_authority() {
    local program_id="$1"
    local current_authority_key="$2"
    
    if [[ -z "$program_id" || -z "$current_authority_key" ]]; then
        echo "${RED}❌ Usage: revoke_program_authority <program_id> <current_authority_key>${RESET}"
        return 1
    fi
    
    echo "${RED}⚠️  WARNING: This will make the program IMMUTABLE!${RESET}"
    echo "   Program: $program_id"
    echo "   Current Authority: $(solana-keygen pubkey "$current_authority_key")"
    echo ""
    echo "   This action CANNOT be undone!"
    
    read -p "Type 'REVOKE' to confirm: " -r
    if [[ "$REPLY" != "REVOKE" ]]; then
        echo "Authority revocation cancelled"
        return 1
    fi
    
    # Execute authority revocation
    solana program set-upgrade-authority \
        "$program_id" \
        --upgrade-authority "$current_authority_key" \
        --new-upgrade-authority null
    
    echo "${GREEN}✅ Program upgrade authority revoked - program is now immutable${RESET}"
    
    # Log authority revocation
    echo "$(date): REVOKED upgrade authority for $program_id - program is now immutable" >> "$KEYS_DIR/authority_transfers.log"
}

# Audit key security
audit_key_security() {
    echo "${BLUE}🔍 Auditing key security...${RESET}"
    
    local issues=0
    
    # Check key directory permissions
    if [[ -d "$KEYS_DIR" ]]; then
        local perms=$(stat -f%A "$KEYS_DIR" 2>/dev/null || stat -c%a "$KEYS_DIR" 2>/dev/null)
        if [[ "$perms" != "700" ]]; then
            echo "${RED}❌ Key directory permissions insecure: $perms (should be 700)${RESET}"
            issues=$((issues + 1))
        else
            echo "${GREEN}✅ Key directory permissions secure${RESET}"
        fi
    fi
    
    # Check individual key file permissions
    for key_file in "$KEYS_DIR"/*-keypair.json; do
        if [[ -f "$key_file" ]]; then
            local perms=$(stat -f%A "$key_file" 2>/dev/null || stat -c%a "$key_file" 2>/dev/null)
            if [[ "$perms" != "600" ]]; then
                echo "${RED}❌ Key file permissions insecure: $(basename "$key_file") ($perms, should be 600)${RESET}"
                issues=$((issues + 1))
            fi
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        echo "${GREEN}✅ All key security checks passed${RESET}"
    else
        echo "${RED}❌ $issues security issues found${RESET}"
    fi
    
    return $issues
}

# Main menu
show_menu() {
    echo "Key Management Options:"
    echo "1. Create key directories"
    echo "2. Generate program upgrade authority keys"
    echo "3. Generate governance authority keys"
    echo "4. Generate multi-signature setup"
    echo "5. Display key information"
    echo "6. Transfer program authority"
    echo "7. Revoke program authority (make immutable)"
    echo "8. Audit key security"
    echo "9. Exit"
    echo ""
}

# Main execution
main() {
    if [[ $# -eq 0 ]]; then
        # Interactive mode
        while true; do
            show_menu
            read -p "Select option (1-9): " choice
            echo ""
            
            case $choice in
                1) create_key_directories ;;
                2) generate_program_authorities ;;
                3) generate_governance_authorities ;;
                4) generate_multisig_setup ;;
                5) display_key_info ;;
                6) 
                    read -p "Program ID: " program_id
                    read -p "New authority key file: " new_auth
                    read -p "Current authority key file: " current_auth
                    transfer_program_authority "$program_id" "$new_auth" "$current_auth"
                    ;;
                7)
                    read -p "Program ID: " program_id
                    read -p "Current authority key file: " current_auth
                    revoke_program_authority "$program_id" "$current_auth"
                    ;;
                8) audit_key_security ;;
                9) echo "Exiting..."; exit 0 ;;
                *) echo "${RED}Invalid option${RESET}" ;;
            esac
            echo ""
        done
    else
        # Command line mode
        case "$1" in
            "init") create_key_directories ;;
            "generate-program") generate_program_authorities ;;
            "generate-governance") generate_governance_authorities ;;
            "generate-multisig") generate_multisig_setup ;;
            "info") display_key_info ;;
            "audit") audit_key_security ;;
            *) echo "Usage: $0 [init|generate-program|generate-governance|generate-multisig|info|audit]" ;;
        esac
    fi
}

# Run main function
main "$@"
