from crossword.crossword import Crossword
from models.deepseek import DeepseekModel
from matplotlib import pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer
import argparse
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


    

def main(args):
            
    crossword = Crossword(args.puzzle)
    
    print(f"LOADED CROSSWORD FROM {args.puzzle}")
    print(crossword)
    print(f"USING {args.model_name} AS SOLVER")
    print(f"PUTTING MODEL ON {args.device} DEVICE")

    model = DeepseekModel(args.model_name, args.device)

    total_guesses = 0
    incorrect_length = 0
    not_finished_thinking = 0
    steps = 0
    progress = []
    MAX_STEPS = (len(crossword.across_clues) + len(crossword.down_clues)) * 2
    prompt = """I need your help to solve a crossword puzzle. I will give you a clue as well as any letters I have so far for the word I am working on. Give your reasoning for your prediction. You must put your final answer as a single word on a newline without any punctuation."""
    
    while not crossword.check_solved_percentage() == 100.0 and steps < MAX_STEPS:
        clue_types = {"Across": crossword.across_clues, "Down": crossword.down_clues}
        for clue_dict_type in clue_types:
            for clue_id in clue_types[clue_dict_type]:
                current_guess = crossword.get_current_guess(clue_id, clue_dict_type)
                pred = model.predict(f'{prompt}\n\nThe current clue is "{clue_types[clue_dict_type][clue_id]}"\nThe current guess is {current_guess}. It is a {len(current_guess)} letter word.')
                if pred and not pred.isnumeric():
                    out = crossword.guess_word(clue_id, clue_dict_type, pred)
                    if out == "ERROR: Guess is not correct length":
                        incorrect_length += 1
                    total_guesses += 1
                else:
                    not_finished_thinking += 1
                solved_percentage = crossword.check_solved_percentage()
                print(crossword)
                print(f"Made {total_guesses} total guesses")
                print(f"Solved {solved_percentage}% of the crossword")
                progress.append(solved_percentage)
                steps += 1

    print(f"{args.model_name} STATS FOR ATTEMPT:")
    print(f"There are a total of {len(crossword.across_clues) + len(crossword.down_clues)} clues for the puzzle")
    print(f"Ran solver for {steps} steps")
    print(f"{crossword.check_solved_percentage()}% of the crossword was solved")
    print(f"{incorrect_length} guesses were not of the correct length")
    print(f"Model did not finish thinking on {not_finished_thinking} clues")

    plt.plot(list(range(1, len(progress) + 1)), progress, linewidth=3)
    plt.title("Percentage of Crossword Solved Over Timestep")
    plt.ylabel("Solved Percentage")
    plt.xlabel("Step Number")
    plt.xticks(ticks=list(range(1, len(progress) + 1)))
    print("Saving plot of solve trajectory...")
    plt.savefig(f"{args.model_name}.pdf", dpi=300)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--puzzle", type=str, default="htmls/mini.html")
    parser.add_argument("--model_name", type=str, default="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", help="Huggingface Reasoning Model")
    parser.add_argument("--device", type=str, default="cuda", help="Cuda or CPU")

    args = parser.parse_args()
    main(args)


