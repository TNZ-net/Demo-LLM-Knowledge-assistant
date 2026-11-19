import os
import redis
from dotenv import load_dotenv

load_dotenv()
r = redis.Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
LIMIT = 5         
WINDOW = 60       

def allow(user_id: int, limit: int = LIMIT, window: int = WINDOW) -> bool:
    key = f"rate:user:{user_id}"
    try:
        count = r.incr(key)                
        if count == 1:
            r.expire(key, window)          
        return count <= limit
    except redis.RedisError as e:
        print("Redis unavailable, allowing request:", e)
        return True                     

if __name__ == "__main__":
    for i in range(1, 8):
        print(i, allow(999))