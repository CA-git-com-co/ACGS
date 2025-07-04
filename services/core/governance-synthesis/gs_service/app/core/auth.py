# Import shared authentication utilities
from services.shared.auth import (

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    RoleChecker,
    get_current_active_user,
    get_current_user_from_token,
    require_gs_admin,
)

# GS service specific role checkers
require_gs_admin = require_gs_admin
require_synthesis_triggerer = RoleChecker(
    allowed_roles=["gs_admin", "internal_service", "admin"]
)

# Backward compatibility aliases for existing code
get_current_user_placeholder = get_current_user_from_token
get_current_active_user_placeholder = get_current_active_user

# Role checkers are imported from services.shared.auth above
