# AI-Powered Restaurant Order Management System

## Project Description
This project is an AI-driven restaurant order management system implemented using FastAPI and MySQL. The system handles customer orders, tracks their statuses, and manages database interactions. It offers endpoints for managing orders, including adding, removing, and tracking items, with robust error handling and logging for improved reliability.

## Features
- **Order Management**: Add, remove, and track orders seamlessly.
- **Database Integration**: Interacts with a MySQL database to store and retrieve order details.
- **Intent-Based Processing**: Leverages intent-based handlers for dynamic responses.
- **Session Handling**: Maintains order progress for multiple sessions.
- **Custom Helpers**: Provides utility functions for clean and efficient code.

## File Overview
### `main.py`
- Entry point of the application.
- Implements a FastAPI server to handle HTTP requests.
- Routes:
  - `POST /`: Handles incoming requests and dispatches to intent handlers.
- Intent Handlers:
  - `add_to_order`: Adds items to the current order.
  - `remove_from_order`: Removes items from the current order.
  - `complete_order`: Finalizes an order and calculates the total.
  - `track_order`: Retrieves the current status of an order.

### `db_helper.py`
- Handles database operations using MySQL.
- Functions:
  - `insert_order_item`: Inserts an item into an order.
  - `insert_order_tracking`: Updates order tracking information.
  - `get_total_order_price`: Fetches the total price of an order.
  - `get_next_order_id`: Generates the next order ID.
  - `get_order_status`: Retrieves the current status of an order.

### `generic_helper.py`
- Provides utility functions for the project.
- Functions:
  - `get_str_from_food_dict`: Converts a food item dictionary into a readable string.
  - `extract_session_id`: Extracts the session ID from a string.

## Requirements
- Python 3.9+
- MySQL Database
- FastAPI
- mysql-connector-python

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure the MySQL database:
   - Update the credentials in `db_helper.py`.
   - Ensure the database schema includes:
     - Stored procedure `insert_order_item`.
     - Function `get_total_order_price`.
     - Tables `orders` and `order_tracking`.
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```


## Future Enhancements
- Add more functionallity like Discounts, Offers etc.
- Implement a front-end interface.
- Support multiple databases.



