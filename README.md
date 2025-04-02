# Expenses Tracker

A small API project to log and manage expenses using Flask and PostgreSQL.

## Description

Expenses Tracker is a simple REST API designed to help users track and manage their expenses. It allows users to log expenses, retrieve expense data, modify existing expenses, and categorize expenses by month and year. The application uses a PostgreSQL database and provides endpoints for CRUD operations.

## Requirements

- Docker
- Python 3
- The other dependencies are listed in `requirements.txt`

## Installation

1. Clone this repository:
   
   ```sh
   git clone https://github.com/WendersonBarros/expenses-tracker.git
   ```
2. Navigate to the project directory:
   
   ```sh
   cd expenses-tracker
   ```
3. Create a virtual environment:
   
   ```sh
   python3 -m venv env
   ```
4. Activate the virtual environment:
   
   ```sh
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```
5. Install the required dependencies:
   
   ```sh
   pip3 install -r requirements.txt
   ```
6. Start the PostgreSQL database using Docker:
   
   ```sh
   docker compose -f database/docker-compose.yaml up -d
   ```
7. Set up environment variables in a `.env` file (Copy the `.env.example` file):
   
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=expenses_db
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_password
   ```
8. Run the Flask application:
   
   ```sh
   python3 app.py
   ```

## Routes

### Expense Management

#### List all expenses
**GET** `/expenses`

- Retrieves all logged expenses.

#### Get an expense by ID
**GET** `/expense/<expense_id>`

- Retrieves a specific expense using its ID.

#### Create a new expense
**POST** `/expense`

- Logs a new expense.
- **Request Body (JSON):**
  ```json
  {
    "type": "food",
    "name": "Lunch",
    "date": "2025-04-01",
    "value": 15.50,
    "installments": true,
    "installments_months": ["04/2025"]
  }
  ```

#### Modify an existing expense
**PATCH** `/expense/<expense_id>`

- Updates specific fields of an expense.
- **Request Body (JSON):**
  ```json
  {
    "name": "Dinner",
    "value": 20.00
  }
  ```

#### Delete an expense
**DELETE** `/expense/<expense_id>`

- Deletes an expense by ID.

### Expense Summary by Month

#### Get all expenses grouped by month/year
**GET** `/monthly_expenses`

- Returns expenses grouped by month and year.

#### Get expenses for a specific month/year
**GET** `/monthly_expenses/<month_year>`

- Retrieves expenses for a given month and year (format: `MM-YYYY`).
