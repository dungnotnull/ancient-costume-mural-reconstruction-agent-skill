"""
tools/hooks_system.py — Skill 240: ancient-costume-mural-reconstruction

Production-grade hooks system for lifecycle management, state synchronization,
and event emission.
"""
from __future__ import annotations

import json
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Configure logging
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "hooks_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class HookEvent:
    """Structured hook event."""
    event_type: str
    timestamp: str
    data: Dict[str, Any]
    source: str = "harness"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HookRegistration:
    """Hook registration information."""
    name: str
    event_type: str
    handler: Callable[[HookEvent], None]
    priority: int = 0
    once: bool = False
    enabled: bool = True


@dataclass
class StateSnapshot:
    """System state snapshot."""
    timestamp: str
    current_step: str
    degradation_level: int
    language: str
    requirements: Dict[str, Any]
    evidence_bundle: Dict[str, Any]
    reconstruction: Optional[Dict[str, Any]]
    verdict: Optional[Dict[str, Any]]


# ---------------------------------------------------------------------------
# Hooks Bus
# ---------------------------------------------------------------------------

class HooksBus:
    """Central event bus for hook system."""

    def __init__(self):
        self._hooks: Dict[str, List[HookRegistration]] = defaultdict(list)
        self._event_log: List[HookEvent] = []
        self._state: Optional[StateSnapshot] = None
        self._lock = threading.Lock()

    def register(
        self,
        name: str,
        event_type: str,
        handler: Callable[[HookEvent], None],
        priority: int = 0,
        once: bool = False,
        enabled: bool = True
    ) -> None:
        """Register a hook handler."""
        with self._lock:
            registration = HookRegistration(
                name=name,
                event_type=event_type,
                handler=handler,
                priority=priority,
                once=once,
                enabled=enabled
            )
            self._hooks[event_type].append(registration)
            # Sort by priority (higher priority first)
            self._hooks[event_type].sort(key=lambda r: r.priority, reverse=True)
            logger.info(f"Registered hook: {name} for event {event_type} (priority {priority})")

    def unregister(self, name: str, event_type: str) -> bool:
        """Unregister a hook handler."""
        with self._lock:
            hooks = self._hooks.get(event_type, [])
            original_count = len(hooks)
            self._hooks[event_type] = [h for h in hooks if h.name != name]
            removed = original_count - len(self._hooks[event_type])
            if removed > 0:
                logger.info(f"Unregistered hook: {name} from event {event_type}")
            return removed > 0

    def emit(self, event: HookEvent) -> None:
        """Emit an event to all registered handlers."""
        with self._lock:
            self._event_log.append(event)

        handlers = self._hooks.get(event.event_type, [])
        if not handlers:
            logger.debug(f"No handlers registered for event: {event.event_type}")
            return

        logger.info(f"Emitting event: {event.event_type} to {len(handlers)} handlers")

        for registration in handlers:
            if not registration.enabled:
                continue

            try:
                registration.handler(event)
                if registration.once:
                    # Mark for removal after emission
                    registration.enabled = False
            except Exception as e:
                logger.error(f"Hook {registration.name} failed: {e}")

        # Clean up once-only hooks
        if registration.once:
            with self._lock:
                self._hooks[event.event_type] = [h for h in handlers if not (h.once and not h.enabled)]

    def get_event_log(self, event_type: Optional[str] = None, limit: int = 100) -> List[HookEvent]:
        """Get event log, optionally filtered by type."""
        with self._lock:
            if event_type:
                events = [e for e in self._event_log if e.event_type == event_type]
            else:
                events = self._event_log[-limit:]
            return events

    def clear_event_log(self) -> None:
        """Clear the event log."""
        with self._lock:
            self._event_log.clear()
            logger.info("Event log cleared")

    def get_state(self) -> Optional[StateSnapshot]:
        """Get current system state."""
        return self._state

    def update_state(self, **kwargs) -> None:
        """Update system state."""
        with self._lock:
            if self._state is None:
                self._state = StateSnapshot(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    current_step="",
                    degradation_level=0,
                    language="en",
                    requirements={},
                    evidence_bundle={},
                    reconstruction=None,
                    verdict=None
                )
            for key, value in kwargs.items():
                if hasattr(self._state, key):
                    setattr(self._state, key, value)
            self._state.timestamp = datetime.now(timezone.utc).isoformat()


# Global hooks bus instance
_hooks_bus = HooksBus()


def get_hooks_bus() -> HooksBus:
    """Get the global hooks bus instance."""
    return _hooks_bus


# ---------------------------------------------------------------------------
# Built-in Hook Handlers
# ---------------------------------------------------------------------------

def log_to_file_handler(event: HookEvent) -> None:
    """Log events to structured log file."""
    log_entry = {
        "timestamp": event.timestamp,
        "event_type": event.event_type,
        "data": event.data
    }
    log_file = LOG_DIR / f"hooks_{event.event_type}.log"

    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to hook log: {e}")


def metrics_handler(event: HookEvent) -> None:
    """Collect metrics from events."""
    metrics_file = LOG_DIR / "metrics.jsonl"

    try:
        metric = {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "duration_ms": event.data.get("duration_ms", 0),
            "step": event.data.get("step", ""),
            "tokens": event.data.get("tokens", 0)
        }
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metric) + "\n")
    except Exception as e:
        logger.error(f"Failed to write metrics: {e}")


def state_sync_handler(event: HookEvent) -> None:
    """Synchronize state on step completion."""
    if event.event_type == "step_complete":
        bus = get_hooks_bus()
        bus.update_state(
            current_step=event.data.get("skill_name", ""),
            **event.data.get("outputs", {})
        )


def degradation_alert_handler(event: HookEvent) -> None:
    """Send alert on degradation level increase."""
    if event.event_type == "degradation":
        old_level = event.data.get("old_level", 0)
        new_level = event.data.get("new_level", 0)

        if new_level >= 3:
            logger.warning(f"SEVERE DEGRADATION: Level {new_level}")
            # Could send external notification here
        elif new_level > old_level:
            logger.info(f"Degradation increased: {old_level} → {new_level}")


# ---------------------------------------------------------------------------
# Event Emission Helpers
# ---------------------------------------------------------------------------

def emit_routing_decision(
    requirements_summary: str,
    selected_chain: List[str],
    rationale: str,
    fallback_strategy: str,
    estimated_complexity: str
) -> Dict[str, Any]:
    """Emit routing decision event."""
    bus = get_hooks_bus()
    event = HookEvent(
        event_type="routing_decision",
        timestamp=datetime.now(timezone.utc).isoformat(),
        data={
            "requirements_summary": requirements_summary,
            "selected_chain": selected_chain,
            "rationale": rationale,
            "fallback_strategy": fallback_strategy,
            "estimated_complexity": estimated_complexity
        }
    )
    bus.emit(event)
    return {"status": "emitted", "event": event}


def emit_quality_gate_result(
    gate_id: str,
    passed: bool,
    payload: Dict[str, Any],
    auto_fix_applied: bool = False
) -> Dict[str, Any]:
    """Emit quality gate result event."""
    bus = get_hooks_bus()
    event = HookEvent(
        event_type="quality_gate_result",
        timestamp=datetime.now(timezone.utc).isoformat(),
        data={
            "gate_id": gate_id,
            "passed": passed,
            "payload_keys": list(payload.keys()) if payload else [],
            "auto_fix_applied": auto_fix_applied
        }
    )
    bus.emit(event)
    return {"status": "emitted", "event": event}


def emit_step_complete(
    skill_name: str,
    outputs: Dict[str, Any],
    duration_ms: int,
    success: bool = True
) -> Dict[str, Any]:
    """Emit step completion event."""
    bus = get_hooks_bus()
    event = HookEvent(
        event_type="step_complete",
        timestamp=datetime.now(timezone.utc).isoformat(),
        data={
            "skill_name": skill_name,
            "outputs_keys": list(outputs.keys()) if outputs else [],
            "duration_ms": duration_ms,
            "success": success
        }
    )
    bus.emit(event)
    return {"status": "emitted", "event": event}


def emit_degradation(
    old_level: int,
    new_level: int,
    reason: str
) -> Dict[str, Any]:
    """Emit degradation event."""
    bus = get_hooks_bus()
    event = HookEvent(
        event_type="degradation",
        timestamp=datetime.now(timezone.utc).isoformat(),
        data={
            "old_level": old_level,
            "new_level": new_level,
            "reason": reason
        }
    )
    bus.emit(event)
    return {"status": "emitted", "event": event}


def emit_analysis_complete(
    verdict: Dict[str, Any],
    total_duration_ms: int
) -> Dict[str, Any]:
    """Emit analysis complete event."""
    bus = get_hooks_bus()
    event = HookEvent(
        event_type="analysis_complete",
        timestamp=datetime.now(timezone.utc).isoformat(),
        data={
            "verdict": verdict.get("verdict", ""),
            "total_duration_ms": total_duration_ms,
            "confidence": verdict.get("confidence", "unknown")
        }
    )
    bus.emit(event)
    return {"status": "emitted", "event": event}


# ---------------------------------------------------------------------------
# Hooks System Initialization
# ---------------------------------------------------------------------------

def initialize_hooks_system() -> None:
    """Initialize the hooks system with built-in handlers."""
    bus = get_hooks_bus()

    # Register built-in handlers
    bus.register(
        name="log_to_file",
        event_type="*",
        handler=log_to_file_handler,
        priority=10
    )

    bus.register(
        name="metrics",
        event_type="*",
        handler=metrics_handler,
        priority=5
    )

    bus.register(
        name="state_sync",
        event_type="step_complete",
        handler=state_sync_handler,
        priority=20
    )

    bus.register(
        name="degradation_alert",
        event_type="degradation",
        handler=degradation_alert_handler,
        priority=30
    )

    logger.info("Hooks system initialized with built-in handlers")


# Auto-initialize on module import
initialize_hooks_system()


# ---------------------------------------------------------------------------
# Hooks Configuration (from JSON)
# ---------------------------------------------------------------------------

def load_hooks_config(config_path: Optional[Path] = None) -> None:
    """Load hooks configuration from JSON file."""
    if config_path is None:
        config_path = PROJECT_ROOT / "assets" / "hooks.json"

    if not config_path.exists():
        logger.info(f"No hooks configuration found at {config_path}")
        return

    try:
        with open(config_path) as f:
            config = json.load(f)

        bus = get_hooks_bus()

        for hook_config in config.get("hooks", []):
            # Load custom handler from module
            module_path = hook_config.get("handler")
            if module_path:
                # This would dynamically load the handler function
                # For now, just log that we'd load it
                logger.info(f"Would load custom hook: {hook_config['name']} from {module_path}")

        logger.info(f"Loaded hooks configuration from {config_path}")

    except Exception as e:
        logger.error(f"Failed to load hooks configuration: {e}")


# ---------------------------------------------------------------------------
# Main Entry Point (for testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Testing hooks system...")

    # Test event emission
    emit_routing_decision(
        requirements_summary="Test reconstruction",
        selected_chain=["sub-gather-requirements", "sub-evidence-collector"],
        rationale="Test routing",
        fallback_strategy="Test fallback",
        estimated_complexity="medium"
    )

    emit_quality_gate_result(
        gate_id="U1",
        passed=True,
        payload={"sources": [{"tier": "Tier 1"}]}
    )

    # Get event log
    bus = get_hooks_bus()
    events = bus.get_event_log()
    print(f"\nEvent log contains {len(events)} events")

    for event in events:
        print(f"  - {event.event_type}: {event.timestamp}")
