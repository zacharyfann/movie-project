import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import SecretStr


def test_openai_connection():
    # Retrieve API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    # secret_api_key = SecretStr(str(api_key))
    # Initialize the ChatOpenAI client with your API key
    if api_key != None:
        chat = ChatOpenAI(api_key=api_key)

        messages = [
            ("system", "You are a knowledgeable assistant."),
            ("user", "How many floors does the Empire State Building have?")
        ]

        try:
            # Send the query to the OpenAI API
            response = chat.invoke(messages)

            # Print the response
            final_response =("Response:", response)
        except Exception as e:
            final_response =(f"An error occurred: {e}")
    return final_response