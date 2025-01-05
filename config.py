# my_config.py
class Config:
    WEBSITE_NAME = 'Startup'
    YEAR = 2024
    DATA_FILE = 'data.json'
    API_BASE_URL = 'http://127.0.0.1:5000'
    RESERVATION_TYPES = [
        ('orientation', 'Orientation'),
        ('resume_help', 'Resume Help'),
        ('computer_skills', 'Computer Skills'),
        ('skills_in_demand', 'Skills in Demand'),
        ('web_development', 'Web Development'),
        ('networking', 'Networking'),
    ]

