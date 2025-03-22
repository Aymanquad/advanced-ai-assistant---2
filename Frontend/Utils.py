import os

def safe_file_read(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except:
        return ""

def safe_file_write(filepath, content):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except:
        return False

def GetMicrophoneStatus():
    return safe_file_read(os.path.join(os.getcwd(), "Frontend", "Files", "Mic.data"))

def SetMicrophoneStatus(Command):
    return safe_file_write(os.path.join(os.getcwd(), "Frontend", "Files", "Mic.data"), Command) 