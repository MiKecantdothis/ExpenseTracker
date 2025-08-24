# agent.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
from dotenv import load_env  
load_env()
google_api = os.getenv('GEMINI_API')


llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=google_api)


class ExpenseAnalysisAgent:
    """
    An agent that analyzes expense data and answers user questions.
    """
    def __init__(self):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=['expenses_data', 'question'],
            template="""
            You are an expert financial analyst. Here is a summary of recent expenses:
            {expenses_data}

            Please answer the following question based on this data:
            Question: {question}

            Provide a clear and concise answer.
            """
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def analyze(self, expenses_df: pd.DataFrame, question: str) -> str:
        """
        Analyzes the provided expense data to answer a user's question.

        Args:
            expenses_df: A pandas DataFrame of the user's current expenses.
            question: The user's question.

        Returns:
            A string containing the agent's answer.
        """
        if self.chain is None:
            return "LLM Agent not initialized. Please check your API key."
        if expenses_df.empty:
            return "There is no expense data to analyze yet. Please add some expenses first."

        # Convert dataframe to a string format suitable for the LLM
        expenses_data_str = expenses_df.to_string(index=False)

        try:
            # The invoke method now directly returns the string output due to StrOutputParser
            response = self.chain.invoke({
                'expenses_data': expenses_data_str,
                'question': question
            })
            print(f"LLM Response: {response}") # For debugging
            return response
        except Exception as e:
            print(f"Error during analysis: {e}")
            return f"Sorry, I encountered an error: {e}"


class SavingsSuggestionAgent:
    """
    An agent that suggests ways to save money based on expense data.
    """
    def __init__(self):
        self.llm = llm
        self.prompt_template = PromptTemplate(
            input_variables=['income', 'monthly_expenses', 'current_expenses'],
            template="""
            You are a helpful financial advisor. A user needs help saving money.
            Here is their financial situation:
            - Monthly Income: ${income}
            - Typical Monthly Expenses (e.g., rent, utilities):
            {monthly_expenses}
            - Recent Discretionary Spending:
            {current_expenses}

            Based on this information, please provide 3-5 actionable and personalized tips on how they can save money.
            Focus on the discretionary spending first. Be encouraging and non-judgmental.
            """
        )
        self.chain = self.prompt_template | self.llm | StrOutputParser()

    def suggest(self, income: float, monthly_df: pd.DataFrame, current_df: pd.DataFrame) -> str:
        """
        Generates savings suggestions.

        Args:
            income: The user's monthly income.
            monthly_df: DataFrame of typical monthly expenses.
            current_df: DataFrame of current discretionary expenses.

        Returns:
            A string with savings suggestions.
        """
        if self.chain is None:
            return "LLM Agent not initialized. Please check your API key."
        if current_df.empty:
            return "I need some current expense data to give you the best advice. Try adding a few expenses first!"

        monthly_expenses_str = monthly_df.to_string(index=False)
        current_expenses_str = current_df.to_string(index=False)

        try:
            # The invoke method now directly returns the string output due to StrOutputParser
            response = self.chain.invoke({
                'income': income,
                'monthly_expenses': monthly_expenses_str,
                'current_expenses': current_expenses_str
            })
            print(f"LLM Response: {response}") # For debugging
            return response
        except Exception as e:
            print(f"Error generating suggestions: {e}")
            return f"Sorry, I encountered an error: {e}"

# Instantiate the agents for use in the main app
analysis_agent = ExpenseAnalysisAgent()

savings_agent = SavingsSuggestionAgent()
