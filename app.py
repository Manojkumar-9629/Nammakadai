from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
app = Flask(__name__)

app.config['MYSQL_HOSTNAME'] = 'localhost'  # Corrected to MYSQL_HOSTNAME
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'nammakadai'

mysql = MySQL(app)
@app.route('/')
def index():
    # Fetch the cash balance from the Company table
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT cash_balance FROM Company')
    cash_balance = cursor.fetchone()[0]
    
    return render_template('index.html', cash_balance=cash_balance)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        
        # Insert the new item into the Item table
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Item (item_name, qty) VALUES (%s, %s)', (item_name, 0))
        
        # Commit the transaction
        mysql.connection.commit()
        
       # return redirect(url_for('index'))
    
    return render_template('add_item.html')

@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if request.method == 'POST':
        item_id = int(request.form['item_id'])
        qty = int(request.form['qty'])
        
        # Fetch the item price from the database
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT item_name, qty FROM Item WHERE item_id = %s', (item_id,))
        item_data = cursor.fetchone()
        
        if item_data:
            item_name, item_qty = item_data
            item_price = 0
            
            # Assign the appropriate item price based on the item ID
            if item_id == 1:
                item_price = 2
            elif item_id == 2:
                item_price = 5
            elif item_id == 3:
                item_price = 1
            elif item_id == 4:
                item_price = 2
            elif item_id == 5:
                item_price = 10
            
            # Calculate the purchase amount
            purchase_amount = item_price * qty
            
            # Get the current timestamp
            timestamp = datetime.now()
            
            # Insert purchase data into the Purchase table
            cursor.execute('INSERT INTO Purchase (timestamp, item_id, qty, rate, amount) VALUES (%s, %s, %s, %s, %s)',
                           (timestamp, item_id, qty, item_price, purchase_amount))
            
            # Update the cash balance in the Company table
            cursor.execute('UPDATE Company SET cash_balance = cash_balance - %s', (purchase_amount,))
            
            # Update the item quantity in the Item table
            cursor.execute('UPDATE Item SET qty = qty + %s WHERE item_id = %s', (qty, item_id))
            
            # Commit the transactions
            mysql.connection.commit()
            
        return redirect(url_for('index'))
    
    return render_template('add_purchase.html')


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        item_id = int(request.form['item_id'])
        qty = int(request.form['qty'])
        sale_rate = float(request.form['rate'])
        
        # Fetch the item's current quantity from the database
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT qty FROM Item WHERE item_id = %s', (item_id,))
        item_qty = cursor.fetchone()[0]
        
        # Check if there is enough quantity to sell
        if item_qty >= qty:
            # Fetch the purchased rate for the item
            cursor.execute('SELECT rate FROM Purchase WHERE item_id = %s ORDER BY purchase_id DESC LIMIT 1', (item_id,))
            purchased_rate = cursor.fetchone()[0]
            
            # Calculate the sale amount
            sale_amount = sale_rate * qty
            
            # Update the cash balance in the Company table
            cursor.execute('UPDATE Company SET cash_balance = cash_balance + %s', (sale_amount,))
            
            # Insert sale data into the Sales table
            timestamp = datetime.now()  # Get the current timestamp
            cursor.execute('INSERT INTO Sales (timestamp, item_id, qty, rate, amount) VALUES (%s, %s, %s, %s, %s)',
                           (timestamp, item_id, qty, sale_rate, sale_amount))
            
            # Update the item's quantity in the Item table
            cursor.execute('UPDATE Item SET qty = qty - %s WHERE item_id = %s', (qty, item_id))
            
            # Commit the transactions
            mysql.connection.commit()
            
        #return redirect(url_for('index'))
    
    return render_template('add_sale.html')

@app.route('/view_item')
def view_item():
    cursor = mysql.connection.cursor()

    # Fetch all items from the Item table
    cursor.execute('SELECT * FROM Item')
    items = cursor.fetchall()

    return render_template('view_item.html', items=items)



if __name__ == '__main__':
    app.run(debug=True)
