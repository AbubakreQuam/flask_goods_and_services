from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import streamlit as st

app = Flask(__name__)
CORS(app)  # Allow all origins for simplicity

connection_database_key = st.secrets["connection_database_secret"]
os.environ["connection_database_secret"] = connection_database_key

# Database connection helper
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password=connection_database_key,
            database="goods_db"
        )
    except Error as e:
        return None

# Routes
@app.route("/goods", methods=["GET"])
def get_goods():
    search = request.args.get("search")
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)

    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = db.cursor(dictionary=True)
        query = "SELECT id, name, status FROM goods"
        params = []

        if search:
            query += " WHERE name LIKE %s"
            params.append(f"%{search}%")

        query += " ORDER BY id LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        #goods = cursor.fetchall()
        goods =[{"id":1,"name":"Milk","status":"unlocked"},{"id":2,"name":"Bread","status":"locked"},{"id":3,"name":"Cheese","status":"locked"},{"id":4,"name":"Coca-Cola Can","status":"unlocked"},{"id":5,"name":"Pepsi Bottle","status":"locked"},{"id":6,"name":"Lay’s Classic Chips","status":"unlocked"},{"id":7,"name":"Snickers Bar","status":"locked"},{"id":8,"name":"Orange Juice","status":"unlocked"},{"id":9,"name":"Whole Milk 1L","status":"unlocked"},{"id":10,"name":"Oreo Cookies","status":"unlocked"},{"id":11,"name":"Red Bull Energy","status":"locked"},{"id":12,"name":"Bottled Water","status":"unlocked"},{"id":13,"name":"Sprite Zero","status":"locked"},{"id":14,"name":"Rice 1kg","status":"unlocked"},{"id":15,"name":"Pasta Penne","status":"locked"},{"id":16,"name":"Olive Oil 500ml","status":"unlocked"},{"id":17,"name":"Frozen Pizza","status":"locked"},{"id":18,"name":"Cheddar Cheese","status":"unlocked"},{"id":19,"name":"Yogurt Cup","status":"locked"},{"id":20,"name":"Apple Pack (6)","status":"unlocked"},{"id":21,"name":"Banana Bunch","status":"locked"},{"id":22,"name":"Chocolate Muffin","status":"unlocked"},{"id":23,"name":"Iced Tea Bottle","status":"locked"}]

        return jsonify(goods)
    except Error:
        return jsonify({"error": "Failed to fetch goods."}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/lock", methods=["POST"])
def lock_good():
    data = request.get_json()
    good_id = data.get("id")
    status = data.get("status", "").lower()

    if status not in {"locked", "unlocked"}:
        return jsonify({"error": "Invalid status. Use 'locked' or 'unlocked'."}), 400

    db = get_db_connection()
    if not db:
        return jsonify({"error": "Database connection failed."}), 500

    try:
        cursor = db.cursor()
        cursor.execute(
            "UPDATE goods SET status = %s WHERE id = %s",
            (status, good_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Good not found."}), 404
        db.commit()
        return jsonify({"message": f"Good {good_id} status set to {status}."})
    except Error:
        return jsonify({"error": "Failed to update status."}), 500
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode, use_reloader=False)

