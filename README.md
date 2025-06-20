# Bang Simulation

This repository contains a simple simulation of the board game **Bang!**. It uses
Python and `pandas` to run multiple games and gather statistics about the
outcome.

## Installation

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Run the simulation using:

```bash
python main.py
```

The script will prompt for the number of players (3 to 7) and
optionally which characters to use.

By default the simulation uses a random seed generated from the system. To
reproduce specific results you can set the `BANG_SEED` environment variable
before running any command:

```bash
BANG_SEED=123 python main.py
```

## Running as a microservice

You can expose the simulation through a simple Flask API with a small
web interface. Start the service with:

```bash
python service.py
```

After starting, open `http://localhost:5000/` in your browser to use the
interactive front‑end.

The API exposes two endpoints:

- `GET /simulate` - Run a single game. Query parameters:
  - `players` (optional, default `4`): number of players.
  - `characters` (optional): comma separated list of characters.
- `GET /probability-matrix` - Generate the win/loss matrix. Parameters:
  - `players` (optional, default `4`)
  - `games` (optional, default `50`) number of simulations per
    character/role pair.

Both endpoints return JSON data suitable for a front‑end.

### Characters in the simulation

The following 14 characters from the base game are currently implemented:

```
Bart Cassidy, Calamity Janet, Jesse Jones, Lucky Duke, Paul Regret, Sid Ketchum,
Slab the Killer, Suzy Lafayette, Willy the Kid, El Gringo, Pedro Ramirez,
Kit Carlson, Rose Doolan, Black Jack
```

### Role distribution

Roles are assigned according to the number of players:

| Players | Roles |
|---------|------------------------------------------------|
| 3       | Sheriff, Outlaw, Renegade |
| 4       | Sheriff, 2 Outlaws, Renegade |
| 5       | Sheriff, Deputy, 2 Outlaws, Renegade |
| 6       | Sheriff, Deputy, 3 Outlaws, Renegade |
| 7       | Sheriff, 2 Deputies, 3 Outlaws, Renegade |
