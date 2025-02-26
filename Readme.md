# AI Zombie Apocalypse - Game Documentation

## Overview
AI Zombie Apocalypse is a top-down shooter game where you control an AI robot fighting against hordes of zombies. The game features AI-assisted gameplay mechanics, power-ups, and online leaderboards powered by Supabase.

## Game Features
- Fast-paced zombie shooting action
- AI assistant power-ups that help you fight zombies
- Dynamic difficulty that increases over time
- Online leaderboard to compete with other players
- Cyberpunk-inspired visuals with glowing effects

## Controls
- **WASD** or **Arrow Keys**: Move your character
- **Mouse**: Aim and shoot (left-click)
- Collect AI power-ups (glowing blue orbs) for automated assistance

## Installation

### Requirements
- Python 3.8+
- Required packages (install via pip):
  ```
  pip install -r requirements.txt
  ```

### Running the Game
```
python main.py
```

### Web Version
The game can also be played in a web browser using pygbag:
```
pygbag main.py
```

## Setting Up Supabase

### 1. Create a Supabase Account
1. Go to [Supabase](https://supabase.com/) and sign up for an account
2. Create a new project

### 2. Set Up Environment Variables
Create a `.env` file in the project root with the following:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Database Setup
Execute the following SQL commands in the Supabase SQL Editor:

```sql
-- Create scores table
CREATE TABLE scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    player_name TEXT NOT NULL,
    email TEXT,
    score INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster leaderboard queries
CREATE INDEX scores_score_idx ON scores (score DESC);

-- Create a secure policy for inserting scores
CREATE POLICY "Enable insert for authenticated users only" 
ON scores FOR INSERT 
WITH CHECK (true);

-- Create a policy for reading scores (public)
CREATE POLICY "Enable read access for all users" 
ON scores FOR SELECT 
USING (true);

-- Enable Row Level Security
ALTER TABLE scores ENABLE ROW LEVEL SECURITY;
```

### 4. API Functions
Create the following Supabase Edge Function for email validation:

```javascript
// filename: functions/validate-email/index.js
import { serve } from 'https://deno.land/std@0.131.0/http/server.ts'

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

serve(async (req) => {
  const { email } = await req.json();
  
  const isValid = typeof email === 'string' && emailRegex.test(email);
  
  return new Response(
    JSON.stringify({ valid: isValid }),
    { headers: { 'Content-Type': 'application/json' } },
  );
});
```

## Game Architecture

### Main Components
- **Player**: Controls the AI robot character
- **Zombies**: Enemy NPCs that chase the player
- **Bullets**: Projectiles fired by the player
- **AI Assistant**: Temporary power-up that helps the player
- **Visual Effects**: Blood splatters and explosions

### Game Loop
1. Process user input
2. Update game state (player, zombies, bullets)
3. Check for collisions
4. Render game elements
5. Repeat

## Development
The game is built with Python and Pygame. The main components are:
- `main.py`: Entry point and game loop
- `assets/`: Directory containing game assets

## Credits
- Developed by: HackerHall
- Artwork: Procedurally generated with Python
- Sound effects: Artlist

## License
[Specify your license here]
