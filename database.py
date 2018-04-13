import pymongo
from pymongo import MongoClient
import configparser
################################################################################
#  REMOVE THESE LISTS, THEY ARE HERE AS MOCK DATA ONLY.
customers = list()
customers.append({'id': 0, 'firstName': "Kasandra", 'lastName': "Cryer", 'street':"884 Meadow Lane", 'city':"Bardstown", 'state':"KY", 'zip':  "4004"})
customers.append({'id': 1, 'firstName': "Ferne", 'lastName': "Linebarger", 'street':"172 Academy Street", 'city':"Morton Grove", 'state':"IL", 'zip':  "60053"})
customers.append({'id': 2, 'firstName': "Britany", 'lastName': "Manges", 'street':"144 Fawn Court", 'city':"Antioch", 'state':"TN", 'zip':  "37013"})

products = list()
products.append({'id':0, 'name': "Product A", 'price': 5})
products.append({'id':1, 'name': "Product B", 'price': 10})
products.append({'id':2, 'name': "Product C", 'price': 2.5})

orders = list()
orders.append({'id':0, 'customerId': 0, 'productId':0, 'date':"2017-04-12"})
orders.append({'id':1, 'customerId': 2, 'productId':1, 'date':"2015-08-13"})
orders.append({'id':2, 'customerId': 0, 'productId':2, 'date':"2019-10-18"})
orders.append({'id':3, 'customerId': 1, 'productId':0, 'date':"2011-03-30"})
orders.append({'id':4, 'customerId': 0, 'productId':1, 'date':"2017-09-01"})
orders.append({'id':5, 'customerId': 1, 'productId':2, 'date':"2017-12-17"})

#products = None
#customers = None
#orders = None
    

################################################################################
# The following three functions are only for mocking data - they should be removed,
def _find_by_id(things, id):
    results = [thing for thing in things if thing['id'] == id]
    if ( len(results) > 0 ): 
        return results[0]
    else:
        return None

def _upsert_by_id(things, thing):
    if 'id' in thing:
        index = [i for i, c in enumerate(things) if c['id'] == thing['id']]
        if ( len(index) > 0 ) :
            del things[index[0]]
            things.append(thing)
    else:
        thing['id'] = len(things)
        things.append(thing)

def _delete_by_id(things, id):
    index = [i for i, c in enumerate(things) if c['id'] == id]
    if ( len(index) > 0 ) :
        del things[index[0]]

def connect_to_db(conn_str):
    global products
    global customers
    global orders
    client = MongoClient(conn_str)
    products = client.cmps364.products
    customers = client.cmps364.customers
    orders = client.cmps364.orders
    return client

# The following functions are REQUIRED - you should REPLACE their implementation
# with the appropriate code to interact with your Mongo database.
def initialize():
	config = configparser.ConfigParser()
	config.read('config.ini')
	connection_string = config['database']['mongo_connection']
	conn = connect_to_db(connection_string)

    # this function will get called once, when the application starts.
    # this would be a good place to initalize your connection!
    # You might also want to connect to redis...

def get_customers():
    return customers

def get_customer(id):
    return _find_by_id(customers, id)

def upsert_customer(customer):
    _upsert_by_id(customers, customer)

def delete_customer(id):
    _delete_by_id(customers, id)
    
def get_products():
    return products

def get_product(id):
    return _find_by_id(products, id)

def upsert_product(product):
    _upsert_by_id(products, product)

def delete_product(id):
    _delete_by_id(products, id)

def get_orders():
    for order in orders:
        order['product'] = _find_by_id(products, order['productId'])
        order['customer'] = _find_by_id(customers, order['customerId'])
    return orders

def get_order(id):
    return _find_by_id(orders, id)

def upsert_order(order):
    _upsert_by_id(orders, order)

def delete_order(id):
    _delete_by_id(orders, id)

# Return the customer, with a list of orders.  Each order should have a product 
# property as well.
def customer_report(id):
    customer = _find_by_id(customers, id)
    orders = get_orders()
    customer['orders'] = [o for o in orders if o['customerId'] == id]
    return customer

# Pay close attention to what is being returned here.  Each product in the products
# list is a dictionary, that has all product attributes + last_order_date, total_sales, and 
# gross_revenue.  This is the function that needs to be use Redis as a cache.

# - When a product dictionary is computed, save it as a hash in Redis with the product's
#   ID as the key.  When preparing a product dictionary, before doing the computation, 
#   check if its already in redis!
def sales_report():
    products = get_products()
    for product in products:
        orders = [o for o in get_orders() if o['productId'] == product['id']] 
        orders = sorted(orders, key=lambda k: k['date']) 
        product['last_order_date'] = orders[-1]['date']
        product['total_sales'] = len(orders)
        product['gross_revenue'] = product['price'] * product['total_sales']
    return products
