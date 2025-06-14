# TravelHub

A web application for sharing and discovering resort reviews and recommendations.

## Features

- User authentication system
- Resort information display with ratings
- User profiles with review history
- Responsive design for all devices
- Secure password requirements
- Image upload and preview functionality

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd travelhub
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a MySQL database:
```sql
CREATE DATABASE TravelHub;
```

5. Create a `.env` file in the project root with the following content:
```
SECRET_KEY=your-secret-key-here
DB_USER=root
DB_PASSWORD=Woaixuexi123
DB_HOST=localhost
DB_NAME=TravelHub
```

6. Initialize the database:
```bash
python app.py
```

## Running the Application

1. Make sure your MySQL server is running
2. Activate the virtual environment if not already activated
3. Run the Flask application:
```bash
python app.py
```
4. Open your browser and navigate to `http://localhost:5000`

## Default Admin Account

- Username: admin
- Password: world_peace

## Project Structure

```
travelhub/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/          # CSS stylesheets
│   ├── js/           # JavaScript files
│   └── images/       # Image assets
├── templates/         # HTML templates
│   ├── base.html     # Base template
│   ├── home.html     # Home page
│   ├── login.html    # Login page
│   └── profile.html  # Profile page
└── README.md         # Project documentation
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 