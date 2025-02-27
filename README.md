# NYTimes Puzzle Solvers
I like doing some of the NYTimes puzzles, so I made this repo to see if AI can solve any of the puzzles. So far, Deepseek seems to struggle with character based reasoning.

### Installation
First install Anaconda. Afterwards, run this in the anaconda prompt:

```python
conda create -n nytimes python=3.10
conda activate nytimes
git clone https://github.com/tossowski/NYTimesPuzzleSolver.git && cd NYTimesPuzzleSolver
pip install -r requirements.txt
```

### Usage
Each NYTimes puzzle will have its own solving script (e.g. `crossword_solver.py`). Detailed instructions for each puzzle are described in the argparse help screen, which is shown when running `python <solver_script> -h`
