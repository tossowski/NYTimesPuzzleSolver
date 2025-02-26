import argparse
import pyautogui
import win32gui
from models.deepseek import DeepseekModel
from ctypes import windll

all_words = set()
with open('words.txt', "r", encoding='utf-8') as f:
    for line in f:
        all_words.add(line.strip().lower())
        
    

parser = argparse.ArgumentParser(description="Solve the NYT Spelling Bee puzzle.")
parser.add_argument("--center", help="The required center letter.")
parser.add_argument("--letters", help="All available letters (including center).")
parser.add_argument("--solver_type", help="Heuristic or AI", default='Heuristic')

args = parser.parse_args()
    
# Convert input to lowercase
center_letter = args.center.lower()
available_letters = args.letters.lower()


if args.solver_type == 'Heuristic':
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

    valid_words.sort()
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

else:
    model = DeepseekModel('deepseek-ai/DeepSeek-R1-Distill-Qwen-7B', 'cpu')
    prompt = f"""I need your help to solve the NYTimes Spelling Bee. The objective is to make as many valid words as possible using the letters I provide. Additionally, each word must use the center letter which I will also provide.\nThe letters are {','.join(args.letters)}.\nThe center letter is {args.center}.\nFind as many words satisfying these criteria as possible.Your answer should be on a newline, and contain a comma separated list of all the words you find."""
    model.predict(prompt)