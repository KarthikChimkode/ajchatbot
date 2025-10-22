import requests
import json
import uuid
import logging
import sys
import os
from datetime import datetime

# Configure logging
try:
    logger = logging.getLogger('LawfeatAPI')
    logger.setLevel(logging.DEBUG)
    logger.handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    log_file = 'lawfeat_api.log'
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    except PermissionError as e:
        print(f"Warning: Cannot write to log file {log_file}: {str(e)}")
        logger.warning(f"Cannot write to log file {log_file}: {str(e)}. Logging to console only.")

    logger.info("Logging setup complete. Starting script execution.")
except Exception as e:
    print(f"Critical: Failed to configure logging: {str(e)}")
    raise

BASE_URL = "https://lawfeat.com/aj/api/public/category/getAll?status=AceJobber&page=0&size=20"
HEADERS = {"X-Api-Key": "acejobberpublicsecret"}
REQUEST_TIMEOUT = 10  # Timeout for API requests in seconds

def fetch_all_categories():
    logger.info("Starting category fetch process")
    all_categories = []
    size = sys.maxsize  # Request maximum possible records

    params = {"status": "AceJobber", "page": 0, "size": size}
    logger.info(f"Fetching all categories with params: {params}")

    try:
        logger.debug(f"Sending request to {BASE_URL} with headers: {HEADERS}")
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        logger.info(f"Received response with status code: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Failed to fetch data: Status code {response.status_code}")
            return all_categories

        try:
            data = response.json()
            logger.debug(f"Response JSON: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return all_categories

        # Log pagination metadata (if available)
        total_pages = data.get("totalPages", 0)
        total_elements = data.get("totalElements", 0)
        is_last = data.get("last", False)
        logger.info(f"Pagination info: totalPages={total_pages}, totalElements={total_elements}, last={is_last}")

        # Extract categories
        categories = data.get("content", [])
        logger.info(f"Found {len(categories)} categories in response")

        if not categories:
            logger.info("No categories returned.")
            return all_categories

        for cat in categories:
            logger.debug(f"Processing category: {cat.get('name', 'Unknown Category')}")
            entry = {
                "id": cat.get("id", 0),
                "name": cat.get("name", "Unknown Category"),
                "services": []
            }
            services = cat.get("services", [])
            logger.debug(f"Found {len(services)} services in category {entry['name']}")

            for service in services:
                service_entry = {
                    "id": service.get("id", 0),
                    "serviceName": service.get("serviceName", "Unknown Service"),
                    "rate": service.get("rate", "N/A")
                }
                entry["services"].append(service_entry)
                logger.debug(f"Added service: {service_entry['serviceName']}")

            all_categories.append(entry)
            logger.info(f"Processed category: {entry['name']} with {len(entry['services'])} services")

    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        print(f"Error: Request failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: Unexpected error: {str(e)}")

    # Save to JSON
    try:
        with open("lawfeat_services.json", "w", encoding="utf-8") as f:
            json.dump(all_categories, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved {len(all_categories)} categories to lawfeat_services_api.json")
    except Exception as e:
        logger.error(f"Failed to save categories to JSON file: {str(e)}")
        print(f"Error: Failed to save JSON file: {str(e)}")

    logger.info(f"Scraped {len(all_categories)} categories. Process completed.")
    return all_categories

if __name__ == "__main__":
    logger.info(f"Script started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        fetch_all_categories()
    except Exception as e:
        logger.critical(f"Script failed: {str(e)}")
        print(f"Critical: Script failed: {str(e)}")
    logger.info("Script execution finished")