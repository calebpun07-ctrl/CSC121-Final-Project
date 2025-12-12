# TETRIS

This is my final project for CS 121, a recreation of the classic puzzle game Tetris

## Project Overview

This project is a Python implementation of the classic Tetris game. It allows users to play a fully functional version of Tetris directly from the terminal or window (depending on your implementation). The game includes real-time piece movement, rotation, row clearing, scoring, and high‑score tracking.

## Features

* Classic Tetris gameplay
* Random tetromino generation
* Soft drop and rotation controls
* Collision and boundary detection
* Row‑clearing with score updates based on level
* High‑score saving and loading via CSV file
* Multi-file code storing

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/fu-cs-121/final-project-calebpun07-ctrl.git
   cd final-project-calebpun07-ctrl
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install pygame==2.1.3
   ```

## Usage

1. Activate the virtual environment (if not already active):
   ```bash
   source .venv/bin/activate
   ```

2. Run the game:
   ```bash
   python main.py
   ```

3. A window will pop up where you can play Tetris!

### Controls

(Replace these with the actual controls if different.)

* **Arrow Keys or WASD** – Move piece left, right and down (increases fall speed)
* **J and K** – Rotate piece
* **Space** – Hard drop

## Project Structure

```
project/
├── main.py          # Launches the menu
├── game.py          # Handles gameplay mechanics
├── functions.py     # Helper functions used across the game
├── high_scores.csv  # Stores previous scores
└── README.md        # Project documentation
```

## Items to add

* Piece count statstics 
* Incremental speed ups instead of per level
* Soft drop and Hard Drop points
* Next box showing the next piece


## Credits

This project was developed with the assistance of **GitHub Copilot** and **ChatGPT** for code suggestions and documentation support, along with comentation and desgin. 
For getting the user's name, I found help in this post on stack overflow, https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame, and drew inspiration from that desgin.
Inspiration for this project is from the game Tetris made by Alexey Pajitnov, spesificlly NES Tetris, also know as "Classic Tetris".

