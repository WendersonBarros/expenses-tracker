import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2

load_dotenv()

app = Flask(__name__)
try:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
except:
    print("Could not connect to db")


@app.get("/expenses")
def list_all_expenses():
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM expenses")
        records = cur.fetchall()
        conn.commit()
        return jsonify({"data": records}), 200
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": "Failed to get expenses"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"message": "An unexpected error occurred"}), 500
    finally:
        cur.close()


@app.get("/expense/<int:expense_id>")
def list_expense_by_id(expense_id):
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT * FROM expenses
            WHERE id = %s""",
            (expense_id,),
        )
        return jsonify({"data": cur.fetchone()}), 200
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": "Failed to get the expense"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.post("/expense")
def create_expense():
    data = request.get_json()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO expenses
            (type, name, date, value, installments, installments_months)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                data["type"],
                data["name"],
                data["date"],
                data["value"],
                data["installments"],
                data["installments_months"],
            ),
        )
        conn.commit()
        return jsonify({"message": "Expense logged successfully"}), 201
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"error": "Failed to log expenses"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        cur.close()


@app.patch("/expense/<int:expense_id>")
def modify_expense(expense_id):
    data = request.get_json()
    cur = conn.cursor()
    try:
        allowed_keys = {
            "type",
            "name",
            "date",
            "value",
            "installments",
            "installments_months",
        }
        keys = ", ".join([f"{key} = %s" for key in data.keys() if key in allowed_keys])
        values = list(data.values()) + [expense_id]
        cur.execute(
            f"""UPDATE expenses
            SET {keys}
            WHERE id = %s
            RETURNING *""",
            (values),
        )
        result = cur.fetchone()
        conn.commit()
        return jsonify({"data": result}), 200
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": "Failed to upadate expense"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"message": "An unexpected error occurred"}), 500
    finally:
        cur.close()


@app.delete("/expense/<int:expense_id>")
def delete_expense(expense_id):
    cur = conn.cursor()
    try:
        cur.execute(
            """DELETE FROM expenses
            WHERE id = %s""",
            (expense_id,),
        )
        conn.commit()
        return jsonify({"message": "Expense deleted successfully"})
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": "Failed to delete expense"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"message": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8005)
