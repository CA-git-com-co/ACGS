# Import shared authentication utilities
import sys

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


sys.path.append("/home/dislove/ACGS-1/services/shared")
from auth import (
    RoleChecker,
    get_current_active_user,
    get_current_user_from_token,
    require_pgc_admin,
)

# PGC service specific role checkers
require_pgc_admin = require_pgc_admin
require_policy_evaluation_triggerer = RoleChecker(
    allowed_roles=["policy_requester", "pgc_admin", "internal_service", "admin"]
)

# Backward compatibility aliases for existing code
get_current_user_placeholder = get_current_user_from_token
get_current_active_user_placeholder = get_current_active_user

# Role checkers are imported from services.shared.auth above
