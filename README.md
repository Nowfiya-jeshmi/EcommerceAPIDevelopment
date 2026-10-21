E-commerce API Project
Overview
This project is a fully functional e-commerce API built with Flask, SQLAlchemy, Marshmallow, and MySQL. It supports advanced order management, pagination, and JWT authentication for secure user operations.

Features
🟢 User Management (JWT protected)
Create, read, update, delete users

Supports pagination when listing users (e.g., /users?page=1&per_page=5)

JWT login to generate access tokens

🟢 Product Management
Create, read, update, delete products

Supports pagination when listing products

🟢 Order Management
Create orders

Add or remove products from orders

Get all orders by a user

View all products in an order

Get total price of an order

Technologies
Python

Flask

Flask-SQLAlchemy

Flask-Marshmallow

Marshmallow-SQLAlchemy

MySQL

Flask-JWT-Extended

Postman (for testing)

Setup
1️⃣ Create a MySQL database named ecommerce_api using MySQL Workbench.

2️⃣ Clone or download this repository.

3️⃣ Create a virtual environment:

python -m venv venv

4️⃣ Activate the environment:

venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux

5️⃣ Install dependencies:

pip install -r requirements.txt

If you don't have requirements.txt, install manually:

pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy mysql-connector-python Flask-JWT-Extended

6️⃣ Update your MySQL root password in app.py:

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:YourPassword@localhost/ecommerce_api'

7️⃣ Run the app:

python app.py

JWT Authentication Usage
First, create a user in the database (via /users POST or directly).

Use /login endpoint to get a JWT token by providing the email.

Copy the returned token and add it as a Bearer Token in Postman when accessing protected user endpoints.

Example Endpoints
Login (get token)

POST /login
Body:
{"email": "user@example.com"}

Create User (requires JWT)

POST /users
Authorization: Bearer <your_token>
Body:
{"name": "John Doe", "address": "123 Main St", "email": "user@example.com"}

List Users with Pagination

GET /users?page=1&per_page=5
Authorization: Bearer <your_token>

Get Order Total

GET /orders/1/total

Author
Leah Crockwell

