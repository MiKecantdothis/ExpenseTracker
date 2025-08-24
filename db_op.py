# database_operations.py

import os
from supabase import create_client, Client
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

# --- Supabase Connection ---
# It's recommended to use environment variables for your Supabase URL and Key
SUPABASE_URL=""
SUPABASE_KEY=""

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def setup_database():
    """
    This function is intended to be run once to ensure tables exist.
    In a real application, you would use Supabase's SQL editor or migrations.
    For this example, we'll just log a message.
    """
    print("Database setup: Ensure 'monthly_expenses' and 'current_expenses' tables exist.")
    print("Columns for 'monthly_expenses': name (text), amount (numeric)")
    print("Columns for 'current_expenses': name (text), amount (numeric), created_at (timestamp with time zone)")


def add_monthly_expenses(expenses: list[dict]):
    """
    Adds a list of typical monthly expenses to the 'monthly_expenses' table.
    It first clears the existing expenses to avoid duplicates on re-submission.

    Args:
        expenses: A list of dictionaries, where each dict has 'name' and 'amount'.
    """
    if not supabase:
        print("Supabase client not initialized.")
        return None, "Supabase client not initialized."

    try:
        # Clear existing monthly expenses to start fresh
        supabase.table('monthly_expenses').delete().neq('name', 'dummy_value_to_delete_all').execute()

        # Insert new expenses
        data, error = supabase.table('monthly_expenses').insert(expenses).execute()
        if error and error[1]:
            raise Exception(error[1])
        return data, None
    except Exception as e:
        print(f"Error adding monthly expenses: {e}")
        return None, str(e)

def add_or_edit_expense(name: str, amount: float, expense_id: int = None):
    """
    Adds a new expense or updates an existing one in the 'current_expenses' table.

    Args:
        name: The name of the expense.
        amount: The amount of the expense.
        expense_id: The ID of the expense to update. If None, a new expense is added.
    """
    if not supabase:
        print("Supabase client not initialized.")
        return None, "Supabase client not initialized."

    expense_data = {'name': name, 'amount': amount}
    try:
        if expense_id:
            # Update existing expense
            data, error = supabase.table('current_expenses').update(expense_data).eq('id', expense_id).execute()
        else:
            # Add new expense
            data, error = supabase.table('current_expenses').insert(expense_data).execute()

        if error and error[1]:
            raise Exception(error[1])
        return data, None
    except Exception as e:
        print(f"Error adding/editing expense: {e}")
        return None, str(e)

def get_current_expenses_df():
    """
    Retrieves all expenses from the 'current_expenses' table.

    Returns:
        A pandas DataFrame containing the expenses.
    """
    if not supabase:
        print("Supabase client not initialized.")
        return pd.DataFrame()

    try:
        response = supabase.table('current_expenses').select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error retrieving current expenses: {e}")
        return pd.DataFrame()

def get_monthly_expenses_df():
    """
    Retrieves all expenses from the 'monthly_expenses' table.

    Returns:
        A pandas DataFrame containing the typical monthly expenses.
    """
    if not supabase:
        print("Supabase client not initialized.")
        return pd.DataFrame()

    try:
        response = supabase.table('monthly_expenses').select("*").execute()
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error retrieving monthly expenses: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    # This block can be used for initial setup and testing
    print("Running database setup...")
    setup_database()
   