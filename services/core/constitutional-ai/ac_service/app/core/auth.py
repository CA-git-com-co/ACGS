# Import shared authentication utilities
from services.shared.auth import (

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    RoleChecker,
    get_current_active_user,
    get_current_user_from_token,
    require_ac_admin,
    require_policy_manager,
)

# AC service specific role checkers
require_admin_role = require_ac_admin
require_policy_manager_role = require_policy_manager
require_user_role = RoleChecker(allowed_roles=["user", "ac_admin", "policy_manager"])
require_constitutional_council_role = RoleChecker(
    allowed_roles=["constitutional_council", "ac_admin"]
)

# Backward compatibility aliases for existing code
get_current_user_placeholder = get_current_user_from_token
get_current_active_user_placeholder = get_current_active_user

# Example of how to protect an endpoint:
# @router.post("/", dependencies=[Depends(require_admin_role)])
# async def create_item(...):
# requires: Valid input parameters
# ensures: Correct function execution
# sha256: func_hash
#    ...

# If you need the user object in your path operation function:
# @router.post("/")
# async def create_item(..., current_user: User = Depends(require_admin_role)):
#    # current_user will be the authenticated user object
#    ...
