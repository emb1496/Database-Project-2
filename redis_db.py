import json
import configparser
import redis

CONN = None

'''
  NAME: initlize_connection
  PARAMS: None
  DESC: connects to our redis instance and the first database.
'''
def initlize_connection():
    global CONN
    config = configparser.ConfigParser()
    config.read('config.ini')
    CONN = redis.StrictRedis(host=config['database']['redis_ip'],
                             port=config['database']['redis_port'],
                             password=config['database']['redis_passwd'],
                             db=0)

'''
  NAME: check_product
  PARAMS: product -> current product being checked.
  DESC: Searches for products within the cache,
  if not found then it is added to the cache.
'''
def check_product(product_id):
    global CONN
    if CONN.exists(product_id):
        return CONN.get(product_id)

    return None

'''
  NAME: load_productId
  PARAMS: new_product -> product being added into the redis cache
          productId = id of the product being cached, used as the key.
  DESC: Loads product data into the redis cache if it is not already
  within the DB.
'''
def load_product(new_product, product_id):
    global CONN

    #using json in order to keep data standardized and avoid nasty lookup situations.
    val = json.dumps(new_product)
    CONN.set(product_id, val)

'''
  NAME: delete_product_cache
  PARAMS: product_id -> id of the product being deleted
  DESC: deletes the given cached data with the given key.
'''
def delete_product_cache(product_id):
    global CONN
    CONN.delete(product_id)

'''
 NAME: deserialize_json
 PARAMS: None
 DESC: When json is stored within the redis cache, we need to deserialize
 data back into a json object when using the data.
'''
def deserialize_json(json_string):
    return json.loads(json_string.decode('utf-8'))
