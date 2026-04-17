#!/usr/bin/env python3
"""
STC Dispatcher WatchPane -- Pure observability daemon.
Zero LLM cost. Tails DISPATCHER_QUEUE.md, polls FLEET_STATUS.md every 2min,
alerts on RED status. Appends heartbeat every 5min.

Designed to run in the VS Code bottom-right terminal pane.

Usage:
    python3 watchpane.py
"""

import os, time, sys, hashlib
from datetime import datetime

BASE = os.path.expanduser("~/Desktop/JARVIS_EMPIRE")
QUEUE_FILE = os.path.join(BASE, "DISPATCHER_QUEUE.md")
FLEET_FILE = os.path.join(BASE, "FLEET_STATUS.md")
HEARTBEAT_FILE = os.path.join(BASE, "dispatcher", "heartbeat.log")
POLL_INTERVAL = 30  # seconds between checks
FLEET_POLL_EVERY = 4  # every 4 cycles = 2 min
HEARTBEAT_EVERY = 10  # every 10 cycles = 5 min

COO_HANDSHAKE = "local_eebdb0ba"


def ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S CDT")


def log(msg, level="INFO"):
    line = f"[{ts()}] [{level}] {msg}"
    print(line, flush=True)
    return line


def file_hash(path):
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def tail_queue(last_hash):
    """Check if DISPATCHER_QUEUE.md changed, print new content."""
    current_hash = file_hash(QUEUE_FILE)
    if current_hash is None:
        return last_hash
    if current_hash != last_hash:
        log("DISPATCHER_QUEUE.md changed -- reading updates")
        try:
            with open(QUEUE_FILE, "r") as f:
                content = f.read()
            lines = content.strip().split("\n")
            recent = lines[-20:] if len(lines) > 20 else lines
            for line in recent:
                if line.strip():
                    print(f"  QUEUE: {line}", flush=True)
        except Exception as e:
            log(f"Error reading queue: {e}", "WARN")
    return current_hash


def poll_fleet():
    """Read FLEET_STATUS.md, alert on RED or FAIL items."""
    try:
        with open(FLEET_FILE, "r") as f:
            content = f.read()
    except FileNotFoundError:
        log("FLEET_STATUS.md not found", "WARN")
        return

    alerts = []
    for line in content.split("\n"):
        lower = line.lower()
        # Match "| RED |" or "| RED " as a status cell, not substrings like "credit" or "RESOLVED"
        if ("| red |" in lower or "| red " in lower) and "resolved" not in lower:
            alerts.append(f"RED ALERT: {line.strip()}")
        elif ("| fail" in lower or "| failed" in lower) and "|" in line:
            alerts.append(f"FAIL: {line.strip()}")

    if alerts:
        log(f"FLEET ALERTS ({len(alerts)}):", "ALERT")
        for a in alerts:
            print(f"  >> {a}", flush=True)
    else:
        log("FLEET: all systems nominal")


def write_heartbeat(cycle):
    """Append heartbeat to log file."""
    try:
        with open(HEARTBEAT_FILE, "a") as f:
            f.write(f"{ts()} | cycle={cycle} | handshake={COO_HANDSHAKE} | alive\n")
    except Exception as e:
        log(f"Heartbeat write failed: {e}", "WARN")


def main():
    print("=" * 60, flush=True)
    log("STC DISPATCHER WATCHPANE v1.0")
    log(f"COO Handshake: {COO_HANDSHAKE}")
    log(f"Queue: {QUEUE_FILE}")
    log(f"Fleet: {FLEET_FILE}")
    log(f"Poll: {POLL_INTERVAL}s | Fleet: {POLL_INTERVAL * FLEET_POLL_EVERY}s | Heartbeat: {POLL_INTERVAL * HEARTBEAT_EVERY}s")
    print("=" * 60, flush=True)

    queue_hash = file_hash(QUEUE_FILE)
    cycle = 0

    poll_fleet()
    write_heartbeat(cycle)

    while True:
        try:
            time.sleep(POLL_INTERVAL)
            cycle += 1

            queue_hash = tail_queue(queue_hash)

            if cycle % FLEET_POLL_EVERY == 0:
                poll_fleet()

            if cycle % HEARTBEAT_EVERY == 0:
                write_heartbeat(cycle)
                log(f"Heartbeat #{cycle // HEARTBEAT_EVERY} written")

        except KeyboardInterrupt:
            log("Dispatcher stopped by user", "STOP")
            sys.exit(0)
        except Exception as e:
            log(f"Cycle error: {e}", "ERROR")
            time.sleep(5)


if __name__ == "__main__":
    main()
