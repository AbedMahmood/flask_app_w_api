# utils.py
import os, re
import json
import secrets
import string
import random
from config import Config
from flask import render_template, current_app
from datetime import datetime, timedelta


# --------------------- Data Functions ---------------------
def generate_reservation_key(length=6):
    """Generate a random hexadecimal reservation key."""
    characters = string.hexdigits[:-6]  # Exclude 'abcdef' for lowercase
    return ''.join(random.choice(characters) for _ in range(length))


def save_json_data(data, file_path):
    """Helper function to save JSON data to a file."""
    with open(file_path, 'w') as f:
        json.dump(data, f)


def get_json_data(file_path):
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON data: {e}")
        return None


def write_record_to_json(data, file_path, reservation_key):
    """Function to write the reservation data to a JSON file."""
    data['reservation_key'] = reservation_key
    
    try:
        # Read existing data
        with open(file_path, 'r') as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    
    # Append new data
    records.append(data)
    
    # Write updated data back to file
    with open(file_path, 'w') as f:
        json.dump(records, f, indent=4)


def get_record_by_hash_key(hash_key):
    reservations = get_json_data(current_app.config['DATA_FILE'])
    reservation = next((r for r in reservations if r['reservation_key'] == hash_key), None)
    return reservation




def update_record_by_hash_key(hash_key, updated_data, DATA_FILE):
    reservations = get_json_data(DATA_FILE)
    updated_reservations = []
    record_updated = False  # Flag to track if an update occurred
    
    for reservation in reservations:
        if reservation.get('reservation_key') == hash_key:  # Use .get() to avoid KeyError
            reservation.update(updated_data)  # Update with new data
            record_updated = True  # Mark that we updated a record
        updated_reservations.append(reservation)
    
    with open(DATA_FILE, 'w') as file:
        json.dump(updated_reservations, file, indent=4)

    current_app.logger.info(f"Updated reservations: {updated_reservations}")  # Log all reservations after update
    return record_updated  # Return whether an update occurred




def delete_record_by_hash_key(hash_key, DATA_FILE):
    reservations = get_json_data(DATA_FILE)
    updated_reservations = [r for r in reservations if r['reservation_key'] != hash_key]
    
    with open(DATA_FILE, 'w') as file:
        json.dump(updated_reservations, file, indent=4)
    
    return len(reservations) != len(updated_reservations)




# --------------------- Helper Functions for data ---------------------
# count records
def count_records(DATA_FILE):
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as file:
                data = json.load(file)
                return len(data)
        else:
            print("Error: The specified JSON file was not found.")
            return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

# if validated reserve
def if_validated_reserve(data):
    required_fields = ['first_name', 'last_name', 'email', 'reservation_type', 'reservation_date', 'reservation_time']

    for field in required_fields:
        if not data.get(field):
            return False, f"{field.replace('_', ' ').capitalize()} is required."
    
    # Check email validity
    if not re.match(r'^[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', data.get('email', '')):
        return False, "Invalid email format."

    # Ensure reservation date is in the future
    current_date = datetime.now().date()
    try:
        reservation_date = datetime.strptime(data['reservation_date'], "%Y-%m-%d").date()
        if reservation_date < current_date:
            return False, "Reservation date cannot be in the past."
    except ValueError:
        return False, "Invalid reservation date."

    return True, "Validated"


# --------------------- Template Utility Function ---------------------
def render_page(page_name, **context):
    # Set default context values
    context.setdefault('website_name', Config.WEBSITE_NAME)
    context.setdefault('page_title', page_name.capitalize())
    context.setdefault('body_class', page_name)
    context.setdefault('page_name', page_name)

    # Render the template with the provided context
    return render_template(f'{page_name}/{page_name}.html', **context)


# --------------------- Sample Data Generation ---------------------
def generate_sample_data(RESERVATION_TYPES, DATA_FILE):
    existing_data = get_json_data(DATA_FILE)
    
    if len(existing_data) >= 10:
        return  # Don't generate new data if there are already 10 or more records

    num_records_to_generate = max(6 - len(existing_data), 0)  # Generate up to 6 records total

    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana"]
    last_names = ["Doe", "Smith", "Johnson", "Williams", "Brown", "Jones"]
    reservation_types = [rtype[0] for rtype in RESERVATION_TYPES]
    times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]

    new_data = []
    for _ in range(num_records_to_generate):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        record = {
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "reservation_type": random.choice(reservation_types),
            "reservation_date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
            "reservation_time": random.choice(times),
            "reservation_key": ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
        }
        new_data.append(record)

    combined_data = existing_data + new_data

    with open(DATA_FILE, 'w') as file:
        json.dump(combined_data, file, indent=4)


