# Bang! Simulation

This repository contains a simplified simulation of the card game **Bang!**. The
program runs multiple mock games and reports statistics for the winning roles
and selected characters.

## Requirements

- Python 3.8 or newer
- [pandas](https://pandas.pydata.org/) library

Install the dependency with:

```bash
pip install pandas
```

## Running the simulation

Execute `main.py` with Python. The script will prompt for the number of players
and optional characters to use in the game. By default it simulates 5000 games
and prints a summary table.

```bash
python main.py
```

Example interaction:

```text
$ python main.py
Numero de jogadores (3-16): 4
Personagens disponiveis:
Bart Cassidy, Calamity Janet, Jesse Jones, Lucky Duke, Paul Regret, Sid Ketchum,
Slab the Killer, Suzy Lafayette, Willy the Kid, El Gringo, Pedro Ramirez,
Kit Carlson, Rose Doolan, Black Jack
Digite os personagens separados por virgula ou pressione Enter para aleatorio:
```

After answering the prompts, the script outputs the win statistics for each role
and for specific role/character combinations.

## Available characters

The current list of characters supported by the simulation is:

- Bart Cassidy
- Calamity Janet
- Jesse Jones
- Lucky Duke
- Paul Regret
- Sid Ketchum
- Slab the Killer
- Suzy Lafayette
- Willy the Kid
- El Gringo
- Pedro Ramirez
- Kit Carlson
- Rose Doolan
- Black Jack
