# Import shared authentication utilities
from services.shared.auth import (

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    get_current_active_user,
    get_current_user_from_token,
    require_auditor,
    require_integrity_admin,
    require_internal_service,
)

# Integrity service specific role checkers
require_integrity_admin = require_integrity_admin
require_auditor = require_auditor
require_internal_service = require_internal_service

# Backward compatibility aliases for existing code
get_current_user_placeholder = get_current_user_from_token
get_current_active_user_placeholder = get_current_active_user

# Role checkers are imported from services.shared.auth above
