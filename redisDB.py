import redis
import json
import configparser

conn = None

def initlize_connection():
    global conn
    config = configparser.ConfigParser()
    config.read('config.ini')
    conn = redis.StrictRedis(host=config['database']['redis_ip'],
                             port=config['database']['redis_port'],
                             password=config['database']['redis_passwd'],
                             db=0)

'''
  Paramas: product -> current product being checked.
  Description: Searches for products within the cache,
  if not found then it is added to the cache.
'''
def check_product(productId):
    global conn
    if conn.exists(productId):
        return conn.get(productId)

    return None

'''
  NAME: load_productId
  PARAMS: new_product -> product being added into the redis cache
          productId = id of the product being cached, used as the key.
  DESC: Loads product data into the redis cache if it is not already
  within the DB.
'''
def load_product(new_product, productId):
    global conn
    #using json in order to keep data standardized and avoid nasty lookup situations.
    val = json.dumps(new_product)
    conn.set(productId, val)

'''
 When json is stored within the redis cache, we need to deserialize
 data back into a json object when using the data.
'''
def deserialize_json(json_string):
    return json.loads(json_string)
