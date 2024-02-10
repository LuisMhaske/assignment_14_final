from flask import Flask, render_template, request, redirect, url_for
from models import db, Account, Transaction, Inventory
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def main_page():
    account_balance = Account.query.first().balance
    inventory = Inventory.query.all()
    return render_template('main_page.html', account_balance=account_balance, inventory=inventory)

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    if request.method == 'POST':
        product_name = request.form['product_name']
        unit_price = float(request.form['unit_price'])
        quantity = int(request.form['quantity'])

        new_transaction = Transaction(description=f"Purchased: {product_name}",
                                       amount=unit_price * quantity,
                                       timestamp=datetime.now())
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('main_page'))
    return render_template('purchase.html')

@app.route('/sale', methods=['GET', 'POST'])
def sale():
    if request.method == 'POST':
        product_name = request.form['product_name']
        unit_price = float(request.form['unit_price'])
        quantity = int(request.form['quantity'])

        new_transaction = Transaction(description=f"Sold: {product_name}",
                                       amount=unit_price * quantity * -1,
                                       timestamp=datetime.now())
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('main_page'))
    return render_template('sale.html')

@app.route('/balance', methods=['GET', 'POST'])
def balance():
    account = Account.query.first()
    if request.method == 'POST':
        operation = request.form['operation']
        amount = float(request.form['amount'])

        if operation == 'add':
            account.balance += amount
        elif operation == 'subtract':
            account.balance -= amount

        new_transaction = Transaction(description=f"Balance {operation}: ${amount}",
                                       amount=amount if operation == 'add' else -amount,
                                       timestamp=datetime.now())
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('main_page'))
    return render_template('balance.html', account_balance=account.balance)

@app.route('/history')
def history():
    transactions = Transaction.query.all()
    return render_template('history.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)
