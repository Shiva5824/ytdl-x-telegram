import redis
import json
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
r = redis.Redis.from_url(REDIS_URL)

def enqueue_download(task_id, data):
    r.set(task_id, json.dumps(data))
    r.rpush("ytdl_queue", task_id)

def dequeue_download():
    task_id = r.lpop("ytdl_queue")
    if task_id:
        raw = r.get(task_id)
        if raw:
            r.delete(task_id)
            return json.loads(raw)
    return None