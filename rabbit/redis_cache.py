import redis
import time 
import json 

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def get_user_from_db(user_id):
    time.sleep(2)
    return {"name":"Mehrshad","age":23,"user_id":user_id}


def get_user(user_id):
    cache_key = f"user:{user_id}"

    cached = r.get(cache_key)
    if cached:
        print("✅ Cache HIT")
        return json.loads(cached)
    
    print("❌ Cache MISS — hitting DB")
    user = get_user_from_db(user_id)

    r.setex(cache_key, 60, json.dumps(user))

    return user


print(get_user(1)) 
print(get_user(1000)) 

