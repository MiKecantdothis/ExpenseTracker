# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import numpy as np

# Import functions and agents from other modules
import db_op as db
from Agents import analysis_agent, savings_agent

# --- Page Configuration ---
st.set_page_config(
    page_title="Boring Budget Buddy",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Main App Logic ---
def page_setup():
    """
    Page for initial user setup: monthly income and typical expenses.
    """
    st.header("How MUCH DO YOU MAKE?")
    st.write("Let's start with the basics. This will help understand your financial situation.")

    # Use session state to manage dynamic expense inputs
    if 'monthly_expenses' not in st.session_state:
        st.session_state.monthly_expenses = [{"name": "", "amount"}]

    # Capture income and store it in session state
    income = st.number_input("What is your total monthly income?", step=100.0, value=st.session_state.get('income'))
    st.session_state.income = income

    st.write("List your typical, recurring monthly expenses (e.g., Rent, Utilities, Insurance).")

    for i, expense in enumerate(st.session_state.monthly_expenses):
        cols = st.columns([3, 2])
        expense['name'] = cols[0].text_input(f"Expense Name {i+1}", value=expense['name'], key=f"name_{i}")
        expense['amount'] = cols[1].number_input(f"Amount {i+1}", value=expense['amount'], step=10.0, key=f"amount_{i}")

    st.markdown("---") # Visual separator

    # --- Action Buttons ---
    col1, col2, _ = st.columns([1, 1, 3]) # Use columns to place buttons side-by-side

    with col1:
        if st.button("Save Initial Setup"):
            # Filter out empty expenses
            valid_expenses = [exp for exp in st.session_state.monthly_expenses if exp['name'] and exp['amount'] > 0]
            if not valid_expenses:
                st.warning("Please enter at least one monthly expense.")
            else:
                _, error = db.add_monthly_expenses(valid_expenses)
                if error:
                    st.error(f"Failed to save expenses: {error}")
                else:
                    st.success("Your financial snapshot has been saved!")
                    st.info("Navigate to the 'Dashboard & AI Assistant' page to track spending and get insights.")
    with col2:
        if st.button("Add Another Expense"):
            st.session_state.monthly_expenses.append({"name": "", "amount"})
            st.rerun()

def page_dashboard():
    """
    Page for visualizing data and interacting with the AI assistant.
    """
    st.header("Dashboard")
    st.write("Track your day-to-day spending and chat with your financial AI for insights.")

    # Fetch data first
    df_current = db.get_current_expenses_df()
    df_monthly = db.get_monthly_expenses_df()
    income = st.session_state.get('income')

    # --- Spending Rate Cards ---
    st.subheader("📈 Daily Spending Overview")
    if income == 0:
        st.warning("Please set your monthly income in the 'Initial Setup' page to see your spending overview.")
    else:
        recommended_rate = (income - df_monthly['amount'].sum()) / 30
        current_sum = df_current['amount'].sum() if not df_current.empty else 0
        current_rate = current_sum / 30

        col1, col2 = st.columns(2)
        col1.metric("Recommended Daily Spending", f"₹{recommended_rate:,.2f}")
        col2.metric("Current Daily Spending Rate", f"₹{current_rate:,.2f}", delta=f"₹{(recommended_rate - current_rate):,.2f}",
                    help="Shows difference between recommended and current spending. Negative is over budget.")


    st.markdown("---") # Visual separator

    # --- Segment 1: Add/Edit Expenses and Visualizations ---
    st.subheader("📊 Your Daily Spending Patterns")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.write("**Add a New Expense**")
        with st.form("expense_form", clear_on_submit=True):
            exp_name = st.text_input("Expense Name (e.g., Coffee, Movie Tickets)")
            exp_amount = st.number_input("Amount", step=0.5)
            submitted = st.form_submit_button("Add Expense")

            if submitted:
                if not exp_name:
                    st.warning("Please enter an expense name.")
                else:
                    _, error = db.add_or_edit_expense(exp_name, exp_amount)
                    if error:
                        st.error(f"Failed to add expense: {error}")
                    else:
                        st.success(f"Added '{exp_name}' to your expenses.")
                        st.rerun()


    with col2:
        if df_current.empty:
            st.info("Your spending charts will appear here once you add some expenses.")
        else:
            # Visualization tabs
            tab1, tab2 = st.tabs(["Everyday Spending", "Monthly Expense Distribution"])

            with tab1:
                # Pie chart for spending categories
                fig_pie = px.pie(df_current, names='name', values='amount', title='Spending by Category')
                st.plotly_chart(fig_pie, use_container_width=True)

            with tab2:
                # Histogram for expense distribution
                fig_hist = px.histogram(df_monthly, x='name',y = 'amount', nbins=20, title='Distribution of Monthly Expense Amounts')
                fig_hist.update_layout(xaxis_title="Expense", yaxis_title="Expense Amount (₹)")
                st.plotly_chart(fig_hist, use_container_width=True)


    st.markdown("---") # Visual separator

    # --- Segment 2: AI Chatbot Interface ---
    st.subheader("How Money Save?")
    st.write("Bot Knows How Money Save")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("e.g., 'How much did I spend on food?' or 'Suggest ways to save.'"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("Thinking..."):
                # Decide which agent to use based on prompt
                if "save" in prompt.lower() or "tip" in prompt.lower() or "suggest" in prompt.lower():
                    # Use savings agent
                    df_monthly = db.get_monthly_expenses_df()
                    full_response = savings_agent.suggest(income, df_monthly, df_current)
                else:
                    # Use analysis agent
                    full_response = analysis_agent.analyze(df_current, prompt)

            message_placeholder.markdown(full_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


# --- Main Application Navigator ---
def main():
    """
    The main function that runs the Streamlit app and handles page navigation.
    """
    with st.sidebar:
        selected = option_menu(
            "Main Menu",
            ["Initial Setup", "Where Money Go"],
            icons=['gear', 'bar-chart-line'],
            menu_icon="cast",
            default_index=0
        )

    if selected == "Initial Setup":
        page_setup()
    elif selected == "Where Money Go":
        page_dashboard()

if __name__ == "__main__":
    # Before running the app, ensure the database tables are ready
    db.setup_database()
    main()




