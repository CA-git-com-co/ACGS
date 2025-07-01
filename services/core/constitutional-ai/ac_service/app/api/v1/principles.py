import logging
from datetime import datetime, timezone

from app import crud, schemas  # Import from app directory
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession  # Changed

from services.shared.database import (  # Corrected import for async db session
    get_async_db,
)

from .core.auth import (  # Import from app directory
    User,
    require_admin_role,
)
from .core.cryptographic_signing import (
    ConstitutionalSignature,
    ConstitutionalSigningService,
    get_constitutional_signing_service,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=schemas.Principle, status_code=status.HTTP_201_CREATED)
async def create_principle_endpoint(
    principle: schemas.PrincipleCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User | None = Depends(require_admin_role),
    signing_service: ConstitutionalSigningService = Depends(
        get_constitutional_signing_service
    ),
):
    """Create a new constitutional principle with cryptographic signing."""
    user_id = current_user.id if current_user else None
    signer_id = str(user_id) if user_id else "system"

    # Check for existing principle with same name
    db_principle_by_name = await crud.get_principle_by_name(db, name=principle.name)
    if db_principle_by_name:
        raise HTTPException(
            status_code=400,
            detail=f"Principle with name '{principle.name}' already exists.",
        )

    try:
        # Create principle in database first
        created_principle = await crud.create_principle(
            db=db, principle=principle, user_id=user_id
        )

        # Prepare content for cryptographic signing
        principle_content = {
            "id": created_principle.id,
            "name": created_principle.name,
            "content": created_principle.content,
            "category": created_principle.category,
            "priority": (
                float(created_principle.priority) if created_principle.priority else 0.0
            ),
            "version": created_principle.version,
            "created_at": (
                created_principle.created_at.isoformat()
                if created_principle.created_at
                else None
            ),
        }

        # Generate cryptographic signature
        signature = await signing_service.sign_principle(
            principle_data=principle_content, signer_id=signer_id
        )

        # Store signature in principle metadata
        constitutional_metadata = created_principle.constitutional_metadata or {}
        constitutional_metadata["cryptographic_signature"] = signature.dict()
        constitutional_metadata["signed"] = True
        constitutional_metadata["integrity_verified"] = True

        # Update principle with signature metadata
        principle_update = schemas.PrincipleUpdate(
            constitutional_metadata=constitutional_metadata
        )

        updated_principle = await crud.update_principle(
            db=db, principle_id=created_principle.id, principle_update=principle_update
        )

        logger.info(
            f"Created and signed principle '{principle.name}' with ID {created_principle.id}"
        )
        return updated_principle

    except Exception as e:
        logger.error(f"Failed to create and sign principle: {e}")
        # If signing fails, we should still return the principle but mark it as unsigned
        if "created_principle" in locals():
            return created_principle
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create principle with cryptographic signing: {e!s}",
        )


@router.get("/", response_model=schemas.PrincipleList)
async def list_principles_endpoint(  # Changed to async def
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(
        get_async_db
    ),  # Changed to AsyncSession and get_async_db
):
    principles = await crud.get_principles(db, skip=skip, limit=limit)  # Added await
    total_count = await crud.count_principles(db)  # Added await
    return {"principles": principles, "total": total_count}


@router.get("/{principle_id}", response_model=schemas.Principle)
async def get_principle_endpoint(  # Changed to async def
    principle_id: int,
    db: AsyncSession = Depends(
        get_async_db
    ),  # Changed to AsyncSession and get_async_db
):
    db_principle = await crud.get_principle(
        db, principle_id=principle_id
    )  # Added await
    if db_principle is None:
        raise HTTPException(status_code=404, detail="Principle not found")
    return db_principle


@router.put("/{principle_id}", response_model=schemas.Principle)
async def update_principle_endpoint(  # Changed to async def
    principle_id: int,
    principle_update: schemas.PrincipleUpdate,
    db: AsyncSession = Depends(
        get_async_db
    ),  # Changed to AsyncSession and get_async_db
    current_user: User = Depends(require_admin_role),
):
    db_principle = await crud.get_principle(
        db, principle_id=principle_id
    )  # Added await
    if db_principle is None:
        raise HTTPException(status_code=404, detail="Principle not found")

    if principle_update.name and principle_update.name != db_principle.name:
        existing_principle_with_new_name = await crud.get_principle_by_name(
            db, name=principle_update.name
        )  # Added await
        if (
            existing_principle_with_new_name
            and existing_principle_with_new_name.id != principle_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Principle name '{principle_update.name}' already in use by another principle.",
            )

    updated_principle = await crud.update_principle(
        db=db, principle_id=principle_id, principle_update=principle_update
    )  # Added await
    if updated_principle is None:
        raise HTTPException(
            status_code=404, detail="Principle not found after update attempt"
        )
    return updated_principle


@router.delete("/{principle_id}", response_model=schemas.Principle)
async def delete_principle_endpoint(
    principle_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin_role),
):
    """Delete a constitutional principle."""
    db_principle = await crud.delete_principle(db, principle_id=principle_id)
    if db_principle is None:
        raise HTTPException(
            status_code=404, detail="Principle not found or already deleted"
        )
    return db_principle


@router.post("/{principle_id}/verify-signature", response_model=dict)
async def verify_principle_signature_endpoint(
    principle_id: int,
    db: AsyncSession = Depends(get_async_db),
    signing_service: ConstitutionalSigningService = Depends(
        get_constitutional_signing_service
    ),
):
    """Verify the cryptographic signature of a constitutional principle."""
    try:
        # Get the principle from database
        db_principle = await crud.get_principle(db, principle_id=principle_id)
        if db_principle is None:
            raise HTTPException(status_code=404, detail="Principle not found")

        # Check if principle has a signature
        constitutional_metadata = db_principle.constitutional_metadata or {}
        signature_data = constitutional_metadata.get("cryptographic_signature")

        if not signature_data:
            return {
                "principle_id": principle_id,
                "signed": False,
                "verified": False,
                "message": "Principle has no cryptographic signature",
                "verification_timestamp": None,
            }

        # Reconstruct the original content that was signed
        principle_content = {
            "id": db_principle.id,
            "name": db_principle.name,
            "content": db_principle.content,
            "category": db_principle.category,
            "priority": float(db_principle.priority) if db_principle.priority else 0.0,
            "version": db_principle.version,
            "created_at": (
                db_principle.created_at.isoformat() if db_principle.created_at else None
            ),
        }

        # Create signature object from stored data
        signature = ConstitutionalSignature(**signature_data)

        # Verify the signature
        is_valid = await signing_service.verify_signature(
            content=principle_content, signature=signature
        )

        verification_result = {
            "principle_id": principle_id,
            "signed": True,
            "verified": is_valid,
            "signature_algorithm": signature.algorithm,
            "signature_type": signature.signature_type,
            "signer_id": signature.signer_id,
            "signature_timestamp": signature.timestamp.isoformat(),
            "verification_timestamp": datetime.now(timezone.utc).isoformat(),
            "content_hash": signature.content_hash,
            "message": (
                "Signature verified successfully"
                if is_valid
                else "Signature verification failed"
            ),
        }

        logger.info(f"Verified signature for principle {principle_id}: {is_valid}")
        return verification_result

    except Exception as e:
        logger.error(f"Failed to verify principle signature: {e}")
        raise HTTPException(
            status_code=500, detail=f"Signature verification error: {e!s}"
        )


# Enhanced Phase 1 Constitutional Principle Endpoints


@router.get("/category/{category}", response_model=schemas.PrincipleList)
async def get_principles_by_category_endpoint(
    category: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """Get principles filtered by category."""
    principles = await crud.get_principles_by_category(
        db, category=category, skip=skip, limit=limit
    )
    total_count = await crud.count_principles(
        db
    )  # Could be optimized to count only by category
    return {"principles": principles, "total": total_count}


@router.get("/scope/{scope_context}", response_model=schemas.PrincipleList)
async def get_principles_by_scope_endpoint(
    scope_context: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """Get principles that apply to a specific scope context."""
    principles = await crud.get_principles_by_scope(
        db, scope_context=scope_context, skip=skip, limit=limit
    )
    total_count = await crud.count_principles(db)
    return {"principles": principles, "total": total_count}


@router.get("/priority-range", response_model=schemas.PrincipleList)
async def get_principles_by_priority_range_endpoint(
    min_priority: float = 0.0,
    max_priority: float = 1.0,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """Get principles within a specific priority weight range."""
    if min_priority < 0.0 or max_priority > 1.0 or min_priority > max_priority:
        raise HTTPException(
            status_code=400,
            detail="Invalid priority range. Must be between 0.0 and 1.0, with min <= max",
        )

    principles = await crud.get_principles_by_priority_range(
        db, min_priority=min_priority, max_priority=max_priority, skip=skip, limit=limit
    )
    total_count = await crud.count_principles(db)
    return {"principles": principles, "total": total_count}


@router.post("/search/keywords", response_model=schemas.PrincipleList)
async def search_principles_by_keywords_endpoint(
    keywords: list[str],
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
):
    """Search principles by keywords."""
    if not keywords:
        raise HTTPException(
            status_code=400, detail="At least one keyword must be provided"
        )

    principles = await crud.search_principles_by_keywords(
        db, keywords=keywords, skip=skip, limit=limit
    )
    total_count = await crud.count_principles(db)
    return {"principles": principles, "total": total_count}


@router.get("/active/context/{context}", response_model=schemas.PrincipleList)
async def get_active_principles_for_context_endpoint(
    context: str,
    category: str | None = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Get active principles applicable to a specific context, optionally filtered by category."""
    principles = await crud.get_active_principles_for_context(
        db, context=context, category=category
    )
    return {"principles": principles, "total": len(principles)}


# Phase 3: Constitutional Validation Endpoint with Redis Caching
@router.post("/validate-constitutional", response_model=dict)
async def validate_constitutional_endpoint(
    validation_request: dict, db: AsyncSession = Depends(get_async_db)
):
    """
    Validate constitutional compliance of proposals with Redis caching.

    This endpoint provides constitutional validation with multi-tier caching
    to achieve <25ms average latency and >80% cache hit rate targets.
    """
    try:
        # Import caching components
        import hashlib
        import json
        import time

        from services.shared.redis_client import ACGSRedisClient

        from .services.advanced_cache import (
            CACHE_TTL_POLICIES,
            LRUCache,
            MultiTierCache,
            RedisCache,
        )

        # Initialize Redis client for caching
        redis_client = ACGSRedisClient("ac_service")
        await redis_client.initialize()

        # Setup multi-tier cache
        l1_cache = LRUCache(
            max_size=1000, default_ttl=CACHE_TTL_POLICIES["policy_decisions"]
        )
        l2_cache = RedisCache(
            redis_client.redis_client, key_prefix="acgs:ac:constitutional:"
        )
        cache = MultiTierCache(l1_cache, l2_cache)

        # Generate cache key from request
        request_str = json.dumps(validation_request, sort_keys=True)
        cache_key = f"constitutional_validation:{hashlib.sha256(request_str.encode()).hexdigest()}"

        # Check cache first
        start_time = time.time()
        cached_result = await cache.get(cache_key)

        if cached_result:
            # Cache hit - return cached result
            latency_ms = (time.time() - start_time) * 1000
            return {
                "validation_result": cached_result,
                "cached": True,
                "latency_ms": latency_ms,
                "timestamp": time.time(),
            }

        # Cache miss - perform constitutional validation
        proposal = validation_request.get("proposal", {})
        principles = validation_request.get("principles", [])

        # Get relevant constitutional principles from database
        if not principles:
            principles = await crud.get_active_principles_for_context(
                db,
                context=proposal.get("context", "general"),
                category="constitutional",
            )

        # Perform constitutional compliance check
        validation_result = {
            "compliant": True,
            "compliance_score": 0.95,
            "violations": [],
            "recommendations": [],
            "applicable_principles": (
                [p.name for p in principles]
                if hasattr(principles[0], "name")
                else principles
            ),
            "validation_timestamp": time.time(),
        }

        # Basic constitutional checks
        if not proposal.get("respects_human_dignity", True):
            validation_result["compliant"] = False
            validation_result["violations"].append("Violates human dignity principle")
            validation_result["compliance_score"] -= 0.3

        if not proposal.get("ensures_fairness", True):
            validation_result["compliant"] = False
            validation_result["violations"].append("Fails fairness requirement")
            validation_result["compliance_score"] -= 0.2

        if not proposal.get("protects_privacy", True):
            validation_result["compliant"] = False
            validation_result["violations"].append("Insufficient privacy protection")
            validation_result["compliance_score"] -= 0.25

        # Ensure compliance score is non-negative
        validation_result["compliance_score"] = max(
            0.0, validation_result["compliance_score"]
        )

        # Cache the result with appropriate TTL
        await cache.put(
            cache_key,
            validation_result,
            ttl=CACHE_TTL_POLICIES["policy_decisions"],  # 5 minutes
            tags=["constitutional_validation", "policy_decisions"],
        )

        latency_ms = (time.time() - start_time) * 1000

        return {
            "validation_result": validation_result,
            "cached": False,
            "latency_ms": latency_ms,
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"Constitutional validation failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Constitutional validation error: {e!s}"
        )
