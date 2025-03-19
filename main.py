from flask import Flask

app = Flask(__name__)

@app.get("/expenses")
def list_all_expenses():
    return "Hello"
