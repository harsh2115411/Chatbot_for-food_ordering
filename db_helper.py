import mysql.connector
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="hp81719838",  # Note: Consider using environment variables for credentials
    database="pandeyji_eatery"
)

def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))
        cnx.commit()
        cursor.close()
        logger.debug(f"Order item inserted successfully: {food_item}, {quantity}, {order_id}")
        return 1

    except mysql.connector.Error as err:
        logger.error(f"MySQL Error inserting order item: {err}")
        cnx.rollback()
        return -1

    except Exception as e:
        logger.error(f"Unexpected error inserting order item: {e}")
        cnx.rollback()
        return -1

def insert_order_tracking(order_id, status):
    try:
        cursor = cnx.cursor()
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
        cursor.close()
        logger.debug(f"Order tracking inserted successfully: {order_id}, {status}")
    except Exception as e:
        logger.error(f"Error inserting order tracking: {e}")
        cnx.rollback()
        raise

def get_total_order_price(order_id):
    try:
        cursor = cnx.cursor()
        query = f"SELECT get_total_order_price({order_id})"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        cursor.close()
        return result
    except Exception as e:
        logger.error(f"Error getting total order price: {e}")
        return None

def get_next_order_id():
    try:
        cursor = cnx.cursor()
        query = "SELECT MAX(order_id) FROM orders"
        cursor.execute(query)
        result = cursor.fetchone()[0]
        cursor.close()
        return 1 if result is None else result + 1
    except Exception as e:
        logger.error(f"Error getting next order ID: {e}")
        return None

def get_order_status(order_id):
    try:
        cursor = cnx.cursor()
        query = "SELECT status FROM order_tracking WHERE order_id = %s"  # Using parameterized query
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        return None

if __name__ == "__main__":
    print(get_next_order_id())