from bs4 import BeautifulSoup

class Crossword():
    def __init__(self, path_to_html):
        html = open(path_to_html, 'r', encoding="utf-8")
        self.cells, self.across_clues, self.down_clues = self.parse_html(html)
        xs = [cell['x'] for cell in self.cells]
        ys = [cell['y'] for cell in self.cells]

        assert self.cells[0]['width'] == self.cells[0]['height']
        for cell in self.cells:
            assert cell['width'] == self.cells[0]['width']
            assert cell['height'] == self.cells[0]['height']

        grid_size = int(self.cells[0]['width'])
        n_rows = int((max(ys) - min(ys)) // grid_size + 1)
        n_cols = int((max(xs) - min(xs)) // grid_size + 1)

        self.crossword = [[' ' for _ in range(n_cols)] for _ in range(n_rows)]
        self.solution = [[' ' for _ in range(n_cols)] for _ in range(n_rows)]
        self.word_starts = {}
        for cell in self.cells:
            cell['i'] = int((cell['x'] - min(xs)) // grid_size)
            cell['j'] = int((cell['y'] - min(ys)) // grid_size)
            if cell['text'] != None:
                self.solution[cell['j']][cell['i']] = cell['answer']
                if cell['text'].isnumeric():
                    self.word_starts[cell['text']] = (cell['j'], cell['i'])
                #crossword[cell['j']][cell['i']] = cell['text']
            else:
                self.crossword[cell['j']][cell['i']] = "■"

    def parse_html(self, path_to_html):
        soup = BeautifulSoup(path_to_html, 'html.parser')
    
        # Extract crossword cells
        cells = []
        for cell in soup.find_all('g', class_='xwd__cell'):
            rect = cell.find('rect')
            cell_text = None
            text = cell.find('text')
            if text:
                cell_text = text.get_text(strip=True)
            cell_texts = cell.find_all("text", {"data-testid": "cell-text"})

            answer = '■'
            for text_element in cell_texts:
                hidden_text = text_element.find("text", class_="xwd__cell--hidden")
                answer = hidden_text.text if hidden_text else text_element.text
            
            cell_info = {
                'cell_id': rect.get('id', ''),
                'x': float(rect.get('x', '0.0')),
                'y': float(rect.get('y', '0.0')),
                'width': float(rect.get('width', '0.0')),
                'height': float(rect.get('height', '0.0')),
                'text': cell_text,
                'answer': answer
            }
            cells.append(cell_info)
        
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

    def check_solved_percentage(self):
        correct = 0
        total = 0
        for i in range(len(self.crossword)):
            for j in range(len(self.crossword[0])):
                if self.crossword[i][j] == self.solution[i][j]:
                    correct += 1
                total += 1
        return round(correct / total * 100, 2)

    def get_current_guess(self, clue_num, direction):
        i, j = self.word_starts[clue_num]
        current_guess = ""
        if direction == 'Across':
            while j < len(self.crossword[0]) and self.crossword[i][j] != "■":
                if self.crossword[i][j] == ' ':
                    current_guess += "_"
                else:
                    current_guess += self.crossword[i][j]
                j += 1
        else:
            while i < len(self.crossword) and self.crossword[i][j] != "■":
                if self.crossword[i][j] == ' ':
                    current_guess += "_"
                else:
                    current_guess += self.crossword[i][j]
                i += 1
        return current_guess 

    def guess_word(self, clue_num, direction, guess):
        current_guess = self.get_current_guess(clue_num, direction)
        if len(current_guess) != len(guess):
            return "ERROR: Guess is not correct length"
        i, j = self.word_starts[clue_num]
        current_guess = ""
        if direction == 'Across':
            for k in range(len(guess)):
                self.crossword[i][j + k] = guess[k].upper()
        else:     
            for k in range(len(guess)):
                self.crossword[i + k][j] = guess[k].upper()

    def __str__(self):
        
        # Determine the maximum width of any cell (up to 3 characters)
        max_width = max(len(cell) for row in self.crossword for cell in row)
        max_width = min(max_width, 3)  # Limit to 3 characters
        acc = ""
        row_separator = "+" + ("-" * (max_width + 2) + "+") * len(self.crossword[0])
        
        for row in self.crossword:
            acc += row_separator + "\n"
            acc += "| " + " | ".join(cell.ljust(max_width) for cell in row) + " |\n"
        
        return acc + row_separator