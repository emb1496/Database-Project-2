import redis
import json

conn = None

def initlize_connection():
    global conn
    conn = redis.StrictRedis(host='localhost', port=6379, db=0)

'''
  Paramas: product -> current product being checked.
  Description: Searches for products within the cache,
  if not found then it is added to the cache.
'''
def check_product(product):
    global conn
    if conn.exists(product['id']):
        return conn.get(product['id'])

    return None

'''
  Loads product data into the redis cache if it is not already
  within the DB.
'''
def load_product(new_product, productId):
    global conn
    #using json in order to keep data standardized and avoid nasty lookup situations.
    val = json.dumps(new_product)
    conn.set(productId, val)

def deserialize_json(json_string):
    return json.loads(json_string)
