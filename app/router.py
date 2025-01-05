# index.py
import os, re
from config import Config
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest
from flask import Blueprint, request, current_app, redirect, url_for, send_from_directory,jsonify
from app.utils import (write_record_to_json, render_page, update_record_by_hash_key, get_json_data,
delete_record_by_hash_key, get_record_by_hash_key, generate_reservation_key, generate_sample_data)


bp = Blueprint('main', __name__)


# ------------------ Helper Routes ----------------------------
@bp.route('/css/<page_name>.css')
def serve_css(page_name):
    return send_from_directory(os.path.join(current_app.root_path, 'templates', page_name), f'{page_name}.css')

@bp.route('/js/<page_name>.js')
def serve_js(page_name):
    return send_from_directory(os.path.join(current_app.root_path, 'templates', page_name), f'{page_name}.js')

@bp.route('/templates/<path:filename>')
def serve_template_file(filename):
    return send_from_directory('templates', filename)


# -------------------------- Error Handling --------------------------
@bp.route('/error')
def error():

    page_title = 'error'
    return render_page(page_title)


# -------------------------- Main Route --------------------------
@bp.route('/')
@bp.route('/<page_name>')
def main(page_name='home'):

    page_title = page_name
    try:
        return render_page(page_title)
    except Exception:
        return redirect(url_for('main.error'))
    

# -------------------------- Reservation API POST --------------------------
@bp.route('/api/reservation', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    # Extract fields from the incoming data
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    reservation_type = data.get('reservation_type')
    reservation_date = data.get('reservation_date')  # Expecting 'YYYY-MM-DD'
    reservation_time = data.get('reservation_time')  # Expecting 'HH:MM'

    # Validate first name and last name
    if not isinstance(first_name, str) or not first_name.strip():
        return jsonify({"success": False, "message": "First name must be a non-empty text"}), 400

    if not isinstance(last_name, str) or not last_name.strip():
        return jsonify({"success": False, "message": "Last name must be a non-empty text"}), 400

    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"success": False, "message": "Email must be a valid email address"}), 400

    # Validate reservation type
    valid_types = [type[0] for type in current_app.config['RESERVATION_TYPES']]  
    if reservation_type not in valid_types:
        return jsonify({"success": False, 
                        "message": f"Reservation type must be one of the following: {current_app.config['RESERVATION_TYPES']}"}), 400

    # Validate reservation date and time
    if not reservation_date or not reservation_time:
        return jsonify({"success": False, "message": "Reservation date and time must be provided"}), 400
    
    try:
        # Parse the reservation date and time separately
        reservation_date_obj = datetime.strptime(reservation_date, '%Y-%m-%d').date()
        reservation_time_obj = datetime.strptime(reservation_time, '%H:%M').time()

        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).date()

        # Check if the reservation date is today or in the past
        if reservation_date_obj < tomorrow:
            return jsonify({"success": False, "message": "Reservation date cannot be today or in the past"}), 400

        # Check if the reservation is more than two weeks in the future
        if reservation_date_obj > (now + timedelta(weeks=2)).date():
            return jsonify({"success": False, "message": "Reservation date cannot be more than two weeks in the future"}), 400

        # Check if the reservation time is between 9 AM and 4 PM
        if not (9 <= reservation_time_obj.hour < 16):
            return jsonify({"success": False, "message": "Reservation time must be between 9 AM and 4 PM"}), 400

        # Generate a random reservation key
        reservation_key = generate_reservation_key()

        # Write record to JSON (assuming this function handles writing correctly)
        write_record_to_json(data, current_app.config['DATA_FILE'], reservation_key)

        return jsonify({
            "success": True,
            "message": "Reservation created successfully",
            "data": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "reservation_type": reservation_type,
                "reservation_date": reservation_date,
                "reservation_time": reservation_time,
                "reservation_key": reservation_key
            }
        }), 201

    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format. Please use YYYY-MM-DD for date and HH:MM for time."}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ----------------------------- Reservation API GET All----------------------------------
@bp.route('/api/reservation', methods=['GET'])
def get_all_reservations():
    file_path = 'data.json'  # Replace with the actual path to your JSON file
    reservations = get_json_data(file_path)
    
    if reservations is None:
        return jsonify({"error": "Unable to read reservations data"}), 500
    
    return jsonify(reservations)


# -------------------------- Reservation API GET by hash key -----------------------------
@bp.route('/api/reservation/<hash_key>', methods=['GET'])
def get_reservation(hash_key):
    reservation = get_record_by_hash_key(hash_key)
    if reservation is None:
        return jsonify({"error": "Reservation not found"}), 404
    return jsonify(reservation), 200


# --------------------------- Reservation API PUT ---------------------------------------
@bp.route('/api/reservation/<hash_key>', methods=['PUT'])
def update_reservation(hash_key):
    # Extract updated data from the request
    updated_data = {
        'first_name': request.json.get('first_name'),
        'last_name': request.json.get('last_name'),
        'email': request.json.get('email'),  # Ensure 'email' is used here
        'reservation_type': request.json.get('reservation_type'),
        'reservation_date': request.json.get('reservation_date'),
        'reservation_time': request.json.get('reservation_time')
    }

    # Log the incoming update request
    current_app.logger.info(f"Updating reservation for hash key: {hash_key} with data: {updated_data}")

    if not updated_data:
        current_app.logger.warning("No data provided for update.")
        return jsonify({"error": "No data provided"}), BadRequest.code

    try:
        success = update_record_by_hash_key(hash_key, updated_data, current_app.config['DATA_FILE'])
        
        if not success:
            current_app.logger.warning(f"Update failed for hash key: {hash_key}")
            return jsonify({"error": "Failed to update reservation. Please check the hash key."}), 404
        
        current_app.logger.info("Reservation updated successfully.")
        return jsonify({"message": "Reservation updated successfully"}), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating reservation: {str(e)}")
        return jsonify({"error": "An internal error occurred. Please try again later."}), 500


# ----------------------------- Reservation API DELETE -------------------------------------
@bp.route('/api/reservation/<hash_key>', methods=['DELETE'])
def delete_reservation(hash_key):
    success = delete_record_by_hash_key(hash_key, current_app.config['DATA_FILE'])
    if not success:
        return jsonify({"error": "Reservation not found"}), 404
    return jsonify({"message": "Reservation deleted successfully"}), 200



# -------------------------- Client side routing --------------------------
@bp.route('/reserve', methods=['GET'])
def serve_reserve_page():
    page_title = 'reserve'
    reservation_types = current_app.config['RESERVATION_TYPES']  # Accessing reservation types from config
    return render_page(page_title, reservation_types=reservation_types)


@bp.route('/reservation', methods=['GET'])
def serve_reservation_page():
    page_title = 'reservation'
    reservation_key = request.args.get('key')
    reservation_data = get_record_by_hash_key(reservation_key) 
    return render_page(page_title, reservation_data=reservation_data)


@bp.route('/reservations')
def serve_reservations_page():
    data_file = current_app.config['DATA_FILE']

    # Check if the data file exists; if not, create it
    if not os.path.exists(data_file):
        with open(data_file, 'w') as f:
            f.write('[]')

    # Retrieve reservations data
    reservations = get_json_data(data_file)

    # Generate sample data if necessary
    if reservations is None or len(reservations) < 3:
        generate_sample_data(current_app.config['RESERVATION_TYPES'], data_file)

    reservations = get_json_data(data_file)

    # Sort reservations by reservation_date (most recent first)
    reservations_sorted = sorted(reservations, 
                                key=lambda x: datetime.strptime(x['reservation_date'], '%Y-%m-%d'), 
                                reverse=False)

    page_title = 'reservations'
    return render_page(page_title, reservations=reservations_sorted)




@bp.route('/update', methods=['GET'])
def serve_update_page():
    page_title = 'edit_reservation'
    hash_key = request.args.get('hash_key')
    reservation = get_record_by_hash_key(hash_key)
    RESERVATION_TYPES = current_app.config['RESERVATION_TYPES']
    
    # Ensure you pass 'reservation_types' to the template
    return render_page(page_title, reservation=reservation, reservation_types=RESERVATION_TYPES)


@bp.route('/delete', methods=['GET'])
def serve_delete_page():
    page_title = 'delete_reservation'
    hash_key = request.args.get('hash_key')
    reservation = get_record_by_hash_key(hash_key)
    
    # Ensure you pass 'reservation_types' to the template
    return render_page(page_title, reservation=reservation)


    
