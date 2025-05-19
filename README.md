# Lab Management System

## Project Overview
This is a Laboratory Management System developed as a graduation project for Almaarefa University. The system provides separate interfaces for staff and IT team members to manage computer labs, track equipment status, and handle technical issues through a ticket system.

## Features

### Staff Interface
- View all computer labs and their equipment
- See detailed information about each computer
- Report technical issues by creating tickets
- Track the status of submitted tickets

### IT Team Interface
- Dashboard with system statistics 
- Comprehensive ticket management system
- Lab overview and equipment monitoring
- Track and resolve reported issues

## Technologies Used
- **Backend**: Python and Flask framework
- **Database**: MySQL
- **Frontend**: HTML, CSS, and JavaScript
- **Authentication**: Session-based user authentication

## Installation and Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- pip (Python package manager)

### Database Setup
1. Create a MySQL database:
CREATE DATABASE lab_management;

2. Update the database configuration in app.py:
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/lab_management'

### Installation Steps
1. Clone the repository or download the source code
2. Create a virtual environment:
```py
python -m venv venv
```
4. Activate the virtual environment:

  - Windows: venv\Scripts\activate
  - macOS/Linux: source venv/bin/activate
  
4. Install the required packages:
```bash
pip install -r /path/to/requirements.txt
```
6. Run the application:
```bash
flask run
```
8. Access the application at http://127.0.0.1:5000

## Default Login Credentials
- **Staff User**: 
 - Username: staff1
 - Password: staff123
- **IT User**: 
 - Username: it1
 - Password: it123

## System Architecture
The application follows the MVC (Model-View-Controller) pattern:
- Models: Database models (User, Lab, Computer, Ticket)
- Views: HTML templates with Jinja2
- Controllers: Flask routes that handle requests


Department of Information Systems
Almaarefa University
