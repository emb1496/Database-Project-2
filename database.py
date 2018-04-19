#Elliott Barinberg, Joshua Long, Brendan Brence
import pymongo
from pymongo import MongoClient
import configparser
from bson import ObjectId
#abstraction for redis functionality
from .redisDB import *

products = None
customers = None
orders = None

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
	allCustomers = customers.find({})
	for customer in allCustomers:
		customer['id'] = str(customer['_id'])
		yield customer

def get_customer(id):
	customer = customers.find_one({'_id':ObjectId(id)})
	return customer

def upsert_customer(customer):
	if 'id' not in customer.keys():
		customers.insert_one(customer)
	else:
		customers.update_one({'_id':ObjectId(customer['id'])}, {'$set':{'firstName':customer['firstName'],'lastName':customer['lastName'],'street':customer['street'],'city':customer['city'],'state':customer['state'],'zip':customer['zip']}})

def delete_customer(id):
	customers.delete_one({'_id':ObjectId(id)})
    
def get_products():
	allProducts = products.find({})
	for product in allProducts:
		product['id'] = str(product['_id'])
		yield product

def get_product(id):
	product = products.find_one({'_id':ObjectId(id)})
	return product

def upsert_product(product):
	if 'id' not in product.keys():
		products.insert_one(product)
	else:
		products.update_one({'_id':ObjectId(product['id'])}, {'$set':{'name':product['name'],'price':product['price']}})

def delete_product(id):
	products.delete_one({'_id':ObjectId(id)})

def get_orders():
    allOrders = orders.find({})
    for order in allOrders:
        customer = get_customer(order['customerId'])
        order['customer'] = dict()
        order['customer']['firstName'] = customer['firstName']
        order['customer']['lastName'] = customer['lastName']

        product = get_product(order['productId'])
        if product != None:
            order['product'] = dict()
            order['product']['name'] = product['name']
            order['id'] = str(order['_id'])

            yield order

def get_order(id):
	order = orders.find_one({'_id':ObjectId(id)})
	return order

def _get_order_productId(productId):
    product_orders = orders.find({'productId': productId})
    for order in product_orders:
        yield order

def upsert_order(order):
    orders.insert_one(order)
    cached_product_orders = check_product(order['productId'])
    if cached_product_orders != None:
        delete_product_cache(order['productId'])

def delete_order(id):
	orders.delete_one({'_id':ObjectId(id)})
    
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
        cached_product_data = check_product(product['id'])
        # add checking for new data to update the cache
        if cached_product_data == None:
            product_orders = _get_order_productId(product['id']) 
            orders = sorted(product_orders, key=lambda k: k['date'])
            product_order = dict()
            product_order['name'] = product['name']
            product_order['last_order_date'] = orders[-1]['date']
            product_order['total_sales'] = len(orders)
            product_order['gross_revenue'] = product['price'] * product_order['total_sales']

            load_product(product_order,product['id'])

            yield product_order

        else:
            yield deserialize_json(cached_product_data)

