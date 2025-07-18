"""
Blackboard Coordination Service
Constitutional Hash: cdd01ef066bc6cf2

FastAPI service implementing blackboard architecture for multi-agent
collaboration through shared knowledge spaces.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator
import asyncio
import json
import os
import uuid
from collections import defaultdict
import time

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Models
class BlackboardEntry(BaseModel):
    """Entry in the blackboard system"""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str
    author_id: str
    entry_type: str
    title: str
    content: Dict[str, Any]
    tags: List[str] = []
    priority: int = Field(ge=1, le=10, default=5)
    visibility: str = "public"  # public, team, private
    status: str = "active"  # active, archived, deleted
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    access_count: int = 0
    subscribers: List[str] = []
    dependencies: List[str] = []  # Other entry IDs this depends on
    constitutional_hash: str = CONSTITUTIONAL_HASH


class Workspace(BaseModel):
    """Collaborative workspace"""

    workspace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    owner_id: str
    participants: List[str] = []
    workspace_type: str = "collaborative"  # collaborative, competitive, hierarchical
    access_policy: str = "open"  # open, invite_only, restricted
    max_entries: int = Field(ge=1, default=1000)
    current_entries: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = {}
    constitutional_compliance: bool = True


class Subscription(BaseModel):
    """Agent subscription to workspace or entry"""

    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subscriber_id: str
    target_type: str  # workspace, entry, tag
    target_id: str
    notification_types: List[str] = ["created", "updated", "deleted"]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = True


class Notification(BaseModel):
    """Notification for subscribers"""

    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    recipient_id: str
    notification_type: str
    title: str
    content: Dict[str, Any]
    priority: str = "normal"  # low, normal, high, urgent
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read: bool = False
    delivered: bool = False


class BlackboardQuery(BaseModel):
    """Query for searching blackboard entries"""

    workspace_id: Optional[str] = None
    entry_type: Optional[str] = None
    tags: List[str] = []
    author_id: Optional[str] = None
    content_search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(ge=1, le=100, default=20)
    offset: int = Field(ge=0, default=0)


# Global storage (in production, would use Redis/Database)
blackboard_storage = {
    "workspaces": {},
    "entries": {},
    "subscriptions": {},
    "notifications": {},
    "entry_index": defaultdict(list),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Blackboard Coordination Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Initialize default workspace
    await initialize_default_workspace()

    # Start background tasks
    asyncio.create_task(cleanup_expired_entries())
    asyncio.create_task(notification_processor())

    yield

    logger.info("Shutting down Blackboard Coordination Service")


app = FastAPI(
    title="Blackboard Coordination Service",
    description="Shared knowledge space for multi-agent collaboration",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def initialize_default_workspace():
    """Initialize default workspace for testing"""
    default_workspace = Workspace(
        name="Default Collaborative Space",
        description="Default workspace for multi-agent collaboration",
        owner_id="system",
        participants=["system"],
        workspace_type="collaborative",
        access_policy="open",
    )

    blackboard_storage["workspaces"][default_workspace.workspace_id] = default_workspace

    # Add sample entries
    sample_entries = [
        BlackboardEntry(
            workspace_id=default_workspace.workspace_id,
            author_id="system",
            entry_type="knowledge",
            title="Constitutional Compliance Guidelines",
            content={
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "guidelines": [
                    "All operations must maintain constitutional compliance",
                    "Performance targets: P99 <5ms, >100 RPS, >85% cache hit rate",
                    "Constitutional validation required for all critical operations",
                ],
                "enforcement_level": "strict",
            },
            tags=["constitutional", "compliance", "guidelines"],
            priority=10,
        ),
        BlackboardEntry(
            workspace_id=default_workspace.workspace_id,
            author_id="system",
            entry_type="protocol",
            title="Multi-Agent Coordination Protocol",
            content={
                "coordination_patterns": [
                    "hierarchical",
                    "flat",
                    "blackboard",
                    "contract_net",
                    "auction",
                    "team",
                ],
                "best_practices": [
                    "Use appropriate pattern for task complexity",
                    "Monitor performance continuously",
                    "Maintain constitutional compliance",
                ],
            },
            tags=["coordination", "protocol", "multi-agent"],
            priority=8,
        ),
        BlackboardEntry(
            workspace_id=default_workspace.workspace_id,
            author_id="system",
            entry_type="resource",
            title="Available Service Endpoints",
            content={
                "services": {
                    "constitutional_core": "http://localhost:8001",
                    "multi_agent_coordination": "http://localhost:8008",
                    "worker_agents": "http://localhost:8009",
                    "blackboard_coordination": "http://localhost:8010",
                },
                "health_checks": {
                    "constitutional_core": "http://localhost:8001/health",
                    "multi_agent_coordination": "http://localhost:8008/health",
                    "worker_agents": "http://localhost:8009/health",
                },
            },
            tags=["services", "endpoints", "resources"],
            priority=6,
        ),
    ]

    for entry in sample_entries:
        blackboard_storage["entries"][entry.entry_id] = entry
        default_workspace.current_entries += 1

        # Index for search
        blackboard_storage["entry_index"]["workspace:" + entry.workspace_id].append(
            entry.entry_id
        )
        blackboard_storage["entry_index"]["type:" + entry.entry_type].append(
            entry.entry_id
        )
        for tag in entry.tags:
            blackboard_storage["entry_index"]["tag:" + tag].append(entry.entry_id)

    logger.info(f"Initialized default workspace with {len(sample_entries)} entries")


async def cleanup_expired_entries():
    """Background task to clean up expired entries"""
    while True:
        try:
            current_time = datetime.utcnow()
            expired_entries = []

            for entry_id, entry in blackboard_storage["entries"].items():
                if entry.expires_at and entry.expires_at <= current_time:
                    expired_entries.append(entry_id)

            for entry_id in expired_entries:
                entry = blackboard_storage["entries"][entry_id]
                entry.status = "archived"
                logger.info(f"Archived expired entry: {entry_id}")

            await asyncio.sleep(300)  # Check every 5 minutes

        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
            await asyncio.sleep(60)


async def notification_processor():
    """Process and deliver notifications"""
    while True:
        try:
            delivered_count = 0

            for notification in blackboard_storage["notifications"].values():
                if not notification.delivered:
                    # In production, would send via websocket/webhook
                    notification.delivered = True
                    delivered_count += 1

            if delivered_count > 0:
                logger.info(f"Delivered {delivered_count} notifications")

            await asyncio.sleep(5)  # Process every 5 seconds

        except Exception as e:
            logger.error(f"Notification processor error: {e}")
            await asyncio.sleep(30)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    total_workspaces = len(blackboard_storage["workspaces"])
    total_entries = len(blackboard_storage["entries"])
    active_entries = sum(
        1
        for entry in blackboard_storage["entries"].values()
        if entry.status == "active"
    )

    return {
        "status": "healthy",
        "service": "blackboard-coordination",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": {
            "workspaces": total_workspaces,
            "total_entries": total_entries,
            "active_entries": active_entries,
            "subscriptions": len(blackboard_storage["subscriptions"]),
        },
    }


# Workspace Management
@app.post("/api/v1/workspaces", response_model=Workspace)
async def create_workspace(workspace: Workspace):
    """Create a new workspace"""

    # Validate constitutional compliance
    if not workspace.constitutional_compliance:
        raise HTTPException(
            status_code=400, detail="Workspace must maintain constitutional compliance"
        )

    blackboard_storage["workspaces"][workspace.workspace_id] = workspace

    logger.info(f"Created workspace: {workspace.workspace_id}")
    return workspace


@app.get("/api/v1/workspaces", response_model=List[Workspace])
async def list_workspaces(
    owner_id: Optional[str] = None, workspace_type: Optional[str] = None
):
    """List workspaces with optional filters"""
    workspaces = list(blackboard_storage["workspaces"].values())

    if owner_id:
        workspaces = [w for w in workspaces if w.owner_id == owner_id]

    if workspace_type:
        workspaces = [w for w in workspaces if w.workspace_type == workspace_type]

    return workspaces


@app.get("/api/v1/workspaces/{workspace_id}", response_model=Workspace)
async def get_workspace(workspace_id: str):
    """Get specific workspace"""
    if workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return blackboard_storage["workspaces"][workspace_id]


@app.put("/api/v1/workspaces/{workspace_id}", response_model=Workspace)
async def update_workspace(workspace_id: str, updates: Dict[str, Any]):
    """Update workspace settings"""
    if workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    workspace = blackboard_storage["workspaces"][workspace_id]

    # Apply updates
    for key, value in updates.items():
        if hasattr(workspace, key) and key != "workspace_id":
            setattr(workspace, key, value)

    workspace.last_activity = datetime.utcnow()

    return workspace


# Entry Management
@app.post("/api/v1/entries", response_model=BlackboardEntry)
async def create_entry(entry: BlackboardEntry):
    """Create a new blackboard entry"""

    # Validate workspace exists
    if entry.workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    workspace = blackboard_storage["workspaces"][entry.workspace_id]

    # Check workspace capacity
    if workspace.current_entries >= workspace.max_entries:
        raise HTTPException(status_code=400, detail="Workspace at maximum capacity")

    # Validate constitutional hash
    if entry.constitutional_hash != CONSTITUTIONAL_HASH:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid constitutional hash. Expected {CONSTITUTIONAL_HASH}",
        )

    # Store entry
    blackboard_storage["entries"][entry.entry_id] = entry
    workspace.current_entries += 1
    workspace.last_activity = datetime.utcnow()

    # Update search index
    blackboard_storage["entry_index"]["workspace:" + entry.workspace_id].append(
        entry.entry_id
    )
    blackboard_storage["entry_index"]["type:" + entry.entry_type].append(entry.entry_id)
    for tag in entry.tags:
        blackboard_storage["entry_index"]["tag:" + tag].append(entry.entry_id)

    # Notify subscribers
    await notify_subscribers(entry, "created")

    logger.info(f"Created entry: {entry.entry_id} in workspace: {entry.workspace_id}")
    return entry


@app.get("/api/v1/entries/{entry_id}", response_model=BlackboardEntry)
async def get_entry(entry_id: str):
    """Get specific entry"""
    if entry_id not in blackboard_storage["entries"]:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry = blackboard_storage["entries"][entry_id]
    entry.access_count += 1

    return entry


@app.put("/api/v1/entries/{entry_id}", response_model=BlackboardEntry)
async def update_entry(entry_id: str, updates: Dict[str, Any]):
    """Update entry content"""
    if entry_id not in blackboard_storage["entries"]:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry = blackboard_storage["entries"][entry_id]

    # Create new version
    entry.version += 1
    entry.updated_at = datetime.utcnow()

    # Apply updates
    for key, value in updates.items():
        if hasattr(entry, key) and key not in ["entry_id", "created_at", "version"]:
            setattr(entry, key, value)

    # Notify subscribers
    await notify_subscribers(entry, "updated")

    return entry


@app.delete("/api/v1/entries/{entry_id}")
async def delete_entry(entry_id: str):
    """Delete entry (mark as deleted)"""
    if entry_id not in blackboard_storage["entries"]:
        raise HTTPException(status_code=404, detail="Entry not found")

    entry = blackboard_storage["entries"][entry_id]
    entry.status = "deleted"
    entry.updated_at = datetime.utcnow()

    # Update workspace count
    workspace = blackboard_storage["workspaces"][entry.workspace_id]
    workspace.current_entries = max(0, workspace.current_entries - 1)

    # Notify subscribers
    await notify_subscribers(entry, "deleted")

    return {"message": "Entry deleted", "entry_id": entry_id}


# Search and Query
@app.post("/api/v1/entries/search", response_model=List[BlackboardEntry])
async def search_entries(query: BlackboardQuery):
    """Search entries with advanced filtering"""

    # Start with all entries or workspace-specific entries
    candidate_ids = set()

    if query.workspace_id:
        workspace_key = "workspace:" + query.workspace_id
        candidate_ids = set(blackboard_storage["entry_index"].get(workspace_key, []))
    else:
        candidate_ids = set(blackboard_storage["entries"].keys())

    # Filter by entry type
    if query.entry_type:
        type_key = "type:" + query.entry_type
        type_ids = set(blackboard_storage["entry_index"].get(type_key, []))
        candidate_ids = candidate_ids.intersection(type_ids)

    # Filter by tags
    for tag in query.tags:
        tag_key = "tag:" + tag
        tag_ids = set(blackboard_storage["entry_index"].get(tag_key, []))
        candidate_ids = candidate_ids.intersection(tag_ids)

    # Apply additional filters
    results = []
    for entry_id in candidate_ids:
        if entry_id not in blackboard_storage["entries"]:
            continue

        entry = blackboard_storage["entries"][entry_id]

        # Skip deleted entries
        if entry.status == "deleted":
            continue

        # Filter by author
        if query.author_id and entry.author_id != query.author_id:
            continue

        # Filter by date range
        if query.date_from and entry.created_at < query.date_from:
            continue
        if query.date_to and entry.created_at > query.date_to:
            continue

        # Content search (simple text search)
        if query.content_search:
            content_str = json.dumps(entry.content).lower()
            if (
                query.content_search.lower() not in content_str
                and query.content_search.lower() not in entry.title.lower()
            ):
                continue

        results.append(entry)

    # Sort by priority (descending) then by creation date (descending)
    results.sort(key=lambda e: (-e.priority, -e.created_at.timestamp()))

    # Apply pagination
    start = query.offset
    end = start + query.limit

    return results[start:end]


@app.get(
    "/api/v1/workspaces/{workspace_id}/entries", response_model=List[BlackboardEntry]
)
async def get_workspace_entries(
    workspace_id: str,
    entry_type: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, ge=1, le=100),
):
    """Get entries for specific workspace"""
    if workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Build query
    query = BlackboardQuery(
        workspace_id=workspace_id,
        entry_type=entry_type,
        tags=tags.split(",") if tags else [],
        limit=limit,
    )

    return await search_entries(query)


# Subscription Management
@app.post("/api/v1/subscriptions", response_model=Subscription)
async def create_subscription(subscription: Subscription):
    """Create subscription for notifications"""

    # Validate target exists
    if subscription.target_type == "workspace":
        if subscription.target_id not in blackboard_storage["workspaces"]:
            raise HTTPException(status_code=404, detail="Workspace not found")
    elif subscription.target_type == "entry":
        if subscription.target_id not in blackboard_storage["entries"]:
            raise HTTPException(status_code=404, detail="Entry not found")

    blackboard_storage["subscriptions"][subscription.subscription_id] = subscription

    return subscription


@app.get("/api/v1/subscriptions/{subscriber_id}", response_model=List[Subscription])
async def get_subscriptions(subscriber_id: str):
    """Get subscriptions for subscriber"""
    subscriptions = [
        sub
        for sub in blackboard_storage["subscriptions"].values()
        if sub.subscriber_id == subscriber_id and sub.active
    ]

    return subscriptions


@app.delete("/api/v1/subscriptions/{subscription_id}")
async def cancel_subscription(subscription_id: str):
    """Cancel subscription"""
    if subscription_id not in blackboard_storage["subscriptions"]:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription = blackboard_storage["subscriptions"][subscription_id]
    subscription.active = False

    return {"message": "Subscription cancelled", "subscription_id": subscription_id}


# Notification Management
@app.get("/api/v1/notifications/{recipient_id}", response_model=List[Notification])
async def get_notifications(
    recipient_id: str,
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, ge=1, le=100),
):
    """Get notifications for recipient"""
    notifications = [
        notif
        for notif in blackboard_storage["notifications"].values()
        if notif.recipient_id == recipient_id
    ]

    if unread_only:
        notifications = [n for n in notifications if not n.read]

    # Sort by creation date (newest first)
    notifications.sort(key=lambda n: n.created_at, reverse=True)

    return notifications[:limit]


@app.put("/api/v1/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark notification as read"""
    if notification_id not in blackboard_storage["notifications"]:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification = blackboard_storage["notifications"][notification_id]
    notification.read = True

    return {"message": "Notification marked as read"}


# Real-time Features
@app.get("/api/v1/workspaces/{workspace_id}/stream")
async def stream_workspace_updates(workspace_id: str):
    """Stream real-time updates for workspace"""
    if workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    async def event_stream() -> AsyncGenerator[str, None]:
        last_check = datetime.utcnow()

        while True:
            try:
                # Find recent entries in workspace
                recent_entries = []
                for entry in blackboard_storage["entries"].values():
                    if (
                        entry.workspace_id == workspace_id
                        and entry.updated_at > last_check
                    ):
                        recent_entries.append(entry)

                # Send updates
                for entry in recent_entries:
                    event_data = {
                        "type": "entry_update",
                        "entry_id": entry.entry_id,
                        "title": entry.title,
                        "author_id": entry.author_id,
                        "updated_at": entry.updated_at.isoformat(),
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"

                last_check = datetime.utcnow()
                await asyncio.sleep(2)  # Check every 2 seconds

            except Exception as e:
                logger.error(f"Stream error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                break

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# Analytics and Insights
@app.get("/api/v1/analytics/workspace/{workspace_id}")
async def get_workspace_analytics(workspace_id: str):
    """Get analytics for workspace"""
    if workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    workspace = blackboard_storage["workspaces"][workspace_id]

    # Collect analytics
    entries = [
        entry
        for entry in blackboard_storage["entries"].values()
        if entry.workspace_id == workspace_id and entry.status == "active"
    ]

    entry_types = defaultdict(int)
    tag_usage = defaultdict(int)
    author_activity = defaultdict(int)

    for entry in entries:
        entry_types[entry.entry_type] += 1
        author_activity[entry.author_id] += 1
        for tag in entry.tags:
            tag_usage[tag] += 1

    return {
        "workspace_id": workspace_id,
        "workspace_name": workspace.name,
        "total_entries": len(entries),
        "total_access_count": sum(entry.access_count for entry in entries),
        "entry_types": dict(entry_types),
        "popular_tags": dict(
            sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)[:10]
        ),
        "most_active_authors": dict(
            sorted(author_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        ),
        "recent_activity": len(
            [
                e
                for e in entries
                if e.updated_at > datetime.utcnow() - timedelta(hours=24)
            ]
        ),
        "constitutional_compliance": workspace.constitutional_compliance,
    }


@app.get("/api/v1/knowledge-graph/{workspace_id}")
async def get_knowledge_graph(workspace_id: str):
    """Get knowledge graph for workspace"""
    if workspace_id not in blackboard_storage["workspaces"]:
        raise HTTPException(status_code=404, detail="Workspace not found")

    entries = [
        entry
        for entry in blackboard_storage["entries"].values()
        if entry.workspace_id == workspace_id and entry.status == "active"
    ]

    # Build simple knowledge graph
    nodes = []
    edges = []

    for entry in entries:
        nodes.append(
            {
                "id": entry.entry_id,
                "label": entry.title,
                "type": entry.entry_type,
                "author": entry.author_id,
                "tags": entry.tags,
                "priority": entry.priority,
            }
        )

        # Add edges for dependencies
        for dep_id in entry.dependencies:
            if dep_id in [e.entry_id for e in entries]:
                edges.append(
                    {"source": dep_id, "target": entry.entry_id, "type": "dependency"}
                )

        # Add edges for tag relationships
        for other_entry in entries:
            if other_entry.entry_id != entry.entry_id:
                common_tags = set(entry.tags) & set(other_entry.tags)
                if common_tags:
                    edges.append(
                        {
                            "source": entry.entry_id,
                            "target": other_entry.entry_id,
                            "type": "related",
                            "strength": len(common_tags),
                        }
                    )

    return {
        "workspace_id": workspace_id,
        "nodes": nodes,
        "edges": edges,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


async def notify_subscribers(entry: BlackboardEntry, action: str):
    """Notify subscribers of entry changes"""
    # Find relevant subscriptions
    relevant_subscriptions = []

    for subscription in blackboard_storage["subscriptions"].values():
        if not subscription.active or action not in subscription.notification_types:
            continue

        if (
            subscription.target_type == "workspace"
            and subscription.target_id == entry.workspace_id
        ):
            relevant_subscriptions.append(subscription)
        elif (
            subscription.target_type == "entry"
            and subscription.target_id == entry.entry_id
        ):
            relevant_subscriptions.append(subscription)
        elif subscription.target_type == "tag":
            if subscription.target_id in entry.tags:
                relevant_subscriptions.append(subscription)

    # Create notifications
    for subscription in relevant_subscriptions:
        notification = Notification(
            recipient_id=subscription.subscriber_id,
            notification_type=f"entry_{action}",
            title=f"Entry {action}: {entry.title}",
            content={
                "entry_id": entry.entry_id,
                "workspace_id": entry.workspace_id,
                "action": action,
                "author_id": entry.author_id,
                "entry_type": entry.entry_type,
                "tags": entry.tags,
            },
            priority="normal" if entry.priority <= 5 else "high",
        )

        blackboard_storage["notifications"][notification.notification_id] = notification


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8010))
    uvicorn.run(app, host="0.0.0.0", port=port)
