import os
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from googlesearch import search as gsearch


env_vars = dotenv_values(".env")
Username = os.getenv("Username")
Assistantname = os.getenv("Assistantname")
GroqAPIKey = os.getenv("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""


SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "How can i  help you ?"}
]

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
        
except FileNotFoundError :
    with open(r"Data\ChatLog.json", "w") as f:
        dump([] ,f)


def GoogleSearch(query): 
    # Add delay between requests to avoid blocking
    results = list(gsearch(
        query,
        advanced=True,
        num_results=5,
        lang="en",
    ))
    
    # if not results:
    #     print("Warning: No search results found")
    #     return f"No results found for query: {query}"
        
    Answer = f"The search results for '{query}' are:\n[start]\n"
    
    for i in results:
        Answer += f"Title : {i.title} \n Description: {i.description} \n"
        
    Answer += "[end]"
    #print(Answer)
    return Answer


def RealtimeInformation():
    current_time = datetime.datetime.now()
    day = current_time.strftime("%A")
    date = current_time.day
    month = current_time.strftime("%B")
    year = current_time.year
    hour = current_time.hour
    minute = current_time.minute
    second = current_time.second


    data = (
        f"Please use this real-time information if needed,\n"
        f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
        f"Time: {hour} hours : {minute} minutes : {second} seconds"
    )
    return data

def AnswerModifier(Answer):
    lines = Answer.split('/n') 
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '/n'.join(non_empty_lines)
    return modified_answer

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    messages.append({"role": "user", "content": f"{prompt}"})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
        max_tokens=1024,
        temperature=0.7,
        top_p=1, 
        stream=True, 
        stop=None 
    )

    Answer = ""


    for chunk in completion:
        if chunk.choices[0].delta.content: # Check if there's content in the current chunk.
            Answer += chunk.choices[0].delta.content # Append the content to the answer.

    Answer = Answer.strip().replace("</s>", "") # Clean up any unwanted tokens from the response.

    # Append the chatbot's response to the messages list.
    messages.append({"role": "assistant", "content": Answer})

    # Save the updated chat log to the JSON file. (to remember chat history)
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    # Return the formatted response.
    return AnswerModifier(Answer=Answer) 




if __name__ == "__main__":
    while True:
        prompt = input("Enter Your query  : ") # Prompt the user for a question.
        print(RealtimeSearchEngine(prompt)) # Call the RealtimeSearchEngine function and print its response.