from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome. options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables from the .env file.
env_vars=dotenv_values(".env")

# Ensure the Data directory exists
data_dir = os.path.join(os.getcwd(), "Data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Add error handling for environment variables
InputLanguage = os.getenv("Input_Language", "en-US")  # Provide a default value

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''


HtmlCode = str(HtmlCode).replace("recognition.lang = '';" , f"recognition.lang = '{InputLanguage}';")

# Fix the file path for writing the HTML file
current_dir = os.getcwd()
html_file_path = os.path.join(current_dir, "Data", "Voice.html")

with open(html_file_path, "w") as f:
    f.write(HtmlCode)

# Fix the Link variable to use the correct path
Link = html_file_path.replace("\\", "/")  # Convert Windows path to URL format

# Set Chrome options for the WebDriver.
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
chrome_options.add_argument("--disable-extensions")  # Disable extensions
chrome_options.add_argument("--disable-logging")  # Disable logging
chrome_options.add_argument("--log-level=3")  # Only show fatal errors
chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Allow microphone access without prompts
chrome_options.add_argument("--use-fake-device-for-media-stream")  # Use fake media device

# Remove the user agent setting as it's not necessary
# Remove unused browser tabs/processes when done
chrome_options.add_experimental_option("detach", False)
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
# Define the path for temporary files. I

TempDirPath =rf"{current_dir}/Frontend/Files"

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    if not Query or Query.isspace():  # Check if Query is empty or only whitespace
        return ""
        
    new_query = Query.lower().strip()
    query_words = new_query.split()
    
    if not query_words:  # Check if there are any words after splitting
        return ""
        
    question_words = ['how', 'what','who','where','when','why','which','whose','whom','can you',"what's","where's","how's","are you","is there"]

    # Check if the query starts with a question word
    if any(new_query.startswith(word) for word in question_words):
        if not new_query.endswith('?'):
            new_query = new_query + '?'
    else:
        if not new_query.endswith('.'):
            new_query = new_query + '.'

    return new_query.capitalize()

def UniversalTranslator(Text):
    eng_translation = mt.translate(Text, "en", "auto")
    return eng_translation.capitalize()

def SpeechRecognition():
    try:
        driver.get("file:///" + Link)
        driver.implicitly_wait(5)
        
        start_button = driver.find_element(by=By.ID, value="start")
        start_button.click()
        
        # Add a wait loop to give time for speech recognition
        max_attempts = 30  # Maximum number of attempts (30 * 0.5 seconds = 15 seconds max wait)
        attempts = 0
        
        while attempts < max_attempts:
            Text = driver.find_element(by=By.ID, value="output").text
            if Text.strip():  # Only proceed if we have non-empty text
                driver.find_element(by=By.ID, value="end").click()
                
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
                    
            attempts += 1
            time.sleep(0.5)  # Wait half a second before checking again
            
        raise TimeoutError("No speech detected within timeout period")
        
    except Exception as e:
        print(f"Error during speech recognition: {str(e)}")
        raise
    finally:
        # Make sure to close any remaining browser windows
        try:
            driver.execute_script("window.onbeforeunload = null")
        except:
            pass

if __name__ == "__main__":
    try:
        while True:
            Text = SpeechRecognition()
            print(Text)
    finally:
        driver.quit()  # Ensure the browser is closed when the script ends
