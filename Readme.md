# P5.js Game

A simple game built with p5.js where you control a character that needs to navigate through obstacles.

## How to Play

- Click or press Space to start the game
- Click or press Space to make the character jump
- Avoid obstacles to score points
- If you hit an obstacle, the game ends
- Click or press Space to restart after game over

## Running the Game

Simply open the `index.html` file in a web browser to play the game.

## Development

This game is built using p5.js, a JavaScript library for creative coding.

### Project Structure

- `index.html`: Main HTML file
- `sketch.js`: Contains all the game logic and rendering code

## Customization

You can customize the game by modifying the constants at the top of the sketch.js file:

- `PLAYER_SIZE`: Size of the player character
- `OBSTACLE_WIDTH`: Width of the obstacles
- `OBSTACLE_GAP`: Gap between top and bottom obstacles
- `OBSTACLE_SPEED`: How fast obstacles move
- `GRAVITY`: Strength of gravity
- `JUMP_FORCE`: Strength of the jump
- `SPAWN_RATE`: How frequently obstacles spawn

# Game Project - Dual Implementation

This project contains two implementations of the same game:

## Python Version (Pygame/Pygbag)

Located in the `python_version` directory, this implementation uses Python with Pygame and can be compiled to WebAssembly using Pygbag.

### Running the Python Version
