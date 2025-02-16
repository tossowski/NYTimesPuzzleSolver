import nltk
from nltk.corpus import words
import argparse
import pyautogui
import win32gui
from ctypes import windll


#all_words = words.words()
all_words = []
with open('words.txt', "r") as f:
    for line in f:
        all_words.append(line.strip())
        
    

parser = argparse.ArgumentParser(description="Solve the NYT Spelling Bee puzzle.")
parser.add_argument("--center", help="The required center letter.")
parser.add_argument("--letters", help="All available letters (including center).")

args = parser.parse_args()
    
# Convert input to lowercase
center_letter = args.center.lower()
available_letters = args.letters.lower()
    
valid_words = []
    
for word in all_words:
    if len(word) < 4:
        continue
    word = word.lower()
    if center_letter not in word:
        continue
    
    valid = True
    for letter in word:
        if letter not in available_letters:
            valid = False
            break
    
    if valid:
        valid_words.append(word)

for word in valid_words:
    print(word)


def find_window_by_partial_title(partial_title):
    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if partial_title.lower() in title.lower():
                results.append(hwnd)
    
    results = []
    win32gui.EnumWindows(callback, results)
    return results[0] if results else None

hwnd = find_window_by_partial_title("Chrome")
if hwnd:
    win32gui.SetForegroundWindow(hwnd)
else:
    print("Window not found!")
    
for word in valid_words:
    pyautogui.write(word, interval=0.1)
    pyautogui.press('enter')
