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

## Running as a microservice

You can expose the simulation through a simple Flask API. Start the
service with:

```bash
python service.py
```

The API exposes two endpoints:

- `GET /simulate` - Run a single game. Query parameters:
  - `players` (optional, default `4`): number of players.
  - `characters` (optional): comma separated list of characters.
- `GET /probability-matrix` - Generate the win/loss matrix. Parameters:
  - `players` (optional, default `4`)
  - `games` (optional, default `50`) number of simulations per
    character/role pair.

Both endpoints return JSON data suitable for a front‑end.
