from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer
import argparse
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

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



    

def main(args):
    def pretty_print(crossword):
        # Determine the maximum width of any cell (up to 3 characters)
        max_width = max(len(cell) for row in crossword for cell in row)
        max_width = min(max_width, 3)  # Limit to 3 characters
        
        row_separator = "+" + ("-" * (max_width + 2) + "+") * len(crossword[0])
        
        for row in crossword:
            print(row_separator)
            print("| " + " | ".join(cell.ljust(max_width) for cell in row) + " |")
        print(row_separator)

    def check_solved_percentage(crossword, solution):
        correct = 0
        total = 0
        for i in range(len(crossword)):
            for j in range(len(crossword[0])):
                if crossword[i][j] == solution[i][j]:
                    correct += 1
                total += 1
        return round(correct / total * 100, 2)

    def guess_word(crossword, clue_num, direction, guess):
        current_guess = get_current_guess(crossword, clue_num, direction)
        if len(current_guess) != len(guess):
            return "ERROR: Guess is not correct length"
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

    html = open(args.puzzle, 'r', encoding="utf-8")
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
    solution = [[' ' for _ in range(n_cols)] for _ in range(n_rows)]
    word_starts = {}
    for cell in cells:
        cell['i'] = int((cell['x'] - min(xs)) // grid_size)
        cell['j'] = int((cell['y'] - min(ys)) // grid_size)
        if cell['text'] != None:
            solution[cell['j']][cell['i']] = cell['answer']
            if cell['text'].isnumeric():
                word_starts[cell['text']] = (cell['j'], cell['i'])
            #crossword[cell['j']][cell['i']] = cell['text']
        else:
            crossword[cell['j']][cell['i']] = "■"
            
    print(f"LOADED CROSSWORD FROM {args.puzzle}")
    pretty_print(crossword)
    print(f"USING {args.model_name} AS SOLVER")

    model_name = args.model_name
    device = "cuda" # the device to load the model onto

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def get_deepseek_prediction(clue):
        prompt = """I need your help to solve a crossword puzzle. I will give you a clue as well as any letters I have so far for the word I am working on. Give your reasoning for your prediction."""
        
        # CoT
        messages = [
            {"role": "system", "content": "Please reason step by step. You must put your final answer as a single word on a newline without any punctuation."},
            {"role": "user", "content": prompt + "\n" + clue},
        ]

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        model_inputs = tokenizer([text], return_tensors="pt").to(device)
        pad_token_id = tokenizer.eos_token_id

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=2000,
            pad_token_id = pad_token_id
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        print(response)
        if "</think>\n" in response:
            return response.split("\n")[-1].strip()
        
        return None

    total_guesses = 0
    incorrect_length = 0
    not_finished_thinking = 0
    steps = 0
    progress = []
    MAX_STEPS = (len(across) + len(down)) * 2
    while not check_solved_percentage(crossword, solution) == 100.0 and steps < MAX_STEPS:
        clue_types = {"Across": across, "Down": down}
        for clue_dict_type in clue_types:
            for clue_id in clue_types[clue_dict_type]:
                current_guess = get_current_guess(crossword, clue_id, clue_dict_type)
                pred = get_deepseek_prediction(f'The current clue is "{clue_types[clue_dict_type][clue_id]}"\nThe current guess is {current_guess}. It is a {len(current_guess)} letter word.')
                if pred and not pred.isnumeric():
                    out = guess_word(crossword, clue_id, clue_dict_type, pred)
                    if out == "ERROR: Guess is not correct length":
                        incorrect_length += 1
                    total_guesses += 1
                else:
                    not_finished_thinking += 1
                solved_percentage = check_solved_percentage(crossword, solution)
                pretty_print(crossword)
                print(f"Made {total_guesses} total guesses")
                print(f"Solved {solved_percentage}% of the crossword")
                progress.append(solved_percentage)
                steps += 1

    print(f"{model_name} STATS FOR ATTEMPT:")
    print(f"There are a total of {len(across) + len(down)} clues for the puzzle")
    print(f"Ran solver for {steps} steps")
    print(f"{check_solved_percentage(crossword, solution)}% of the crossword was solved")
    print(f"{incorrect_length} guesses were not of the correct length")
    print(f"Model did not finish thinking on {not_finished_thinking} clues")

    plt.plot(list(range(1, len(progress) + 1)), progress, linewidth=3)
    plt.title("Percentage of Crossword Solved Over Timestep")
    plt.ylabel("Solved Percentage")
    plt.xlabel("Step Number")
    plt.xticks(list(range(1, len(progress + 1))))
    print("Saving plot of solve trajectory...")
    plt.savefig("crossword.pdf", dpi=300)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--puzzle", type=str, default="htmls/mini.html")
    parser.add_argument("--model_name", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", help="Huggingface Reasoning Model")
    args = parser.parse_args()
    main(args)


