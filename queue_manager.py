#!/usr/bin/env python3
"""
PID-based queue lock manager for dispatcher
Replaces signal-based locking with file-based locks
"""

import os
import json
import time
import fcntl
from pathlib import Path

QUEUE_DIR = Path.home() / ".jarvis" / "dispatcher_queue"
LOCK_FILE = QUEUE_DIR / ".lock"
QUEUE_FILE = QUEUE_DIR / "queue.json"

def acquire_lock(timeout=30):
    """Acquire lock using PID file"""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = LOCK_FILE
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            # Try to create lock file with exclusive flag
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            with os.fdopen(fd, 'w') as f:
                f.write(str(os.getpid()))
            return True
        except FileExistsError:
            # Check if PID in lock file is still alive
            try:
                with open(lock_path) as f:
                    locked_pid = int(f.read().strip())
                os.kill(locked_pid, 0)  # Signal 0 to check if alive
            except (ValueError, ProcessLookupError):
                # PID not found, stale lock - remove it
                lock_path.unlink()
                continue
            time.sleep(0.1)
    
    return False

def release_lock():
    """Release lock by removing PID file"""
    LOCK_FILE.unlink(missing_ok=True)

def enqueue(task):
    """Add task to queue"""
    if not acquire_lock():
        raise RuntimeError("Could not acquire queue lock")
    
    try:
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE) as f:
                queue = json.load(f)
        else:
            queue = []
        
        queue.append({
            'task': task,
            'timestamp': time.time(),
            'status': 'pending'
        })
        
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2)
    finally:
        release_lock()

def drain_queue():
    """Process all pending tasks in queue"""
    if not acquire_lock():
        raise RuntimeError("Could not acquire queue lock")
    
    try:
        if not QUEUE_FILE.exists():
            return 0
        
        with open(QUEUE_FILE) as f:
            queue = json.load(f)
        
        processed = 0
        for item in queue:
            if item['status'] == 'pending':
                # Process task here
                item['status'] = 'completed'
                processed += 1
        
        with open(QUEUE_FILE, 'w') as f:
            json.dump(queue, f, indent=2)
        
        return processed
    finally:
        release_lock()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        enqueue(' '.join(sys.argv[1:]))
        print(f"Enqueued: {' '.join(sys.argv[1:])}")
    else:
        count = drain_queue()
        print(f"Processed {count} tasks")
