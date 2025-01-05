import os, secrets
from flask import Flask
from config import Config
from datetime import datetime

app = Flask(__name__, static_url_path='/static')

default_secret_key = secrets.token_hex(8)
app.secret_key = os.getenv('SECRET_KEY', default_secret_key)

@app.template_filter('format_date')
def format_date(value):
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')  # Adjust format as needed
    elif isinstance(value, str):
        return datetime.strptime(value, '%Y-%m-%d').strftime('%m-%d-%Y')  # Adjust format as needed
    return value  # Return as is if it's neither

@app.template_filter('format_time')
def format_time(time_str):
    if isinstance(time_str, str) and time_str:  # Check if input is a non-empty string
        try:
            # Attempt to parse the time string
            time_obj = datetime.strptime(time_str, '%H:%M')
            return time_obj.strftime('%I:%M %p')  # Format as needed (12-hour format)
        except ValueError:
            return 'Invalid time'  # Handle parsing errors gracefully
    return 'N/A'  # Return 'N/A' if input is not valid

@app.template_filter('format_reservation_type')
def format_reservation_type(type_str):
    return ' '.join(word.capitalize() for word in type_str.split('_'))

app.config.from_object(Config)

from app import router

app.jinja_env.filters['format_date'] = format_date
app.jinja_env.filters['format_time'] = format_time
app.jinja_env.filters['format_reservation_type'] = format_reservation_type

app.register_blueprint(router.bp)

