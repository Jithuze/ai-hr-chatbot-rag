import ollama
import sqlite3
import json

def summary(prompt):
    # Define the message with a system instruction
    system_message = {
        "role": "system",
        "content": "You are an AI who creates sqlite3 commands based on the user prompt and return output in format {'query' : ''}"
    }
    
    # User prompt as the second message
    user_message = {
        "role": "user",
        "content": f"User Prompt: {prompt}"
    }
    
    # Call the ollama chat with both system and user messages
    response = ollama.chat(
        model='stablelm-zephyr',
        messages=[system_message, user_message],  # Correct structure for messages
        stream=True,
        format='json'
    )

    
    
    # Print the response as it streams
    result = ""
    for chunk in response:
        result += chunk['message']['content']
        print(chunk['message']['content'], end='', flush=True)
    
    return result

# Example call to the function
result = summary("I have a table named mobile_prices, I want to get mobile_name whose price is lowest")
result = json.loads(result)
conn = sqlite3.connect('amazon_mobiles.db')
cursor = conn.cursor()

data = cursor.execute(result['query'])
data = data.fetchall()
print(data)