#!/usr/bin/env python3
"""Drain dispatcher queue and log sends"""
import json
import time
from pathlib import Path

QUEUE_DIR = Path.home() / ".jarvis" / "dispatcher_queue"
QUEUE_FILE = QUEUE_DIR / "queue.json"
LOG_FILE = Path.home() / ".jarvis" / "logs" / "operator_sends.log"

def log_send(task, status="SENT"):
    """Log task send"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {status}: {task}\n")

def drain():
    """Drain queue"""
    if not QUEUE_FILE.exists():
        log_send("Queue empty - no items to process", "INFO")
        return 0
    
    with open(QUEUE_FILE) as f:
        queue = json.load(f)
    
    count = 0
    for item in queue:
        if item['status'] == 'pending':
            task = item['task']
            log_send(task, "SENT")
            item['status'] = 'completed'
            count += 1
    
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)
    
    return count

if __name__ == '__main__':
    count = drain()
    print(f"Drained {count} items")
