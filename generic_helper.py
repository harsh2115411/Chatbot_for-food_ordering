import re
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_str_from_food_dict(food_dict: dict):
    try:
        if not food_dict:
            return ""
        result = ", ".join([f"{int(value)} {key}" for key, value in food_dict.items()])
        return result
    except Exception as e:
        logger.error(f"Error formatting food dictionary: {e}")
        return ""

def extract_session_id(session_str: str):
    try:
        match = re.search(r"/sessions/(.*?)/contexts/", session_str)
        if match:
            return match.group(1)  # Return just the session ID
        logger.warning(f"No session ID found in string: {session_str}")
        return ""
    except Exception as e:
        logger.error(f"Error extracting session ID: {e}")
        return ""