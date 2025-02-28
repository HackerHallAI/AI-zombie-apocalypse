# AI Zombie Apocalypse

A zombie survival game with AI assistant features, available in both Python and JavaScript versions.

## Game Overview

In AI Zombie Apocalypse, you control an AI robot fighting against zombie hordes. Collect power-ups to activate special abilities, including an AI assistant that helps you target and shoot zombies automatically.

## Running the Games

### JavaScript Version (Browser-based)

The JavaScript version can be played directly in your web browser:

1. Open the `zombie-js/index.html` file in your web browser
2. Or host the files on any web server and access through your browser

**Features:**
- No installation required
- Leaderboard functionality (requires Supabase configuration)
- Mobile-friendly controls

**Supabase Configuration (Optional):**
1. Copy `zombie-js/supabase-config.template.js` to `zombie-js/supabase-config.js`
2. Update with your Supabase URL and anon key

### Python Version (Desktop)

The Python version runs as a desktop application:

1. Install required dependencies:
   ```
   pip install -r zombie-py/requirements.txt
   ```

2. Run the game:
   ```
   cd zombie-py
   python main.py
   ```

**Requirements:**
- Python 3.7+
- Pygame
- Other dependencies listed in requirements.txt

**Environment Configuration (Optional):**
1. Copy `zombie-py/.env.template` to `zombie-py/.env`
2. Update with your Supabase credentials for leaderboard functionality

## Game Controls

- **Movement**: WASD or Arrow Keys
- **Aim**: Mouse
- **Shoot**: Left Mouse Button
- **Pause**: ESC

## Power-ups

- **AI Assistant**: Automatically targets and shoots nearby zombies
- **Speed Boost**: Increases movement speed
- **Shield**: Provides temporary immunity to zombie attacks
- **Rapid Fire**: Increases firing rate and adds bullet spread

## Leaderboard

Both versions feature an online leaderboard system powered by Supabase. Submit your score to see how you rank against other players!

## Development

This project demonstrates implementing the same game in two different programming languages while maintaining similar gameplay and features.

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
