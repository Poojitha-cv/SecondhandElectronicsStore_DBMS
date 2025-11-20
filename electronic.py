import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date
import time
import pandas as pd

# ---------------------------
# CONFIGURATION
# ---------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "pooja@2005",
    "database": "ElectronicsStore"
}

st.set_page_config(page_title="Electronics Store", layout="wide")

st.markdown("""
    <style>
        /* Hide hamburger menu icon */
        button[kind="header"] {display: none !important;}
        [data-testid="stToolbar"] {display: none !important;}
        [data-testid="stHeaderActionMenu"] {display: none !important;}
        header [data-testid="baseButton-headerNoPadding"] {display: none !important;}

        /* Hide Streamlit main menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# ---------------------------
# UTILITIES
# ---------------------------
def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None


def query(sql, params=None):
    """Execute SELECT queries safely and return a list of dict rows."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        st.error(f"Database query error: {e}")
        return []

# ---------------------------
# SINGLE ROW QUERY HELPER
# ---------------------------
def query_one(sql, params=None):
    """Return only the first row (or None) from a SELECT query."""
    rows = query(sql, params)
    return rows[0] if rows else None

def execute(sql, params=None):
    """Execute INSERT, UPDATE, DELETE safely and return True if successful."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        return True
    except Error as e:
        st.error(f"Database execute error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def execute_with_lastrowid(query, params=None):
    """Executes a query and returns the last inserted row ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        return last_id
    except Exception as e:
        st.error(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
def call_proc(proc_name, params=None):
    """Call a stored procedure and return results if any."""
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.callproc(proc_name, params or [])
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        conn.commit()
        return results
    except Error as e:
        st.error(f"Stored procedure call error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# ---------------------------
# SESSION VARIABLES
# ---------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "nav" not in st.session_state:
    st.session_state.nav = "Home"
if "cart" not in st.session_state:
    st.session_state.cart = {}

# ---------------------------
# HEADER WITH LOGO
# ---------------------------
def app_header():
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.image(r"C:\Users\admin\OneDrive\Desktop\PROJECT\logo.jpeg", width=90)
    with col2:
        st.markdown(
            "<h1 style='text-align:left; color:#1E90FF;'>💻 Second hand Electronics Store </h1>",
            unsafe_allow_html=True,
        )
    st.markdown("---")


# ---------------------------
# SIDEBAR NAVIGATION
# ---------------------------
def sidebar_menu():
    st.sidebar.title("📋 Menu")

    user_role = None
    if isinstance(st.session_state.user, dict):
        user_role = st.session_state.user.get("role")

    # CUSTOMER
    if user_role == "customer":
        st.sidebar.markdown("### 👤 Customer Menu")
        if st.sidebar.button("🏠 Home"): st.session_state.nav = "Home"
        if st.sidebar.button("🛒 Browse Items"): st.session_state.nav = "Browse Items"
        if st.sidebar.button("🛍️ Cart"): st.session_state.nav = "Cart"
        if st.sidebar.button("💳 Payment"): st.session_state.nav = "Payment"
        if st.sidebar.button("📦 My Orders"): st.session_state.nav = "My Orders"
        if st.sidebar.button("⚙️ Request Repair"): st.session_state.nav = "Request Repair"
        if st.sidebar.button("🔧 My Repairs"): st.session_state.nav = "My Repairs"
        if st.sidebar.button("📤 Sell Item"): st.session_state.nav = "Sell Item"
        if st.sidebar.button("📊 Sell Status"): st.session_state.nav = "Sell Status"
        if st.sidebar.button("✏️ Edit Profile"):st.session_state.nav = "Edit Profile"


    # STAFF
    elif user_role == "staff":
        st.sidebar.markdown("### 🧰 Staff Menu")
        if st.sidebar.button("🧭 Dashboard"): st.session_state.nav = "Dashboard"
        if st.sidebar.button("📦 Inventory"): st.session_state.nav = "Inventory"
        if st.sidebar.button("📥 Sell Requests"): st.session_state.nav = "Sell Requests"
        if st.sidebar.button("➕ Add to Inventory"): st.session_state.nav = "Add to Inventory"
        if st.sidebar.button("🔧 Repairs Management"): st.session_state.nav = "Repairs"
        if st.sidebar.button("🧾 Orders Management"): st.session_state.nav = "Orders Management"
        
        if st.sidebar.button("✏️ Edit Profile"):st.session_state.nav = "Edit Staff Profile"
       


   

    # COMMON
    st.sidebar.markdown("### Account")
    if st.sidebar.button("🔓 Logout"):
        st.session_state.user = None
        st.session_state.nav = "Login"
        st.success("You have been logged out.")


# ---------------------------
# PAGE FUNCTIONS
# ---------------------------
def home_page():
    st.header("🏠 Welcome to the Electronics Store!")
    st.write("Browse, buy, sell or repair your electronic items easily.")
    


import streamlit as st

def browse_items_page():
    st.title("🛒 Browse Items")

    # ---------- INITIALIZE CART ----------
    if "cart" not in st.session_state:
        st.session_state.cart = {}

    # ---------- FILTER BAR ----------
    brands = [r['Brand_Name'] for r in query("SELECT DISTINCT Brand_Name FROM Item WHERE Brand_Name IS NOT NULL")]
    categories = [r['Category'] for r in query("SELECT DISTINCT Category FROM Item WHERE Category IS NOT NULL")]

    brands = sorted(set([b for b in brands if b]))
    categories = sorted(set([c for c in categories if c]))

    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    brand = c1.selectbox("Brand", options=[""] + brands)
    category = c2.selectbox("Category", options=[""] + categories)
    min_price = c3.number_input("Min", min_value=0, value=0)
    max_price = c4.number_input("Max", min_value=0, value=200000)

    # ---------- QUERY ----------
    sql = """
    SELECT Item_ID, Brand_Name, Product_model_ID, Category,
           Price, Cond, Quantity_Avl, Status
    FROM Item
    WHERE Price BETWEEN %s AND %s
    """
    params = [min_price, max_price]

    if brand:
        sql += " AND Brand_Name=%s"
        params.append(brand)

    if category:
        sql += " AND Category=%s"
        params.append(category)

    items = query(sql, tuple(params))

    if not items:
        st.info("No items match your filters.")
        return

    # ---------- CSS FOR CARDS ----------
    st.markdown("""
        <style>
            .item-card {
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 15px;
                background: #ffffff;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                margin-bottom: 20px;
            }
            .item-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .item-sub {
                font-size: 14px;
                color: #666;
                margin-bottom: 10px;
            }
            .item-price {
                font-size: 18px;
                font-weight: bold;
                color: #1E90FF;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # ---------- GRID DISPLAY ----------
    cols = st.columns(3)
    for idx, item in enumerate(items):
        col = cols[idx % 3]  # Cycle through 3 columns
        with col:
            st.markdown(
                f"""
                <div class="item-card">
                    <div class="item-title">{item['Brand_Name']} — {item['Product_model_ID']}</div>
                    <div class="item-sub">{item['Category']} • {item['Cond']}</div>
                    <div class="item-price">₹ {item['Price']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if item['Quantity_Avl'] <= 0:
                st.button("🚫 Out of Stock", disabled=True, key=f"out_{item['Item_ID']}")
            else:
                qty = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=int(item['Quantity_Avl']),
                    value=1,
                    key=f"qty_{item['Item_ID']}"
                )

                if st.button("Add to Cart", key=f"add_{item['Item_ID']}"):
                    st.session_state.cart.setdefault(item['Item_ID'], 0)
                    st.session_state.cart[item['Item_ID']] += int(qty)
                    st.success(f"✅ Added {qty} x {item['Brand_Name']}")

    # ---------- SHOW CART ----------
    st.markdown("---")
    st.subheader("🛒 Your Cart")
    if st.session_state.cart:
        total = 0
        for item_id, qty in st.session_state.cart.items():
            it = next((x for x in items if x['Item_ID'] == item_id), None)
            if it:
                st.write(f"{it['Brand_Name']} — {it['Product_model_ID']} | Qty: {qty} | ₹{it['Price']} each")
                total += it['Price'] * qty
        st.write(f"**Total: ₹{total}**")
    else:
        st.info("Cart is empty.")


def cart_page():
    st.header("🛍️ My Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        return

    cart_items = []
    total = 0
    for item_id, qty in st.session_state.cart.items():
        item = query("SELECT * FROM Item WHERE Item_ID=%s", (item_id,))
        if item:
            it = item[0]
            subtotal = it['Price'] * qty
            total += subtotal
            cart_items.append([it['Item_ID'], it['Brand_Name'], it['Price'], qty, subtotal])
    df = pd.DataFrame(cart_items, columns=["Item ID", "Brand", "Price", "Qty", "Subtotal"])
    st.dataframe(df)
    st.subheader(f"Total Amount: ₹{total}")

    if st.button("Proceed to Payment"):
        st.session_state.nav = "Payment"
        st.rerun()



def payment_page():
    st.header("💳 Payment Page")
    if not st.session_state.cart:
        st.info("Your cart is empty.")
        return

    total = 0
    cart_details = []

    # Fetch latest stock & calculate total
    for item_id, qty in st.session_state.cart.items():
        item = query_one("SELECT Price, Quantity_Avl FROM Item WHERE Item_ID=%s", (item_id,))
        if not item:
            st.error(f"Item ID {item_id} not found. Skipping.")
            continue

        if qty > item['Quantity_Avl']:
            st.warning(f"Quantity for {item_id} exceeds available stock ({item['Quantity_Avl']}). Adjusting.")
            qty = item['Quantity_Avl']
            st.session_state.cart[item_id] = qty  # update cart to available qty

        subtotal = item['Price'] * qty
        total += subtotal
        cart_details.append((item_id, qty, item['Quantity_Avl']))

    st.subheader(f"Total Amount: ₹{total:.2f}")
    method = st.selectbox("Select Payment Method", ["Cash", "Credit Card", "Debit Card", "UPI", "Net Banking"])

    if st.button("Make Payment"):
        with st.spinner("Processing payment..."):
            time.sleep(2)

        # -----------------------------
        # Get correct Customer_ID
        # -----------------------------
        cust = query_one("SELECT Customer_ID FROM Customer WHERE user_id=%s", (st.session_state.user['id'],))
        if not cust:
            st.error("Customer record not found.")
            return
        customer_id = cust['Customer_ID']

        # -----------------------------
        # Insert Order
        # -----------------------------
        order_id = execute_with_lastrowid(
            "INSERT INTO Orders (CustomerID, Date, Status) VALUES (%s, %s, %s)",
            (customer_id, date.today(), "Completed")
        )

        if not order_id:
            st.error("❌ Payment failed — order not created.")
            return

        for item_id, qty, available in cart_details:
            if qty <= 0:
                continue

            # Insert into Contains
            execute("INSERT INTO Contains (OrderID, ItemID, Qty) VALUES (%s, %s, %s)", (order_id, item_id, qty))

            # Update quantity
            new_qty = available - qty
            new_status = "Available" if new_qty > 0 else "Sold"
            execute("UPDATE Item SET Quantity_Avl=%s, Status=%s WHERE Item_ID=%s", (new_qty, new_status, item_id))

        # Record payment
        execute("INSERT INTO Payment (Amount, Method, OrderID) VALUES (%s, %s, %s)", (total, method, order_id))

        st.success("✅ Payment Successful!")
        st.toast("Thank you for your purchase!", icon="💳")
        st.session_state.cart.clear()
        st.rerun()





def sell_item_page():
    st.title("Sell Item (Customer) — Submit a request")
    
    # Get actual Customer_ID
    cust = query_one("SELECT Customer_ID FROM Customer WHERE user_id=%s", (st.session_state.user['id'],))
    if not cust:
        st.error("Customer record not found.")
        return
    customer_id = cust['Customer_ID']

    with st.form("sell_form"):
        pmid = st.number_input("Product Model ID", min_value=1, step=1)
        desc = st.text_area("Description (condition, scratches, storage, etc.)")
        price = st.number_input("Expected Price", min_value=0.0, step=100.0)
        sdate = st.date_input("Sell Date", value=date.today())
        submitted = st.form_submit_button("Submit Sell Request")
    
    if submitted:
        ok = execute("""INSERT INTO CustomerSell 
                        (CustomerID, Product_model_ID, ItemDescription, SellDate, SellPrice, Status)
                        VALUES (%s, %s, %s, %s, %s, 'Pending')""",
                     (customer_id, pmid, desc, sdate, price))
        if ok:
            st.success("Sell request submitted (Pending).")
        else:
            st.error("Failed to submit sell request. Check DB constraints.")
            

def sell_status_page():
    st.title("My Sell Requests")

    # Get actual Customer_ID
    cust = query_one("SELECT Customer_ID FROM Customer WHERE user_id=%s", (st.session_state.user['id'],))
    if not cust:
        st.error("Customer record not found.")
        return
    customer_id = cust['Customer_ID']

    rows = query("""SELECT cs.CustomerID, cs.Product_model_ID, pm.Model_name, cs.ItemDescription, cs.SellDate, cs.SellPrice, cs.Status
                    FROM CustomerSell cs 
                    JOIN ProductModel pm ON cs.Product_model_ID = pm.Product_model_ID
                    WHERE cs.CustomerID=%s
                    ORDER BY cs.SellDate DESC""", (customer_id,))
    st.dataframe(rows)


def my_orders_page():
    st.title("My Orders")

    # Get the actual Customer_ID
    cust = query_one("SELECT Customer_ID FROM Customer WHERE user_id=%s", (st.session_state.user['id'],))
    if not cust:
        st.error("Customer record not found.")
        return
    customer_id = cust['Customer_ID']

    rows = query("""
        SELECT o.OrderID, o.Date, o.Status,
               GROUP_CONCAT(CONCAT(i.Item_ID,':',i.Brand_Name,':₹',i.Price) SEPARATOR ' | ') AS Items
        FROM Orders o
        JOIN Contains ct ON o.OrderID=ct.OrderID
        JOIN Item i ON ct.ItemID=i.Item_ID
        WHERE o.CustomerID=%s
        GROUP BY o.OrderID, o.Date, o.Status
        ORDER BY o.Date DESC
    """, (customer_id,))

    if rows:
        st.dataframe(rows)
    else:
        st.info("You have no orders yet.")



def request_repair_page():
    st.title("Request Repair")
    
    # Get correct Customer_ID from the Customer table
    cust = query_one("SELECT Customer_ID FROM Customer WHERE user_id=%s", (st.session_state.user['id'],))
    if not cust:
        st.error("Customer record not found.")
        return
    customer_id = cust['Customer_ID']

    # List customer's items (Info table) OR allow entering ItemID
    items = query("SELECT i.Item_ID, i.Brand_Name, i.Product_model_ID FROM Item i JOIN Info inf ON i.Item_ID=inf.ItemID WHERE inf.CustomerID=%s", (customer_id,))
    item_choices = {str(r['Item_ID']): r for r in items}
    options = [""] + list(item_choices.keys())
    item_id = st.selectbox("Select Item (owned by you) or leave blank and type ID below", options=options)
    custom_item_id = st.text_input("Or enter Item ID directly (optional)")
    issue = st.text_area("Describe the issue")
    est_cost = st.number_input("Estimated Acceptable Cost (optional)", min_value=0.0, value=0.0)
    
    if st.button("Submit Repair Request"):
        target_item_id = None
        if item_id:
            target_item_id = int(item_id)
        elif custom_item_id:
            try:
                target_item_id = int(custom_item_id)
            except:
                st.error("Invalid Item ID")
                return
        
        # Create Repair
        rid = execute_with_lastrowid(
            "INSERT INTO Repair (Issue, RepairCost, Status, ItemID, Staff_ID) VALUES (%s,%s,%s,%s,%s)",
            (issue, est_cost if est_cost>0 else None, "Pending", target_item_id, None)
        )
        if rid is None:
            st.error("Failed to create repair record.")
            return
        
        # Insert into RequestRepair using the correct Customer_ID
        if execute("INSERT INTO RequestRepair (CustomerID, RepairID) VALUES (%s,%s)", (customer_id, rid)):
            st.success(f"Repair request {rid} created successfully.")
        else:
            st.error("Failed to link repair request to customer.")




def my_repairs_page():
    st.title("My Repair Requests")
    
    # Get correct Customer_ID from the Customer table
    cust = query_one("SELECT Customer_ID FROM Customer WHERE user_id=%s", (st.session_state.user['id'],))
    if not cust:
        st.error("Customer record not found.")
        return
    customer_id = cust['Customer_ID']

    # Fetch repair requests for this customer
    rows = query("""
        SELECT r.RepairID, r.Issue, r.RepairCost, r.Status, r.ItemID, s.Name AS Technician
        FROM RequestRepair rr
        JOIN Repair r ON rr.RepairID = r.RepairID
        LEFT JOIN Staff s ON r.Staff_ID = s.Staff_ID
        WHERE rr.CustomerID = %s
    """, (customer_id,))
    
    if not rows:
        st.info("No repair requests found.")
        return

    st.dataframe(rows)


# ---------------------------
# Staff pages
# ---------------------------
def staff_dashboard_page():
    st.title("Staff Dashboard")

    # a) counts
    total_items = query_one("SELECT COUNT(*) AS c FROM Item")['c'] if query_one("SELECT COUNT(*) AS c FROM Item") else 0
    sold_items = query_one("SELECT COUNT(*) AS c FROM Item WHERE Status='Sold'")['c'] if query_one("SELECT COUNT(*) AS c FROM Item WHERE Status='Sold'") else 0
    in_repair = query_one("SELECT COUNT(*) AS c FROM Repair WHERE Status IS NOT NULL AND Status != 'Completed'")['c'] if query_one("SELECT COUNT(*) AS c FROM Repair WHERE Status IS NOT NULL AND Status != 'Completed'") else 0
    pending_sells = query_one("SELECT COUNT(*) AS c FROM CustomerSell WHERE Status='Pending'")['c'] if query_one("SELECT COUNT(*) AS c FROM CustomerSell WHERE Status='Pending'") else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Items", int(total_items))
    c2.metric("Sold Items", int(sold_items))
    c3.metric("Items In Repair", int(in_repair))
    c4.metric("Pending Sell Requests", int(pending_sells))

    st.markdown("---")
    # Items by Category
    by_cat = query("SELECT Category, COUNT(*) as cnt FROM Item GROUP BY Category")
    if by_cat:
        df_cat = pd.DataFrame(by_cat).set_index('Category')
        st.subheader("Items by Category")
        st.bar_chart(df_cat['cnt'])

    # Stock value per brand
    val_brand = query("SELECT Brand_Name as Brand, SUM(IFNULL(Price,0)*IFNULL(Quantity_Avl,0)) as stock_value FROM Item GROUP BY Brand_Name")
    if val_brand:
        df_val = pd.DataFrame(val_brand).set_index('Brand')
        st.subheader("Stock Value per Brand (₹)")
        st.bar_chart(df_val['stock_value'])

    # Orders per month (last 12 months)
    orders = query("SELECT Date FROM Orders WHERE Date IS NOT NULL")
    if orders:
        df_orders = pd.DataFrame(orders)
        df_orders['Date'] = pd.to_datetime(df_orders['Date'])
        df_orders['month'] = df_orders['Date'].dt.to_period('M')
        orders_per_month = df_orders.groupby('month').size().reset_index(name='count')
        orders_per_month['month'] = orders_per_month['month'].astype(str)
        st.subheader("Orders per Month")
        st.line_chart(pd.Series(data=orders_per_month['count'].values, index=orders_per_month['month']))



def inventory_page():
    st.title("📦 Inventory Management")

    def refresh_table():
        """Helper to get and show the latest inventory table."""
        rows = query("SELECT * FROM Item")
        st.subheader("All Items")
        st.dataframe(rows)

    refresh_table()  # Initial display

    st.markdown("---")

    # --- CREATE: Add New Item ---
    st.subheader("➕ Add New Item")
    with st.form("add_item_form"):
        brand = st.text_input("Brand Name")
        model_id = st.number_input("Product Model ID", min_value=1, step=1)
        category = st.text_input("Category")
        price = st.number_input("Price", min_value=0.0, step=0.01)
        cond = st.selectbox("Condition", ["Fair", "Good", "Like New", "Refurbished", "Excellent"])
        qty = st.number_input("Quantity Available", min_value=1, step=1, value=1)
        store_id = st.number_input("Store ID", min_value=1, step=1)
        submitted = st.form_submit_button("Add Item")

    if submitted:
        ok = execute("""
            INSERT INTO Item (Brand_Name, Product_model_ID, Category, Price, Cond, Quantity_Avl, Store_ID, Status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'Available')
        """, (brand, model_id, category, price, cond, qty, store_id))
        if ok:
            st.success("✅ New item added!")
            st.rerun()
        else:
            st.error("❌ Failed to add item.")

    st.markdown("---")

    # --- UPDATE: Update Item Details ---
    st.subheader("✏️ Update Item Details")
    iid = st.number_input("Enter Item ID to Update", min_value=1, step=1, key="upd_id")
    new_price = st.number_input("New Price", min_value=0.0, step=0.01, key="upd_price")
    new_status = st.selectbox("New Status", ["Available", "Sold", "In Repair", "Out of Stock", "Low Stock"], key="upd_status")
    if st.button("Update Item"):
        ok = execute("UPDATE Item SET Price=%s, Status=%s WHERE Item_ID=%s", (new_price, new_status, iid))
        if ok:
            st.success(f"✅ Item {iid} updated successfully.")
            st.rerun()
        else:
            st.error("❌ Failed to update item.")

    st.markdown("---")

    # --- DELETE: Delete Item ---
    st.subheader("🗑️ Delete Item")
    del_id = st.number_input("Enter Item ID to Delete", min_value=1, step=1, key="del_id")
    if st.button("Delete Item"):
        ok = execute("DELETE FROM Item WHERE Item_ID=%s", (del_id,))
        if ok:
            st.success(f"✅ Item {del_id} deleted successfully.")
            st.rerun()
        else:
            st.error("❌ Failed to delete item.")

    st.markdown("---")

    # --- RESTOCK: Add Quantity & Auto Status ---
    st.subheader("🔄 Restock Item")
    rid = st.number_input("Enter Item ID to Restock", min_value=1, step=1, key="restock_id")
    add_qty = st.number_input("Quantity to Add", min_value=1, step=1, key="restock_qty")
    if st.button("Restock Item"):
        ok = execute("UPDATE Item SET Quantity_Avl = Quantity_Avl + %s WHERE Item_ID=%s", (add_qty, rid))
        if ok:
            # Auto-update status based on new quantity
            new_qty = query_one("SELECT Quantity_Avl FROM Item WHERE Item_ID=%s", (rid,))['Quantity_Avl']
            new_status = "Available" if new_qty > 0 else "Out of Stock"
            execute("UPDATE Item SET Status=%s WHERE Item_ID=%s", (new_status, rid))
            st.success(f"✅ Item {rid} restocked. Current Quantity: {new_qty}, Status: {new_status}")
            st.rerun()
        else:
            st.error("❌ Failed to restock item.")

    st.markdown("---")

    # --- QUICK STATUS UPDATE ---
    st.subheader("⚡ Quick Update Status")
    col1, col2, col3 = st.columns(3)
    qid = col1.number_input("Item ID", min_value=1, step=1, key="quick_id")
    qstatus = col2.selectbox("Status", ["Available", "Sold", "In Repair", "Out of Stock", "Low Stock"], key="quick_status")
    if col3.button("Update Status"):
        if execute("UPDATE Item SET Status=%s WHERE Item_ID=%s", (qstatus, qid)):
            st.success("Item status updated successfully.")
            st.rerun()
        else:
            st.error("Failed to update item status.")

def add_to_inventory_page():
    st.title("Add Accepted Customer Item to Inventory (call stored procedure)")

    cust = st.number_input("Customer ID", min_value=1, step=1)
    pmid = st.number_input("Product Model ID", min_value=1, step=1)
    sid = st.number_input("Store ID", min_value=1, step=1, value=101)

    if st.button("Run Procedure"):
        try:
            conn = get_connection()
            if not conn:
                st.error("Database connection failed.")
                return
            cursor = conn.cursor()
            cursor.callproc('AddToInventoryFromCustomerSell', (int(cust), int(pmid), int(sid)))
            conn.commit()

            # Fetch any message returned by the stored procedure
            message = None
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    message = row[0]

            if message:
                if "added" in message.lower():
                    st.success(f"✅ {message}")
                elif "already" in message.lower():
                    st.warning(f"⚠️ {message}")
                else:
                    st.info(message)
            else:
                st.success("✅ Procedure executed successfully.")

        except Exception as e:
            st.error(f"❌ Error running stored procedure: {e}")
        finally:
            cursor.close()
            conn.close()
def sell_requests_page():
    st.title("Customer Sell Requests")
    rows = query("""SELECT cs.CustomerID, cs.Product_model_ID, pm.Model_name, cs.ItemDescription, cs.SellDate, cs.SellPrice, cs.Status, c.Name AS CustomerName
                    FROM CustomerSell cs
                    JOIN ProductModel pm ON cs.Product_model_ID = pm.Product_model_ID
                    LEFT JOIN Customer c ON cs.CustomerID = c.Customer_ID
                    ORDER BY cs.SellDate DESC""")
    st.dataframe(rows)
    st.markdown("**Approve or Reject a sell request**")
    c1, c2, c3 = st.columns(3)
    cust_id = c1.number_input("Customer ID", min_value=1, step=1)
    model_id = c2.number_input("Product Model ID", min_value=1, step=1)
    action = c3.selectbox("Action", ["Accept", "Reject"])
    if st.button("Submit Decision"):
        if action == "Accept":
            ok = execute("UPDATE CustomerSell SET Status='Accepted' WHERE CustomerID=%s AND Product_model_ID=%s", (cust_id, model_id))
            if ok:
                st.success("Sell request accepted")
            else:
                st.error("Failed to accept")
        else:
            ok = execute("UPDATE CustomerSell SET Status='Rejected' WHERE CustomerID=%s AND Product_model_ID=%s", (cust_id, model_id))
            if ok:
                st.success("Sell request rejected")
            else:
                st.error("Failed to reject")            


def repairs_management_page():
    st.title("Repairs Management")
    rows = query("SELECT r.RepairID, r.Issue, r.RepairCost, r.Status, r.ItemID, s.Name AS Technician FROM Repair r LEFT JOIN Staff s ON r.Staff_ID=s.Staff_ID ORDER BY r.RepairID DESC")
    st.dataframe(rows)
    st.markdown("**Assign / Update repair**")
    rid = st.number_input("Repair ID", min_value=1, step=1)
    tech = st.number_input("Assign Technician (Staff_ID)", min_value=1, step=1)
    new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"])
    if st.button("Update Repair"):
        ok = execute("UPDATE Repair SET Staff_ID=%s, Status=%s WHERE RepairID=%s", (int(tech), new_status, int(rid)))
        if ok:
            st.success("Repair updated")
        else:
            st.error("Failed to update repair")

def orders_management_page():
    st.title("Orders Management")

    def load_orders():
        """Load orders with customer names (case-insensitive handling)."""
        rows = query("""
            SELECT o.OrderID, o.Date, o.Status, c.Name AS CustomerName
            FROM Orders o
            LEFT JOIN Customer c ON o.CustomerID = c.Customer_ID
            ORDER BY o.Date DESC
        """)
        return rows

    rows = load_orders()
    st.dataframe(rows)

    st.markdown("**Mark Order Completed**")
    oid = st.number_input("Order ID to mark Completed", min_value=1, step=1)
    if st.button("Mark Completed"):
        if execute("UPDATE Orders SET Status='Completed' WHERE OrderID=%s", (oid,)):
            st.success("Order marked Completed")
            # reload the table to reflect changes immediately
            rows = load_orders()
            st.dataframe(rows)
        else:
            st.error("Failed to update order")

def edit_profile_page():
    st.header("📝 Edit Profile")

    user = st.session_state.user
    if not user:
        st.warning("⚠️ You must be logged in to edit profile.")
        return

    user_id = user['id']
    role = user['role']

    # Fetch current data
    if role == "customer":
        row = query_one("SELECT Name, Address FROM Customer WHERE user_id=%s", (user_id,))
        if not row:
            st.error("Customer record not found.")
            return
        name = st.text_input("Full Name", value=row['Name'])
        address = st.text_area("Address", value=row['Address'])
    else:  # staff
        row = query_one("SELECT Name, Contact, Store_ID FROM Staff WHERE user_id=%s", (user_id,))
        if not row:
            st.error("Staff record not found.")
            return
        name = st.text_input("Full Name", value=row['Name'])
        contact = st.text_input("Contact Number", value=row['Contact'])
        store_id = st.number_input("Store ID", min_value=1, step=1, value=row['Store_ID'])

    # Password change
    password = st.text_input("New Password (leave blank to keep current)", type="password")

    if st.button("Save Changes"):
        # Validation
        if not name or (role == "customer" and not address) or (role == "staff" and (not contact or not store_id)):
            st.warning("⚠️ Please fill all required fields.")
            return

        # Update users table if password or name changed
        if password:
            execute("UPDATE users SET name=%s, password=%s WHERE id=%s", (name, password, user_id))
        else:
            execute("UPDATE users SET name=%s WHERE id=%s", (name, user_id))

        # Update role-specific table
        if role == "customer":
            execute("UPDATE Customer SET Name=%s, Address=%s WHERE user_id=%s", (name, address, user_id))
        else:
            execute("UPDATE Staff SET Name=%s, Contact=%s, Store_ID=%s WHERE user_id=%s", (name, contact, store_id, user_id))

        st.success("✅ Profile updated successfully!")
        # Update session state
        st.session_state.user['name'] = name
    

def edit_staff_profile_page():
    st.header("📝 Edit Staff Profile")

    user = st.session_state.user
    if not user or user.get('role') != "staff":
        st.warning("⚠️ You must be logged in as staff to edit profile.")
        return

    user_id = user['id']

    # Fetch current staff info
    staff = query_one("SELECT Name, Contact, Store_ID FROM Staff WHERE user_id=%s", (user_id,))
    if not staff:
        st.error("Staff record not found.")
        return

    # Input fields pre-filled
    name = st.text_input("Full Name", value=staff['Name'])
    contact = st.text_input("Contact Number", value=staff['Contact'])
    store_id = st.number_input("Store ID", min_value=1, step=1, value=staff['Store_ID'])
    password = st.text_input("New Password (leave blank to keep current)", type="password")

    if st.button("Save Changes"):
        if not name or not contact or not store_id:
            st.warning("⚠️ All fields are required.")
            return

        # Update users table
        if password:
            execute("UPDATE users SET name=%s, password=%s WHERE id=%s", (name, password, user_id))
        else:
            execute("UPDATE users SET name=%s WHERE id=%s", (name, user_id))

        # Update staff-specific table
        execute("UPDATE Staff SET Name=%s, Contact=%s, Store_ID=%s WHERE user_id=%s", 
                (name, contact, store_id, user_id))

        st.success("✅ Profile updated successfully!")
        st.session_state.user['name'] = name




def register_page():
    st.header("📝 Register Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Select Role", ["customer", "staff"])  # only 2 roles

    if st.button("Register"):
        if not name or not email or not password:
            st.warning("⚠️ Please fill all fields.")
            return

        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            existing = cursor.fetchone()

            if existing:
                st.error("⚠️ Email already exists. Please use another email.")
            else:
                cursor.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                    (name, email, password, role)
                )
                conn.commit()
                st.success(f"✅ Account created successfully as **{role}**!")
                st.session_state.nav = "Login"
            conn.close()




def login_page():
    st.header("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not email or not password:
            st.warning("⚠️ Please fill all fields.")
            return

        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # ✅ Include id in the SELECT
            cursor.execute(
                "SELECT id, name, role FROM users WHERE email=%s AND password=%s",
                (email, password)
            )
            user = cursor.fetchone()

            if user:
                st.success(f"✅ Welcome back, {user['name']} ({user['role']})!")
                st.session_state.user = user
                st.session_state.role = user["role"]

                # Redirect to appropriate dashboard
                if user["role"] == "staff":
                    st.session_state.nav = "Dashboard"
                else:
                    st.session_state.nav = "Home"
            else:
                st.error("❌ Invalid email or password. Try again.")
            conn.close()







# ---------------------------
# MAIN CONTROLLER
# ---------------------------
def main():
    app_header()

    if not st.session_state.user:
        st.sidebar.title("Account")
        if st.sidebar.button("Login"): st.session_state.nav = "Login"
        if st.sidebar.button("Register"): st.session_state.nav = "Register"
        if st.session_state.nav == "Login": login_page()
        elif st.session_state.nav == "Register": register_page()
        return

    sidebar_menu()

    nav = st.session_state.nav
    if nav == "Home": home_page()
    elif nav == "Browse Items": browse_items_page()
    elif nav == "Cart": cart_page()
    elif nav == "Payment": payment_page()
    elif nav == "Sell Item": sell_item_page()
    elif nav == "Sell Status": sell_status_page()
    elif nav == "My Orders": my_orders_page()
    elif nav == "Request Repair": request_repair_page()
    elif nav == "My Repairs": my_repairs_page()
    elif nav == "Dashboard": staff_dashboard_page()
    elif nav == "Inventory": inventory_page()
    elif nav == "Sell Requests": sell_requests_page()
    elif nav == "Edit Profile": edit_profile_page()
    elif nav == "Edit Staff Profile":edit_staff_profile_page()
    elif nav == "Add to Inventory": add_to_inventory_page()
    elif nav == "Repairs": repairs_management_page()
    elif nav == "Orders Management": orders_management_page()
    elif nav == "Register": register_page()
    elif nav == "Login": login_page()
    else:
        home_page()


if __name__ == "__main__":
    main()


