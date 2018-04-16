import redis
import json

conn = None

def initlize_connection():
    global conn
    conn = redis.StrictRedis(host='localhost', port=6379, db=0)

'''
  Searches for products within the cache,
  if not found then it is added to the cache.
'''
def get_product(product):
    global conn
    if conn.exists(product['id']):
        return conn.get(product['id'])

    return None

'''
  Loads product data into the redis cache if it is not already
  within the DB.
'''
def load_product(productName, productId, numSales, price, date):
    global conn
    name = productName
    numSales = numSales
    product_price = price
    recent_order_date = date

    order = {
        "productName" : name,
        "numSales" : numSales,
        "price" : product_price,
        "recentDate" : recent_order_date
    }
    #using json in order to keep data standardized.
    val = json.dumps(order)
    conn.set(productId,val)

initlize_connection()

load_product("pop", 1, 2, 200, "asdasdasd")
