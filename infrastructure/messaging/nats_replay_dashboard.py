#!/usr/bin/env python3
"""
ACGS NATS Event Replay Dashboard
Web interface for managing NATS event persistence, replay, and recovery operations.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from nats_persistence_manager import persistence_manager, ReplayConfiguration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# FastAPI app
app = FastAPI(
    title="ACGS NATS Event Replay Dashboard",
    description="Dashboard for managing NATS event persistence and replay",
    version="1.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    """Initialize NATS persistence manager on startup."""
    try:
        await persistence_manager.start()
        logger.info("NATS Persistence Manager started")
    except Exception as e:
        logger.error(f"Failed to start NATS Persistence Manager: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        await persistence_manager.stop()
        logger.info("NATS Persistence Manager stopped")
    except Exception as e:
        logger.error(f"Error stopping NATS Persistence Manager: {e}")

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page."""
    try:
        # Get system status
        persistence_summary = persistence_manager.get_persistence_summary()
        
        # Get stream information
        streams_info = {}
        for stream_name in persistence_manager.stream_configs.keys():
            streams_info[stream_name] = await persistence_manager.get_stream_info(stream_name)
        
        return templates.TemplateResponse("nats_dashboard.html", {
            "request": request,
            "persistence_summary": persistence_summary,
            "streams_info": streams_info,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return HTMLResponse(f"<h1>Dashboard Error</h1><p>{str(e)}</p>", status_code=500)

@app.get("/api/streams")
async def get_streams():
    """Get information about all streams."""
    try:
        streams_info = {}
        for stream_name in persistence_manager.stream_configs.keys():
            streams_info[stream_name] = await persistence_manager.get_stream_info(stream_name)
        
        return {
            "streams": streams_info,
            "total_streams": len(streams_info),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting streams: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/streams/{stream_name}")
async def get_stream_info(stream_name: str):
    """Get detailed information about a specific stream."""
    try:
        if stream_name not in persistence_manager.stream_configs:
            raise HTTPException(status_code=404, detail=f"Stream {stream_name} not found")
        
        stream_info = await persistence_manager.get_stream_info(stream_name)
        
        return {
            "stream_info": stream_info,
            "stream_config": {
                "name": persistence_manager.stream_configs[stream_name].name,
                "subjects": persistence_manager.stream_configs[stream_name].subjects,
                "retention": persistence_manager.stream_configs[stream_name].retention.value,
                "max_age_days": persistence_manager.stream_configs[stream_name].max_age.days,
                "max_bytes": persistence_manager.stream_configs[stream_name].max_bytes,
                "max_msgs": persistence_manager.stream_configs[stream_name].max_msgs
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        logger.error(f"Error getting stream info for {stream_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/replay/start")
async def start_replay(
    stream_name: str = Form(...),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None),
    start_sequence: Optional[int] = Form(None),
    end_sequence: Optional[int] = Form(None),
    replay_speed: float = Form(1.0),
    filter_subjects: Optional[str] = Form(None),
    replay_to_original: bool = Form(True)
):
    """Start a new event replay."""
    try:
        if stream_name not in persistence_manager.stream_configs:
            raise HTTPException(status_code=404, detail=f"Stream {stream_name} not found")
        
        # Parse filter subjects
        filter_subjects_list = []
        if filter_subjects:
            filter_subjects_list = [s.strip() for s in filter_subjects.split(",") if s.strip()]
        
        # Create replay configuration
        replay_config = ReplayConfiguration(
            replay_id=f"replay_{int(datetime.now().timestamp())}_{stream_name}",
            stream_name=stream_name,
            start_time=datetime.fromisoformat(start_time) if start_time else None,
            end_time=datetime.fromisoformat(end_time) if end_time else None,
            start_sequence=start_sequence,
            end_sequence=end_sequence,
            replay_speed=replay_speed,
            filter_subjects=filter_subjects_list,
            replay_to_original_subjects=replay_to_original
        )
        
        # Start replay
        replay_id = await persistence_manager.start_replay(replay_config)
        
        return {
            "replay_id": replay_id,
            "message": f"Replay started successfully",
            "replay_config": {
                "stream_name": stream_name,
                "start_time": start_time,
                "end_time": end_time,
                "replay_speed": replay_speed,
                "filter_subjects": filter_subjects_list
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        logger.error(f"Error starting replay: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/replay/{replay_id}/stop")
async def stop_replay(replay_id: str):
    """Stop an active replay."""
    try:
        await persistence_manager.stop_replay(replay_id)
        
        return {
            "message": f"Replay {replay_id} stopped successfully",
            "replay_id": replay_id,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        logger.error(f"Error stopping replay {replay_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/replays")
async def get_active_replays():
    """Get information about active replays."""
    try:
        active_replays = {}
        for replay_id, config in persistence_manager.active_replays.items():
            active_replays[replay_id] = {
                "replay_id": config.replay_id,
                "stream_name": config.stream_name,
                "start_time": config.start_time.isoformat() if config.start_time else None,
                "end_time": config.end_time.isoformat() if config.end_time else None,
                "replay_speed": config.replay_speed,
                "filter_subjects": config.filter_subjects,
                "constitutional_hash": config.constitutional_hash
            }
        
        return {
            "active_replays": active_replays,
            "total_active": len(active_replays),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting active replays: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streams/{stream_name}/backup")
async def backup_stream(stream_name: str, backup_path: Optional[str] = None):
    """Backup a stream to file."""
    try:
        if stream_name not in persistence_manager.stream_configs:
            raise HTTPException(status_code=404, detail=f"Stream {stream_name} not found")
        
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/nats/{stream_name}_backup_{timestamp}.jsonl"
        
        await persistence_manager.backup_stream(stream_name, backup_path)
        
        return {
            "message": f"Stream {stream_name} backed up successfully",
            "backup_path": backup_path,
            "stream_name": stream_name,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        logger.error(f"Error backing up stream {stream_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/streams/{stream_name}/restore")
async def restore_stream(stream_name: str, backup_path: str = Form(...)):
    """Restore a stream from backup file."""
    try:
        if stream_name not in persistence_manager.stream_configs:
            raise HTTPException(status_code=404, detail=f"Stream {stream_name} not found")
        
        await persistence_manager.restore_stream(stream_name, backup_path)
        
        return {
            "message": f"Stream {stream_name} restored successfully",
            "backup_path": backup_path,
            "stream_name": stream_name,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        logger.error(f"Error restoring stream {stream_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/publish")
async def publish_test_event(
    subject: str = "acgs.events.test",
    event_type: str = "test_event",
    source_service: str = "dashboard"
):
    """Publish a test event for testing purposes."""
    try:
        test_data = {
            "message": "Test event from dashboard",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test_id": f"test_{int(datetime.now().timestamp())}"
        }
        
        event_metadata = await persistence_manager.publish_event(
            subject=subject,
            event_data=test_data,
            event_type=event_type,
            source_service=source_service
        )
        
        return {
            "message": "Test event published successfully",
            "event_metadata": {
                "event_id": event_metadata.event_id,
                "subject": event_metadata.subject,
                "event_type": event_metadata.event_type,
                "stream_name": event_metadata.stream_name,
                "sequence_number": event_metadata.sequence_number
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    except Exception as e:
        logger.error(f"Error publishing test event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_system_status():
    """Get system status and health information."""
    try:
        persistence_summary = persistence_manager.get_persistence_summary()
        
        # Get stream statistics
        total_messages = 0
        total_bytes = 0
        
        for stream_name in persistence_manager.stream_configs.keys():
            try:
                stream_info = await persistence_manager.get_stream_info(stream_name)
                total_messages += stream_info.get("messages", 0)
                total_bytes += stream_info.get("bytes", 0)
            except:
                pass
        
        return {
            "system_status": {
                "connected": persistence_summary["connected"],
                "active_replays": persistence_summary["active_replays"],
                "configured_streams": persistence_summary["configured_streams"],
                "total_messages": total_messages,
                "total_bytes": total_bytes,
                "constitutional_hash": persistence_summary["constitutional_hash"]
            },
            "health": "healthy" if persistence_summary["connected"] else "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "acgs-nats-replay-dashboard",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Create dashboard template
dashboard_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACGS NATS Event Replay Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background-color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin: 10px; padding: 15px; background-color: #ecf0f1; border-radius: 5px; min-width: 150px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { font-size: 14px; color: #7f8c8d; }
        .stream-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .stream-card { background-color: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 15px; }
        .status-connected { color: #27ae60; }
        .status-disconnected { color: #e74c3c; }
        .constitutional-hash { font-family: monospace; background-color: #f8f9fa; padding: 5px; border-radius: 3px; }
        button { background-color: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background-color: #2980b9; }
        .form-group { margin: 10px 0; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .replay-form { background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ACGS NATS Event Replay Dashboard</h1>
        <p>Constitutional Hash: <span class="constitutional-hash">{{ constitutional_hash }}</span></p>
        <p>Last Updated: {{ timestamp }}</p>
    </div>

    <div class="card">
        <h2>System Status</h2>
        <div class="metric">
            <div class="metric-value status-{{ 'connected' if persistence_summary.connected else 'disconnected' }}">
                {{ 'Connected' if persistence_summary.connected else 'Disconnected' }}
            </div>
            <div class="metric-label">NATS Connection</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ persistence_summary.active_replays }}</div>
            <div class="metric-label">Active Replays</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ persistence_summary.configured_streams }}</div>
            <div class="metric-label">Configured Streams</div>
        </div>
    </div>

    <div class="card">
        <h2>Streams Overview</h2>
        <div class="stream-grid" id="streams-grid">
            {% for stream_name, stream_info in streams_info.items() %}
            <div class="stream-card">
                <h3>{{ stream_name }}</h3>
                <p><strong>Messages:</strong> {{ stream_info.get('messages', 'N/A') }}</p>
                <p><strong>Size:</strong> {{ (stream_info.get('bytes', 0) / 1024 / 1024) | round(2) }} MB</p>
                <p><strong>Subjects:</strong> {{ stream_info.get('subjects', []) | join(', ') }}</p>
                <button onclick="backupStream('{{ stream_name }}')">Backup</button>
                <button onclick="showReplayForm('{{ stream_name }}')">Start Replay</button>
            </div>
            {% endfor %}
        </div>
    </div>

    <div class="card">
        <h2>Event Replay</h2>
        <div class="replay-form" id="replay-form" style="display: none;">
            <h3>Start Event Replay</h3>
            <form id="replay-config-form">
                <div class="form-group">
                    <label for="stream-select">Stream:</label>
                    <select id="stream-select" name="stream_name" required>
                        {% for stream_name in streams_info.keys() %}
                        <option value="{{ stream_name }}">{{ stream_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label for="start-time">Start Time (ISO format):</label>
                    <input type="datetime-local" id="start-time" name="start_time">
                </div>
                <div class="form-group">
                    <label for="end-time">End Time (ISO format):</label>
                    <input type="datetime-local" id="end-time" name="end_time">
                </div>
                <div class="form-group">
                    <label for="replay-speed">Replay Speed:</label>
                    <input type="number" id="replay-speed" name="replay_speed" value="1.0" step="0.1" min="0.1" max="10">
                </div>
                <div class="form-group">
                    <label for="filter-subjects">Filter Subjects (comma-separated):</label>
                    <input type="text" id="filter-subjects" name="filter_subjects" placeholder="acgs.events.test,acgs.evolution.submit">
                </div>
                <button type="submit">Start Replay</button>
                <button type="button" onclick="hideReplayForm()">Cancel</button>
            </form>
        </div>
    </div>

    <div class="card">
        <h2>Active Replays</h2>
        <div id="active-replays">
            <!-- Active replays will be loaded here -->
        </div>
    </div>

    <div class="card">
        <h2>Actions</h2>
        <button onclick="publishTestEvent()">Publish Test Event</button>
        <button onclick="refreshData()">Refresh Data</button>
        <button onclick="loadActiveReplays()">Refresh Replays</button>
    </div>

    <script>
        function showReplayForm(streamName) {
            document.getElementById('stream-select').value = streamName;
            document.getElementById('replay-form').style.display = 'block';
        }

        function hideReplayForm() {
            document.getElementById('replay-form').style.display = 'none';
        }

        async function backupStream(streamName) {
            try {
                const response = await fetch(`/api/streams/${streamName}/backup`, {
                    method: 'POST'
                });
                const data = await response.json();
                alert(`Backup started for ${streamName}: ${data.backup_path}`);
            } catch (error) {
                alert('Error starting backup: ' + error.message);
            }
        }

        async function publishTestEvent() {
            try {
                const response = await fetch('/api/events/publish');
                const data = await response.json();
                alert('Test event published: ' + data.event_metadata.event_id);
            } catch (error) {
                alert('Error publishing test event: ' + error.message);
            }
        }

        async function loadActiveReplays() {
            try {
                const response = await fetch('/api/replays');
                const data = await response.json();
                
                const container = document.getElementById('active-replays');
                container.innerHTML = '';
                
                if (Object.keys(data.active_replays).length === 0) {
                    container.innerHTML = '<p>No active replays</p>';
                    return;
                }
                
                for (const [replayId, replay] of Object.entries(data.active_replays)) {
                    const replayDiv = document.createElement('div');
                    replayDiv.className = 'stream-card';
                    replayDiv.innerHTML = `
                        <h4>${replayId}</h4>
                        <p><strong>Stream:</strong> ${replay.stream_name}</p>
                        <p><strong>Speed:</strong> ${replay.replay_speed}x</p>
                        <p><strong>Start Time:</strong> ${replay.start_time || 'N/A'}</p>
                        <button onclick="stopReplay('${replayId}')">Stop Replay</button>
                    `;
                    container.appendChild(replayDiv);
                }
            } catch (error) {
                console.error('Error loading active replays:', error);
            }
        }

        async function stopReplay(replayId) {
            try {
                const response = await fetch(`/api/replay/${replayId}/stop`, {
                    method: 'POST'
                });
                const data = await response.json();
                alert(`Replay ${replayId} stopped`);
                loadActiveReplays();
            } catch (error) {
                alert('Error stopping replay: ' + error.message);
            }
        }

        document.getElementById('replay-config-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/api/replay/start', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                alert(`Replay started: ${data.replay_id}`);
                hideReplayForm();
                loadActiveReplays();
            } catch (error) {
                alert('Error starting replay: ' + error.message);
            }
        });

        function refreshData() {
            location.reload();
        }

        // Load active replays on page load
        loadActiveReplays();
        
        // Refresh active replays every 30 seconds
        setInterval(loadActiveReplays, 30000);
    </script>
</body>
</html>
"""

def create_dashboard_template():
    """Create dashboard template file."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    template_file = templates_dir / "nats_dashboard.html"
    with open(template_file, 'w') as f:
        f.write(dashboard_template)

if __name__ == "__main__":
    # Create template
    create_dashboard_template()
    
    # Start dashboard server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8098,
        log_level="info"
    )
