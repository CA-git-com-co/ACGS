# ACGS-1 Lite Constitutional Policies - Main Entry Point
# Constitutional Hash: cdd01ef066bc6cf2

package acgs.main

import data.acgs.constitutional
import data.acgs.evolution
import data.acgs.data

# Constitutional hash verification
constitutional_hash := "cdd01ef066bc6cf2"

# Default deny policy - explicit authorization required
default allow = false
default decision = {
    "allow": false,
    "reason": "No matching policy found",
    "constitutional_hash": constitutional_hash
}

# Main decision entry point
decision = response {
    # Verify constitutional hash if provided
    input.constitutional_hash == constitutional_hash
    
    # Route to appropriate policy based on request type
    response := route_request(input)
}

# Route requests to appropriate policy modules
route_request(input) = response {
    input.type == "constitutional_evaluation"
    response := constitutional.evaluate
}

route_request(input) = response {
    input.type == "evolution_approval"
    response := evolution.evaluate
}

route_request(input) = response {
    input.type == "data_access"
    response := data.evaluate
}

route_request(input) = response {
    input.type == "action_authorization"
    response := constitutional.evaluate
}

# Fallback for unrecognized request types
route_request(input) = response {
    not input.type in ["constitutional_evaluation", "evolution_approval", "data_access", "action_authorization"]
    response := {
        "allow": false,
        "reason": sprintf("Unknown request type: %s", [input.type]),
        "constitutional_hash": constitutional_hash
    }
}

# Simplified allow for basic compatibility
allow {
    decision.allow
}

# Health check endpoint
health = {
    "status": "healthy",
    "constitutional_hash": constitutional_hash,
    "policies_loaded": [
        "acgs.constitutional",
        "acgs.evolution", 
        "acgs.data",
        "acgs.main"
    ]
}