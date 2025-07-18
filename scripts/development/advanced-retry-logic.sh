# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Advanced retry logic with exponential backoff
# For critical connectivity checks

set -e

# Configuration
MAX_RETRIES=5
BASE_DELAY=2
MAX_DELAY=60

# Exponential backoff retry function
retry_with_backoff() {
    local command="$1"
    local description="$2"
    local attempt=1
    local delay=$BASE_DELAY
    
    while [[ $attempt -le $MAX_RETRIES ]]; do
        echo "🔄 Attempt $attempt/$MAX_RETRIES: $description"
        
        if eval "$command"; then
            echo "✅ Success on attempt $attempt"
            return 0
        fi
        
        if [[ $attempt -lt $MAX_RETRIES ]]; then
            echo "⏳ Waiting ${delay}s before retry..."
            sleep "$delay"
            
            # Exponential backoff with jitter
            delay=$((delay * 2))
            if [[ $delay -gt $MAX_DELAY ]]; then
                delay=$MAX_DELAY
            fi
            
            # Add random jitter (0-25% of delay)
            local jitter=$((delay / 4))
            local random_jitter=$((RANDOM % jitter))
            delay=$((delay + random_jitter))
        fi
        
        ((attempt++))
    done
    
    echo "❌ Failed after $MAX_RETRIES attempts: $description"
    return 1
}

# GitHub connectivity check with advanced retry
github_connectivity_check() {
    echo "🚀 Starting advanced GitHub connectivity check..."
    
    # Test 1: Basic HTTP connectivity
    if retry_with_backoff "curl -s --max-time 10 --head https://github.com >/dev/null 2>&1" "GitHub main site connectivity"; then
        echo "✅ GitHub main site accessible"
    else
        echo "❌ GitHub main site not accessible"
        return 1
    fi
    
    # Test 2: API connectivity
    if retry_with_backoff "curl -s --max-time 10 https://api.github.com/zen >/dev/null 2>&1" "GitHub API connectivity"; then
        echo "✅ GitHub API accessible"
    else
        echo "⚠️  GitHub API not accessible (but main site works)"
    fi
    
    echo "🎉 Advanced connectivity check completed successfully!"
    return 0
}

# Main execution
main() {
    if github_connectivity_check; then
        echo "✅ All connectivity checks passed!"
        exit 0
    else
        echo "❌ Connectivity checks failed!"
        exit 1
    fi
}

main "$@"
