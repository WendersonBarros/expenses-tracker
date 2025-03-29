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


def format_response(values_arr, column_names):
    if len(values_arr) == 0:
        return []

    formatted_values = []
    values = values_arr[0]
    values_dict = {}
    for index in range(len(values)):
        values_dict[column_names[index].name] = values[index]

    if values_dict:
        formatted_values.append(values_dict)

    if len(values_arr) > 1:
        formatted_values += format_response(values_arr[1:], column_names)

    return formatted_values


def group_all_expenses_by_month_year(expenses):
    if len(expenses) == 0:
        return {}

    expenses_by_month_year = {}
    for expense in expenses:
        if expense["installments"] is False:
            month_year = f"{expense["date"].month}/{expense["date"].year}"
            if month_year not in expenses_by_month_year:
                expenses_by_month_year[month_year] = {"total": 0, "expenses": []}

            expenses_by_month_year[month_year]["total"] += expense["value"]
            expenses_by_month_year[month_year]["expenses"].append(expense)

        for date in expense["installments_months"]:
            if date not in expenses_by_month_year:
                expenses_by_month_year[date] = {"total": 0, "expenses": []}

            expenses_by_month_year[date]["total"] += round(
                expense["value"] / len(expense["installments_months"]), 2
            )
            expenses_by_month_year[date]["expenses"].append(expense)

    return expenses_by_month_year


def group_expenses_by_month_year(expenses, month_year):
    if len(expenses) == 0 or len(month_year) == 0:
        return {}

    expenses_by_month_year = {"date": month_year, "total": 0, "expenses": []}
    for expense in expenses:
        if expense["installments"] is False:
            expenses_by_month_year["total"] += expense["value"]
            expenses_by_month_year["expenses"].append(expense)
        else:
            expenses_by_month_year["total"] += round(
                expense["value"] / len(expense["installments_months"]), 2
            )
            expenses_by_month_year["expenses"].append(expense)

    return expenses_by_month_year


@app.get("/expenses")
def list_all_expenses():
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM expenses")
        return jsonify({"data": format_response(cur.fetchall(), cur.description)}), 200
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

        result = cur.fetchone()
        if result is None:
            response = {}
        else:
            (response,) = format_response([result], cur.description)

        return (
            jsonify({"data": response}),
            200,
        )
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": "Failed to get the expense"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"message": "An unexpected error occurred"}), 500
    finally:
        cur.close()


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
        conn.commit()

        result = cur.fetchone()
        if result is None:
            response = {}
        else:
            (response,) = format_response([result], cur.description)

        return (
            jsonify({"data": response}),
            200,
        )
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
            WHERE id = %s
            RETURNING *""",
            (expense_id,),
        )
        conn.commit()

        response = cur.fetchone()
        if response is None:
            return jsonify({"message": "Nothing was deleted"}), 200

        return jsonify({"message": "Expense deleted successfully"}), 200
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return jsonify({"message": "Failed to delete expense"}), 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return jsonify({"message": "An unexpected error occurred"}), 500
    finally:
        cur.close()


@app.get("/monthly_expenses")
def list_all_expenses_by_month():
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM expenses")
        expenses = cur.fetchall()
        formatted_expenses = format_response(expenses, cur.description)
        return group_all_expenses_by_month_year(formatted_expenses), 200
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return {"message": "Failed to load monthly expenses"}, 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return {"message": "An unexpected error occurred"}, 500
    finally:
        cur.close()


@app.get("/monthly_expenses/<string:month_year>")
def list_expenses_by_month_year(month_year):
    month_year = month_year.replace("-", "/")
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT * FROM expenses
            WHERE (to_char(date, 'MM/YYYY') = %s AND installments = FALSE)
            OR %s = ANY(installments_months)""",
            (month_year, month_year),
        )
        expenses = cur.fetchall()
        formatted_expenses = format_response(expenses, cur.description), 200
        return group_expenses_by_month_year(formatted_expenses, month_year), 200
    except psycopg2.Error as err:
        print(f"Database error: {err}")
        return {"message": "Failed to load monthly expenses"}, 500
    except Exception as err:
        print(f"Unexpected error: {err}")
        return {"message": "An unexpected error occurred"}, 500
    finally:
        cur.close()


if __name__ == "__main__":
    app.run(debug=True, port=8005)
