from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from models import db, Account, Transaction, Inventory
from datetime import datetime

app = Flask(__name__)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Function to initialize the database with default values
def init_db():
    # Create tables
    db.create_all()

    # Check if there are any records in the Account table
    if not Account.query.first():
        # If no records, create an initial account record with default balance
        initial_balance = 1000000
        initial_account = Account(balance=initial_balance)
        db.session.add(initial_account)
        db.session.commit()

@app.route('/')
def main_page():
    #account_balance = Account.query.first().balance
    inventory = Inventory.query.all()
    account = Account.query.first()
    account_balance = account.balance if account else 1000000
    return render_template('mainpage.html', account_balance=account_balance, inventory=inventory)

@app.route('/purchase', methods=['get','POST'])
def purchase():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price_per_unit = float(request.form['price_per_unit'])
        quantity = int(request.form['quantity'])

        total_cost = quantity * price_per_unit

        # Check if the product exists in the inventory
        product = Inventory.query.filter_by(product_name=product_name).first()

        if product is None:
            # Product doesn't exist, add it to the inventory
            product = Inventory(product_name=product_name, quantity=0, price_per_unit=price_per_unit)
            db.session.add(product)
            db.session.commit()

        # Update inventory
        product.quantity += quantity
        db.session.commit()

        # Update balance
        account = Account.query.first()
        account.balance -= total_cost

        # Add transaction to history
        transaction = Transaction(
            timestamp=datetime.now(),
            description=f"Purchased {quantity} units of {product_name} at ${price_per_unit} each.",
            amount = total_cost
        )
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('main_page'))
    return render_template('purchase.html')


@app.route('/sale', methods=['GET', 'POST'])
def sale():
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price_per_unit = float(request.form['price_per_unit'])

        total_price = quantity * price_per_unit

        # Find the product in inventory
        product = Inventory.query.filter_by(product_name=product_name).first()

        # Check if the product is None (not found)
        if product is None:
            return "Error: Product not found."

        # Check if the quantity requested for sale exceeds the available stock
        if product.quantity < quantity:
            return "Error: Not enough stock for sale."

        # Proceed with the sale
        # Update inventory
        product.quantity -= quantity

        # Update balance
        account = Account.query.first()
        account.balance += total_price

        # Add transaction to history
        transaction = Transaction(
            timestamp=datetime.now(),
            transaction_type='Sale',
            description=f"Sold {quantity} units of {product_name} at ${price_per_unit} each.",
            amount=quantity
        )

        # Commit all changes
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('main_page'))

    return render_template('sale.html')

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    account = Account.query.first()
    if request.method == 'POST':
        operation = request.form['operation']
        amount = float(request.form['balance'])

        if operation == 'add':
            account.balance += amount
        elif operation == 'subtract':
            account.balance -= amount

        new_transaction = Transaction(description=f"Balance {operation}: ${amount}",
                                       amount=amount if operation == 'add' else -amount,
                                       timestamp=datetime.now(),
                                      transaction_type='Balance')
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('main_page'))
    return render_template('balance.html', account_balance=account.balance)

@app.route('/history')
def history():
    transactions = Transaction.query.all()
    return render_template('history.html', transactions=transactions)

if __name__ == '__main__':
    with app.app_context():
        init_db()

    app.run(debug=True)
