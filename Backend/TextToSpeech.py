import pygame 
import random 
import asyncio
import edge_tts 
import os 
from dotenv import dotenv_values 


env_vars=dotenv_values(".env")
AssistantVoice = os.getenv("Assistant_Voice") 


async def TextToAudioFile(text) -> None:
    file_path = "Data\speech.mp3" # Define the path where the speech file will be saved
    if os.path.exists(file_path):
        os.remove(file_path) 

    # Create the communicate object to generate speech
    communicate = edge_tts.Communicate(text,AssistantVoice, pitch='+5Hz', rate = '+13%')
    await communicate.save(r'Data\speech.mp3') # Save the generated speech as an MP3 file


# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text,func=lambda r=None: True):
    while True:
        try:
            asyncio.run(TextToAudioFile(Text))

            pygame.mixer.init()

            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if func() == False:
                    break
                pygame.time.Clock().tick(10)

            return True
        
        except Exception as e:
            print("error habibi is .." ,e)

        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()

            except Exception as e :
                print('Error in the final block habibi..' ,e)

if __name__ == "__main__":
    while True:
        TTS(input("Enter your text :"))