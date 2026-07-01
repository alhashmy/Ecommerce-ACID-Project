import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2

app = Flask(__name__)
app.secret_key = "super_secret_secure_key_for_session"

# إعدادات قاعدة البيانات المحلية (تتحول تلقائياً للسحابية عند الرفع)
DB_SETTINGS = {
    "host": "localhost",
    "database": "ecommerce_db",
    "user": "postgres",
    "password": "123123123@@@"
}

def get_db_connection():
    cloud_url = os.environ.get("DATABASE_URL")
    if cloud_url:
        return psycopg2.connect(cloud_url, sslmode='require')
    return psycopg2.connect(**DB_SETTINGS)

@app.route('/')
def index():
    cat = request.args.get('cat', 'all')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if cat == 'all':
        cursor.execute("SELECT * FROM products ORDER BY product_id DESC;")
    else:
        cursor.execute("SELECT * FROM products WHERE category = %s ORDER BY product_id DESC;", (cat,))
        
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', products=products, active_cat=cat)

@app.route('/order/<int:product_id>')
def order_form(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id = %s;", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('order_form.html', product=product)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    product_id = int(request.form['product_id'])
    name = request.form['customer_name']
    phone = request.form['customer_phone']
    address = request.form['customer_address']
    quantity = int(request.form['quantity'])
    promo = request.form['promo_code'].strip().upper() or None

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT price, stock_quantity, discount_percentage FROM products WHERE product_id = %s;", (product_id,))
    product_data = cursor.fetchone()
    
    if not product_data:
        cursor.close()
        conn.close()
        return "<h1>❌ المنتج غير موجود!</h1>"
        
    price, stock_quantity, p_discount = product_data
    current_price = float(price) * (1 - float(p_discount)/100)
    total_price = current_price * quantity

    if promo == 'ASHUR':
        total_price = total_price * 0.50

    # إذا كانت الكمية المطلوبة أكبر من المخزن، يرفض الطلب فوراً لحماية السيستم (Predictive Guard)
    if quantity > stock_quantity:
        cursor.execute("""
            INSERT INTO orders (customer_name, customer_phone, customer_address, product_id, quantity, total_price, promo_code, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Rejected') RETURNING order_id;
        """, (name, phone, address, product_id, quantity, total_price, promo))
        order_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('waiting.html', order_id=order_id)

    cursor.execute("""
        INSERT INTO orders (customer_name, customer_phone, customer_address, product_id, quantity, total_price, promo_code, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending') RETURNING order_id;
    """, (name, phone, address, product_id, quantity, total_price, promo))
    
    order_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('waiting.html', order_id=order_id)

@app.route('/api/order_status/<int:order_id>')
def order_status(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM orders WHERE order_id = %s;", (order_id,))
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    if order:
        return jsonify({"status": order[0]})
    return jsonify({"status": "NotFound"}), 404

@app.route('/track', methods=['GET', 'POST'])
def track_order():
    order_data = None
    error = None
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        if order_id:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT o.*, p.product_name 
                    FROM orders o 
                    JOIN products p ON o.product_id = p.product_id 
                    WHERE o.order_id = %s;
                """, (int(order_id),))
                order_data = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if not order_data:
                    error = "❌ عذراً، رقم الطلب هذا غير موجود بنظامنا!"
            except Exception as e:
                error = "❌ يرجى إدخال رقم طلب صحيح!"
                
    return render_template('track.html', order=order_data, error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '123':
            session['admin'] = True
            session['show_welcome'] = True
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="اسم المستخدم أو كلمة المرور خطأ!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    session.pop('show_welcome', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products ORDER BY product_id DESC;")
    products = cursor.fetchall()
    
    show_modal = session.pop('show_welcome', False)
    
    cursor.close()
    conn.close()
    return render_template('dashboard.html', products=products, show_modal=show_modal)

@app.route('/api/admin/orders')
def admin_orders_api():
    if not session.get('admin'): return jsonify({"error": "Unauthorized"}), 401
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT o.*, p.product_name FROM orders o JOIN products p ON o.product_id = p.product_id ORDER BY o.order_id DESC;")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    orders_list = []
    for o in orders:
        orders_list.append({
            "order_id": o[0],
            "customer_name": o[1],
            "customer_phone": o[2],
            "customer_address": o[3],
            "product_id": o[4],
            "quantity": o[5],
            "total_price": float(o[6]),
            "promo_code": o[7],
            "status": o[8]
        })
    return jsonify(orders_list)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if not session.get('admin'): return redirect(url_for('login'))
    name = request.form['product_name']
    category = request.form['category']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    img = request.form['image_url']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (product_name, category, price, stock_quantity, image_url) VALUES (%s, %s, %s, %s, %s);", (name, category, price, stock, img))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if not session.get('admin'): return redirect(url_for('login'))
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    discount = float(request.form['discount'])
    img = request.form['image_url']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products 
        SET price = %s, stock_quantity = %s, discount_percentage = %s, image_url = %s 
        WHERE product_id = %s;
    """, (price, stock, discount, img, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/delete_product/<int:product_id>')
def delete_product(product_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE product_id = %s;", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

# 🔥 ميزة الحذف الفردي والنهائي للطلبات المضافة لتصفية لوحة التحكم وتصفيرها
@app.route('/admin/delete_order/<int:order_id>')
def delete_order(order_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_id = %s;", (order_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/approve/<int:order_id>')
def approve_order(order_id):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, quantity FROM orders WHERE order_id = %s AND status = 'Pending';", (order_id,))
        order = cursor.fetchone()
        if not order: return redirect(url_for('dashboard'))
        
        product_id, quantity = order
        
        cursor.execute("UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s;", (quantity, product_id))
        cursor.execute("UPDATE orders SET status = 'Approved' WHERE order_id = %s;", (order_id,))
        conn.commit()
    except Exception as error:
        if conn: conn.rollback()
        conn_fail = get_db_connection()
        cursor_fail = conn_fail.cursor()
        cursor_fail.execute("UPDATE orders SET status = 'Rejected' WHERE order_id = %s;", (order_id,))
        conn_fail.commit()
    finally:
        if conn: conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/status/<int:order_id>/<string:new_status>')
def change_order_status(order_id, new_status):
    if not session.get('admin'): return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s;", (new_status, order_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/admin/reject/<int:order_id>')
def reject_order(order_id):
    if not session.get('admin'): return redirect(url_for('login'))
    return change_order_status(order_id, 'Rejected')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)