from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper
import logging
import traceback

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
inprogress_orders = {}

@app.post("/")
async def handle_request(request: Request):
    try:
        payload = await request.json()
        logger.debug(f"Received payload: {payload}")

        intent = payload['queryResult']['intent']['displayName']
        parameters = payload['queryResult']['parameters']
        output_contexts = payload['queryResult']['outputContexts']

        session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
        logger.debug(f"Extracted session ID: {session_id}")
        logger.debug(f"Processing intent: {intent}")

        # Corrected intent names
        intent_handler_dict = {
            'Order.add.context:ongoing-order': add_to_order,
            'order.remove.context-Ongoing-order': remove_from_order,
            'order.complete.context:ongoing-order': complete_order,
            'Track_order.context:ongoing-tacking': track_order
        }

        if intent not in intent_handler_dict:
            logger.warning(f"Unhandled intent: {intent}")
            return JSONResponse(content={
                "fulfillmentText": "I'm not sure how to handle that request. Could you please try again?"
            })

        # Call the appropriate handler
        handler_response = intent_handler_dict[intent](parameters, session_id)
        return handler_response

    except KeyError as e:
        logger.error(f"KeyError in payload: {str(e)}\nPayload: {payload if 'payload' in locals() else 'No payload'}")
        return JSONResponse(content={
            "fulfillmentText": "I'm having trouble understanding your request. Could you please try again?"
        })
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I encountered an error. Please try again later."
        })
def track_order(parameters: dict, session_id: str):
    try:
        # Extract `order_id` from parameters
        order_id = parameters.get("order_id")
        
        if not order_id:
            logger.debug("No order ID provided in parameters.")
            return JSONResponse(content={
                "fulfillmentText": "Could you please provide the order ID you'd like to track?"
            })

        try:
            order_id = int(order_id)
        except ValueError:
            logger.debug(f"Invalid order ID format: {order_id}")
            return JSONResponse(content={
                "fulfillmentText": "The order ID you provided seems incorrect. Please double-check and try again."
            })

        logger.debug(f"Tracking order with ID: {order_id}")

        # Fetch order status from the database
        order_status = db_helper.get_order_status(order_id)
        
        if not order_status:
            logger.debug(f"No status found for order ID: {order_id}")
            return JSONResponse(content={
                "fulfillmentText": f"Sorry, I couldn't find any order with the ID #{order_id}. Please check and try again."
            })

        # Respond with the order status
        return JSONResponse(content={
            "fulfillmentText": f"Your order (ID #{order_id}) is currently {order_status}. Thanks for checking in!"
        })

    except Exception as e:
        logger.error(f"Error in track_order: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I encountered an error while trying to track your order. Please try again later."
        })
def save_to_db(order: dict):
    try:
        # Get the next order ID
        next_order_id = db_helper.get_next_order_id()
        
        if not next_order_id or not isinstance(next_order_id, int):
            logger.error("Could not generate a valid next order ID.")
            return -1  # Return -1 if order ID generation fails

        logger.debug(f"Saving order with ID: {next_order_id}")

        # Insert each food item and its quantity into the database
        for food_item, quantity in order.items():
            try:
                rcode = db_helper.insert_order_item(food_item, quantity, next_order_id)
                if rcode == -1:
                    logger.error(f"Failed to insert order item: {food_item} (Quantity: {quantity})")
                    return -1
            except Exception as e:
                logger.error(f"Error inserting order item {food_item}: {str(e)}\n{traceback.format_exc()}")
                return -1

        # Insert the order's tracking status
        try:
            db_helper.insert_order_tracking(next_order_id, "in progress")
        except Exception as e:
            logger.error(f"Error inserting order tracking for Order ID {next_order_id}: {str(e)}\n{traceback.format_exc()}")
            return -1

        return next_order_id  # Return the order ID if everything succeeds

    except Exception as e:
        logger.error(f"Error in save_to_db: {str(e)}\n{traceback.format_exc()}")
        return -1  # Return -1 if there is a general error

def complete_order(parameters: dict, session_id: str):
    try:
        if session_id not in inprogress_orders:
            logger.debug(f"Session ID {session_id} not found for completing the order.")
            return JSONResponse(content={
                "fulfillmentText": "I couldn't locate your order. Could you start a new one?"
            })

        order = inprogress_orders[session_id]
        logger.debug(f"Completing order for session {session_id}: {order}")

        order_id = save_to_db(order)
        if order_id == -1:
            logger.error("Failed to save order to the database.")
            return JSONResponse(content={
                "fulfillmentText": "Sorry, I couldn't process your order. Please try again."
            })

        order_total = db_helper.get_total_order_price(order_id)
        if not order_total:
            logger.error(f"Failed to fetch total price for order ID {order_id}.")
            return JSONResponse(content={
                "fulfillmentText": "Sorry, I couldn't calculate the total for your order. Please try again."
            })

        del inprogress_orders[session_id]

        return JSONResponse(content={
            "fulfillmentText": f"Your order (ID #{order_id}) is confirmed! The total amount is {order_total}. Thanks for ordering!"
        })

    except Exception as e:
        logger.error(f"Error in complete_order: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I couldn't complete your order due to an error. Please try again."
        })

def add_to_order(parameters: dict, session_id: str):
    try:
        food_items = parameters.get("food_items", [])
        quantities = parameters.get("number", [])

        logger.debug(f"Adding to order - Items: {food_items}, Quantities: {quantities}")

        if not food_items or not quantities or len(food_items) != len(quantities):
            return JSONResponse(content={
                "fulfillmentText": "Sorry, I didn't understand the order items and quantities. Could you please specify them clearly?"
            })

        new_food_dict = dict(zip(food_items, quantities))

        if session_id in inprogress_orders:
            current_food_dict = inprogress_orders[session_id]
            for item, qty in new_food_dict.items():
                current_food_dict[item] = current_food_dict.get(item, 0) + qty
            inprogress_orders[session_id] = current_food_dict
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])

        return JSONResponse(content={
            "fulfillmentText": f"So far you have: {order_str}. Do you need anything else?"
        })
    except Exception as e:
        logger.error(f"Error in add_to_order: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I had trouble adding items to your order. Please try again."
        })

def remove_from_order(parameters: dict, session_id: str):
    try:
        if session_id not in inprogress_orders:
            return JSONResponse(content={
                "fulfillmentText": "I'm having trouble finding your order. Sorry! Can you place a new order please?"
            })

        food_items = parameters.get("food_items", [])
        current_order = inprogress_orders[session_id]

        logger.debug(f"Removing items {food_items} from order {session_id}")

        removed_items = []
        no_such_items = []

        for item in food_items:
            if item in current_order:
                removed_items.append(item)
                del current_order[item]
            else:
                no_such_items.append(item)

        fulfillment_text = ""
        if removed_items:
            fulfillment_text = f"Removed {', '.join(removed_items)} from your order!"
        if no_such_items:
            fulfillment_text += f" Note: {', '.join(no_such_items)} were not in your order."
        if not current_order:
            fulfillment_text += " Your order is now empty!"
        else:
            order_str = generic_helper.get_str_from_food_dict(current_order)
            fulfillment_text += f" Remaining items in your order: {order_str}"

        return JSONResponse(content={
            "fulfillmentText": fulfillment_text
        })
    
    except Exception as e:
        logger.error(f"Error in remove_from_order: {str(e)}\n{traceback.format_exc()}")
        return JSONResponse(content={
            "fulfillmentText": "Sorry, I couldn't remove items from your order. Please try again."
        })
