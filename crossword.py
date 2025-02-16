from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import random

prompt = """I need your help to solve a crossword puzzle. I will give you a clue as well as any letters I have so far for the word I am working on. Give your reasoning for your prediction, and put the final word on a newline by itself without punctuation. If you are not 100 percent sure of the answer, say your answer is 404."""

def pretty_print(crossword):
    # Determine the maximum width of any cell (up to 3 characters)
    max_width = max(len(cell) for row in crossword for cell in row)
    max_width = min(max_width, 3)  # Limit to 3 characters
    
    row_separator = "+" + ("-" * (max_width + 2) + "+") * len(crossword[0])
    
    for row in crossword:
        print(row_separator)
        print("| " + " | ".join(cell.ljust(max_width) for cell in row) + " |")
    print(row_separator)

def is_full(crossword):
    for row in crossword:
        if " " in row:
            return False
    return True

def guess_word(crossword, clue_num, direction, guess):
    current_guess = get_current_guess(crossword, clue_num, direction)
    if len(current_guess) != len(guess):
        print("ERROR: Guess is not correct length")
        return
    i, j = word_starts[clue_num]
    current_guess = ""
    if direction == 'Across':
        for k in range(len(guess)):
            crossword[i][j + k] = guess[k].upper()
    else:     
        for k in range(len(guess)):
            crossword[i + k][j] = guess[k].upper()
            
def get_current_guess(crossword, clue_num, direction):
    i, j = word_starts[clue_num]
    current_guess = ""
    if direction == 'Across':
        while j < len(crossword[0]) and crossword[i][j] != "■":
            if crossword[i][j] == ' ':
                current_guess += "_"
            else:
                current_guess += crossword[i][j]
            j += 1
    else:
        while i < len(crossword) and crossword[i][j] != "■":
            if crossword[i][j] == ' ':
                current_guess += "_"
            else:
                current_guess += crossword[i][j]
            i += 1
    return current_guess 


def parse_crossword(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract crossword cells
    cells = []
    for cell in soup.find_all('g', class_='xwd__cell'):
        rect = cell.find('rect')
        cell_text = None
        text = cell.find('text')
        if text:
            cell_text = text.get_text(strip=True)
        cell_info = {
            'cell_id': rect.get('id', ''),
            'x': float(rect.get('x', '0.0')),
            'y': float(rect.get('y', '0.0')),
            'width': float(rect.get('width', '0.0')),
            'height': float(rect.get('height', '0.0')),
            'text': cell_text
        }
        cells.append(cell_info)
    
    # Extract clues
    accross_clues = {}
    down_clues = {}
    
    clue_lists = soup.find_all('div', class_="xwd__clue-list--wrapper")

    for clue_list in clue_lists:
        clue_direction = clue_list.find('h3', class_='xwd__clue-list--title').get_text()
        for entry in clue_list.find('ol'):
            clue_num = entry.find('span', class_='xwd__clue--label').get_text()
            clue_text = entry.find('span', class_='xwd__clue--text').get_text()
            if clue_direction == 'Across':
                accross_clues[clue_num] = clue_text
                #text
            else:
                down_clues[clue_num] = clue_text
    return cells, accross_clues, down_clues

# Example usage:
# html = """<html>...your provided HTML here...</html>"""
html = open('htmls/mini.html', 'r', encoding="utf-8")
cells, across, down = parse_crossword(html)
xs = [cell['x'] for cell in cells]
ys = [cell['y'] for cell in cells]

assert cells[0]['width'] == cells[0]['height']
for cell in cells:
    assert cell['width'] == cells[0]['width']
    assert cell['height'] == cells[0]['height']

grid_size = int(cells[0]['width'])
n_rows = int((max(ys) - min(ys)) // grid_size + 1)
n_cols = int((max(xs) - min(xs)) // grid_size + 1)

crossword = [[' ' for _ in range(n_cols)] for _ in range(n_rows)]

word_starts = {}
for cell in cells:
    cell['i'] = int((cell['x'] - min(xs)) // grid_size)
    cell['j'] = int((cell['y'] - min(ys)) // grid_size)
    if cell['text'] != None:
        if cell['text'].isnumeric():
            word_starts[cell['text']] = (cell['j'], cell['i'])
        #crossword[cell['j']][cell['i']] = cell['text']
    else:
        crossword[cell['j']][cell['i']] = "■"
    
print(across)
print(down)
pretty_print(crossword)
letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

while not is_full(crossword):
    
    for clue_id in across:
        current_guess = get_current_guess(crossword, clue_id, 'Across')
        print(f'{prompt}\n\nThe current clue is "{across[clue_id]}"\nThe current guess is {current_guess}. It is a {len(current_guess)} letter word.')
        if "_" in current_guess:
            guess_word(crossword, clue_id, 'Across', ''.join([random.choice(letters) for _ in range(len(current_guess))]))
    for clue_id in down:
        current_guess = get_current_guess(crossword, clue_id, 'Down')
        if "_" in current_guess:
            guess_word(crossword, clue_id, 'Down', ''.join([random.choice(letters) for _ in range(len(current_guess))]))

# guess_word(crossword, '1', 'Across', 'hello')
pretty_print(crossword)
# print(get_current_guess(crossword, '1', 'Across'))
# print(get_current_guess(crossword, '1', 'Down'))

