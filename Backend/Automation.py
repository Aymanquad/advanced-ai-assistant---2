from AppOpener import close, open as appopen 
from webbrowser import open as webopen
from pywhatkit import search, playonyt 
from dotenv import dotenv_values
from bs4 import BeautifulSoup 
from rich import print 
from groq import Groq 
import webbrowser 
import keyboard
import subprocess 
import requests
import asyncio 
import os 


env_vars=dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")



# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTK00 SY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
"IZ6rdc", "05uR6d LTK00", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
"LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Grog client with the API key.
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses for user interactions.
professional_responses = [
"Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
"I'm at your service for any additional questions or support you may need-don't hesitate to ask." ]

messages = []

SystemChatBot =[{"role": "system", "content": f"Hello, I am ${os.environ['Username']}, You're a content writer. You have to write content like letters, code , application , essays, notes, songs ,poems, etc."}]


def GoogleSearch(Topic):
    search(Topic) # Using pywhatkit's search function to perform a Google search.
    return True 

def Content(Topic):

    def OpenNotepad(File): 
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File]) 

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"}) # Add the user's prompt to messages,
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=SystemChatBot + messages, 
            max_tokens= 2048, 
            temperature=0.7,
            top_p=1, 
            stream=True, 
            stop=None
        )

        Answer = "" 

        for chunk in completion:
            if chunk.choices[0].delta.content: 
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "") 
        messages.append({"role": "assistant", "content": Answer}) 
        return Answer
    

    Topic: str = Topic.replace("Content ", "") 
    ContentByAI = ContentWriterAI(Topic) # Generate content using AI.

    with open(rf"Data\{Topic. lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()

    OpenNotepad(rf"Data\{Topic. lower().replace(' ','')}.txt")
    return True

#Content("request to cse staff for hackathon conduction by GDG coming month")



def YouTubeSearch(Topic):
    Url4Search =  f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search) # Open the search URL in a web browser.
    return True 


def PlayYoutube(query):
    playonyt(query) # Use pywhatkit's playonyt function to play the video.
    return True 

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    
    except:
        search_query = f"{app} official website"
        
        try:
            # Use a more browser-like request
            url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"
            }
            
            response = sess.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Print the response text to debug
            print("Response status:", response.status_code)
            print("Response text preview:", response.text[:500])
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # First try: Look for search result links with cite tags (usually contains the URL)
            results = soup.find_all('cite')
            if results:
                for cite in results:
                    url = cite.text.strip()
                    if url and ('http' in url or 'www' in url):
                        final_url = url if url.startswith('http') else f'https://{url}'
                        print(f"Found URL from cite: {final_url}")
                        webopen(final_url)
                        return True
            
            # Second try: Look for any valid links
            all_links = soup.find_all('a')
            for link in all_links:
                href = link.get('href', '')
                # Look for URLs in the Google redirect format
                if href.startswith('/url?q='):
                    actual_url = requests.utils.unquote(href.split('/url?q=')[1].split('&')[0])
                    if 'google' not in actual_url and actual_url.startswith('http'):
                        print(f"Found URL from redirect: {actual_url}")
                        webopen(actual_url)
                        return True
            
            # If everything fails, try a direct approach with common URLs
            common_formats = [
                f"https://www.{app}.com",
                f"https://{app}.com",
                f"https://www.{app}.org",
                f"https://{app}.org"
            ]
            
            for url in common_formats:
                try:
                    test_response = sess.head(url, timeout=5)
                    if test_response.status_code == 200:
                        print(f"Found working URL: {url}")
                        webopen(url)
                        return True
                except:
                    continue
            
            # Last resort: open the search page
            print("No direct links found, opening search page")
            webopen(url)
            return True
                
        except Exception as e:
            print(f"Error searching for {app}: {str(e)}")
            fallback_url = f"https://www.google.com/search?q={requests.utils.quote(app)}"
            webopen(fallback_url)
            return True

#OpenApp("linkedin")
    

def CloseApp(app):
    if "chrome" in app:
        pass # Skip if the app is Chrome. (cuz we need that in speechtotext.py)
    else:
        try:
            close(app, match_closest =True, output=True, throw_error=True)
            return True 
        except:
            return False 
                
def System(command):
    def mute():
        keyboard.press_and_release("volume mute") # Simulate the mute key press.

    def unmute():
        keyboard.press_and_release("volume unmute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    if command=="mute":
        mute()
    elif command=="unmute":
        unmute()
    elif command=="volume up":
        volume_up()
    else :
        volume_down()


async def TranslateAndExecute(commands: list[str]):
    funcs = [] # List to store asynchronous tasks.
    for command in commands:
        if command.startswith("open "): 
            if "open it" in command: 
                pass
            if "open file" == command: 
                pass 
            else:
                fun = asyncio.to_thread (OpenApp, command.removeprefix("open ")) # Schedule app opening.
                funcs.append(fun)
        elif command.startswith("general"): # Placeholder for general commands.
            pass
        elif command.startswith("realtime "): # Placeholder for real time commands.
            pass
        elif command.startswith("close"): # Handle "close" commands.
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close")) # Schedule app closing.
            funcs.append(fun)
        elif command.startswith("play"): # Handle "play" commands.
            fun = asyncio.to_thread (PlayYoutube, command.removeprefix("play ")) # Schedule YouTube playbach.
            funcs.append(fun)
        elif command.startswith("content"): # Handle "content" commands.                                            cant seem to call all the time unless written content
            fun = asyncio.to_thread (Content, command.removeprefix("content")) # Schedule content creation
            funcs.append(fun)
        elif command.startswith("google search "): # Handle Google search commands.
            fun = asyncio.to_thread (GoogleSearch, command.removeprefix("google search ")) # Schedule Google search.
            funcs.append(fun)
        elif command.startswith("youtube search "): # Handle YouTube search commands.
            fun = asyncio.to_thread (YouTubeSearch, command.removeprefix("youtube search ")) # Schedule YouTube search.
            funcs.append(fun)
        elif command.startswith("system "): # Handle system commands.
            fun = asyncio.to_thread (System, command.removeprefix("system ")) # Schedule system command.
            funcs.append(fun)
        else:
            print("No Function Found. For {command}")

    results = await asyncio.gather(*funcs) # Execute all tasks concurrently.

    for result in results: 
        if isinstance(result, str):
            yield result
        else:
            yield result


async def Automation (commands: list[str]):
    async for result in TranslateAndExecute(commands): # Translate and execute commands.
        pass
    return True

if __name__ == "__main__":
    asyncio.run(Automation(["close discord","play nasheed mix","open settings","content request to cse staff for hackathon conduction by GDG coming month"]))
