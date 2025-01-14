from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Initialize the Flask application
app = Flask(__name__)

# Secret key for session management and CSRF protection
app.config['SECRET_KEY'] = "minha_chave_123"

# Configure the database using SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

# Initialize Flask extensions
login_manager = LoginManager()  # Manages user sessions
db = SQLAlchemy(app)  # Database connection and ORM
login_manager.init_app(app)  # Attach LoginManager to the app
login_manager.login_view = 'login'  # Set the login route for unauthorized users
CORS(app)  # Enable Cross-Origin Resource Sharing

# Model definitions

# User model: Represents the users of the system
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    username = db.Column(db.String(120), nullable=False, unique=True)  # Unique username
    password = db.Column(db.String(120), nullable=False)  # User's password
    cart = db.relationship('CartItem', backref='user', lazy=True)  # Relationship with CartItem

# Product model: Represents the products in the system
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique product ID
    name = db.Column(db.String(120), nullable=False)  # Product name
    price = db.Column(db.Float, nullable=False)  # Product price
    description = db.Column(db.Text, nullable=False)  # Product description

# CartItem model: Represents items in a user's cart
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique cart item ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Associated user
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Associated product

# Function to load a user from the database by their ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes

# Login route: Authenticates a user
@app.route('/login', methods=["POST"])
def login():
    data = request.json  # Parse incoming JSON data
    user = User.query.filter_by(username=data.get("username")).first()  # Find user by username
    if user and data.get("password") == user.password:  # Validate credentials
        login_user(user)  # Log the user in
        return jsonify({"message": "Logged in successfully"}), 200
    return jsonify({"message": "Unauthorized. Invalid credentials"}), 401

# Logout route: Logs out the current user
@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()  # End the user session
    return jsonify({"message": "Logout successfully"}), 200

# Add product route: Adds a new product to the database
@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json  # Parse incoming JSON data
    if 'name' in data and 'price' in data:  # Validate required fields
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
        db.session.add(product)  # Add product to the database
        db.session.commit()
        return jsonify({"message": "Product added successfully"}), 200
    return jsonify({"message": "Invalid product data"}), 400

# Delete product route: Deletes a product by its ID
@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)  # Find product by ID
    if product:
        db.session.delete(product)  # Remove product from the database
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"}), 200
    return jsonify({"message": "Product not found"}), 404

# Get product details route: Retrieves details of a specific product
@app.route('/api/products/<int:product_id>', methods=["GET"])
@login_required
def get_product_details(product_id):
    product = Product.query.get(product_id)  # Find product by ID
    if product:
        return jsonify({
            "id": product_id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404

# Update product route: Updates details of a specific product
@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)  # Find product by ID
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.json  # Parse incoming JSON data
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']
    db.session.commit()  # Save updates
    return jsonify({"message": "Product updated successfully"})

# Get all products route: Retrieves a list of all products
@app.route('/api/products', methods=["GET"])
@login_required
def get_products():
    products = Product.query.all()  # Get all products
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        } for product in products
    ]
    return {"products": product_list}, 200

# Implement the add to cart functionality
@app.route('/api/cart/add/<int:product_id>', methods=["POST"])
def add_cart(product_id):
    #User
    user = User.query.get(current_user.id)
    #Password
    product = Product.query.get(product_id)

    if user and product:
        cart_item = CartItem(user_id = user.id, product_id = product.id)
        db.session.add(cart_item)
        db.session.commit()
        return jsonify({"message" : "Item added to cart sucessfully"}), 200
    return jsonify({"message" : "Item not found"}), 404

# Main entry point: Runs the application
if __name__ == '__main__':
    app.run(debug=True)  # Run the app in debug mode (not for production)