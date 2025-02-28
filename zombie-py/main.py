import pygame
import random
import asyncio
import os
import sys
from PIL import Image
import numpy as np
import math
from dotenv import load_dotenv
import re
import pygame.mixer

# Try to import Supabase, but don't fail if it's not available in browser
try:
    from supabase import create_client, Client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Detect if running in browser via Pygbag
IN_BROWSER = "__EMSCRIPTEN__" in sys.modules or "pygbag" in sys.modules

# Load environment variables
load_dotenv()

# Initialize Supabase client if available
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Create a placeholder if environment variables aren't set or in browser
if not SUPABASE_AVAILABLE or not supabase_url or not supabase_key:
    print(
        "Warning: Supabase credentials not found or not available. Using offline mode."
    )
    supabase = None
else:
    supabase = create_client(supabase_url, supabase_key)

# Initialize Pygame
pygame.init()


# Modify the sound system initialization
def initialize_sound_system():
    """Initialize the sound system with browser compatibility."""
    global SOUND_ENABLED

    try:
        pygame.mixer.init()
        if not IN_BROWSER:
            # Only run the test sound in desktop mode
            test_sound_system()
        SOUND_ENABLED = True
        return True
    except Exception as e:
        print(f"Could not initialize sound system: {e}")
        SOUND_ENABLED = False
        return False


# Replace pygame.mixer.init() with this call
initialize_sound_system()

# Set up the screen
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Shooter")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_WIDTH = 32
PLAYER_HEIGHT = 32
PLAYER_COLOR = BLUE
PLAYER_SPEED = 5

# Zombie settings
ZOMBIE_WIDTH = 32
ZOMBIE_HEIGHT = 32
ZOMBIE_COLOR = GREEN
ZOMBIE_SPEED = 2

# Bullet settings
BULLET_WIDTH = 4
BULLET_HEIGHT = 4
BULLET_COLOR = RED
BULLET_SPEED = 10

# Game settings
FPS = 60
SCORE_FONT = pygame.font.SysFont("arial", 20)
GAME_OVER_FONT = pygame.font.SysFont("arial", 40)

# Image paths
ASSETS_DIR = "assets"
PLAYER_IMG = os.path.join(ASSETS_DIR, "player.png")
ZOMBIE_IMG = os.path.join(ASSETS_DIR, "zombie.png")
BULLET_IMG = os.path.join(ASSETS_DIR, "bullet.png")
BACKGROUND_IMG = os.path.join(ASSETS_DIR, "background.png")

# Add these constants
AI_ASSISTANT_COOLDOWN = 600  # 10 seconds at 60 FPS
AI_ASSISTANT_DURATION = 300  # 5 seconds of assistance
AI_ASSISTANT_COLOR = (0, 200, 255)  # Bright blue for AI elements
ROCK_COUNT = 8  # Fewer rocks
SMALL_ROCK_COUNT = 15  # Add smaller decorative rocks that don't block movement
POWERUP_TYPES = [
    {"name": "AI Assistant", "color": (0, 200, 255), "duration": 300},
    {"name": "Speed Boost", "color": (255, 200, 0), "duration": 180},
    {"name": "Shield", "color": (200, 0, 255), "duration": 240},
    {"name": "Rapid Fire", "color": (255, 50, 50), "duration": 200},
]

# Create assets directory if it doesn't exist
os.makedirs(ASSETS_DIR, exist_ok=True)

# Sound settings
SOUND_ENABLED = True  # Allow players to toggle sounds
SOUNDS = {
    "shoot": None,
    "zombie_hit": None,
    "player_damage": None,
    "game_over": None,
    "powerup": None,  # This is ai-assist when we fix this but trying to just get something in the game.
    "wave_start": None,
    "shield_hit": None,  # This is currently the sheild on sound but we will see how it works.
}

# Add volume control variables
SOUND_VOLUME = 0.7  # Default volume (0.0 to 1.0)

# Add this to the sound settings section
MUSIC_ENABLED = True


# Add this function to handle background music
def play_background_music():
    """Start playing background music if available."""
    if not MUSIC_ENABLED:
        return

    try:
        music_file = os.path.join(ASSETS_DIR, "sounds", "background_music.wav")
        if os.path.exists(music_file):
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(
                SOUND_VOLUME * 0.5
            )  # Lower volume for background music
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print("Background music started")
        else:
            # Create procedural background music
            print("Creating procedural background music")
            create_procedural_music()
    except Exception as e:
        print(f"Could not play background music: {e}")


# Simplify the procedural music for browser compatibility
def create_procedural_music():
    """Create simple procedural background music with browser compatibility."""
    try:
        if IN_BROWSER:
            print("Skipping procedural music in browser mode")
            return

        # Rest of your existing procedural music code...
    except Exception as e:
        print(f"Could not create procedural music: {e}")


# Add this function to create placeholder sounds if files are missing
def create_placeholder_sound():
    """Create a simple placeholder sound."""
    try:
        # Create a simple beep sound
        sample_rate = 44100
        duration = 0.1  # 100ms
        frequency = 440  # A4 note

        # Generate a sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(frequency * 2 * np.pi * t) * 0.5

        # Convert to stereo
        stereo = np.column_stack((tone, tone))

        # Convert to 16-bit signed integers
        audio = (stereo * 32767).astype(np.int16)

        # Create a Sound object
        return pygame.mixer.Sound(pygame.sndarray.make_sound(audio))
    except Exception as e:
        print(f"Could not create placeholder sound: {e}")
        return None


# Modify the load_sounds function to properly load existing sound files
def load_sounds():
    """Load all game sound effects with improved error handling."""
    global SOUNDS, SOUND_ENABLED

    # Create sounds directory if it doesn't exist
    sounds_dir = os.path.join(ASSETS_DIR, "sounds")
    os.makedirs(sounds_dir, exist_ok=True)

    # List of expected sound files
    sound_files = {
        "shoot": "shoot.wav",
        "zombie_hit": "zombie_hit.wav",
        "player_damage": "player_damage.wav",
        "game_over": "game_over.wav",
        "powerup": "powerup.wav",
        "wave_start": "wave_start.wav",
        "shield_hit": "shield_hit.wav",
    }

    # Try to load each sound individually
    loaded_count = 0
    missing_count = 0

    for sound_name, filename in sound_files.items():
        file_path = os.path.join(sounds_dir, filename)

        if os.path.exists(file_path):
            # File exists, try to load it
            try:
                SOUNDS[sound_name] = pygame.mixer.Sound(file_path)
                SOUNDS[sound_name].set_volume(SOUND_VOLUME)
                print(f"Successfully loaded sound: {sound_name} from {file_path}")
                loaded_count += 1
            except Exception as e:
                print(f"Error loading sound {sound_name} from {file_path}: {e}")
                SOUNDS[sound_name] = create_placeholder_sound()
                print(f"Using placeholder for {sound_name}")
        else:
            # File doesn't exist, use placeholder
            print(f"Sound file missing: {filename}")
            SOUNDS[sound_name] = create_placeholder_sound()
            missing_count += 1

    # Print summary
    if loaded_count > 0:
        print(f"Successfully loaded {loaded_count} sound files.")

    if missing_count > 0:
        print(f"Created placeholders for {missing_count} missing sound files.")

    # Enable sound if we have any sounds (real or placeholder)
    if any(SOUNDS.values()):
        SOUND_ENABLED = True
        print("Sound system enabled.")
    else:
        SOUND_ENABLED = False
        print("Sound system disabled - no sounds could be loaded.")

    # Debug: Print the current state of the SOUNDS dictionary
    print("Current sounds status:")
    for name, sound in SOUNDS.items():
        print(f"  - {name}: {'Loaded' if sound is not None else 'None'}")


# Function to play a sound
def play_sound(sound_name):
    """Play a sound by name if sound is enabled, with better error handling."""
    if not SOUND_ENABLED:
        return

    if sound_name not in SOUNDS:
        print(f"Warning: Attempted to play unknown sound: {sound_name}")
        return

    if SOUNDS[sound_name] is None:
        # Silent fail for known but unavailable sounds
        return

    try:
        SOUNDS[sound_name].play()
    except Exception as e:
        print(f"Error playing sound {sound_name}: {e}")


# Function to load images
def load_image(path, width, height):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))
    except pygame.error:
        print(f"Could not load image: {path}")
        return None


# Create images programmatically
def initialize_images():
    global player_img, zombie_img, bullet_img, background_img, blood_splatter_imgs, explosion_imgs, rocks

    # Load sounds and ensure sound directory exists
    load_sounds()
    ensure_sound_directory()

    # Start background music
    play_background_music()

    # Create a more detailed player (AI robot with glowing elements)
    player_img = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)

    # Robot body (metallic blue)
    pygame.draw.rect(player_img, (40, 90, 180), (6, 6, 20, 20), border_radius=3)

    # Glowing core
    pygame.draw.circle(player_img, (0, 200, 255, 200), (16, 16), 5)
    pygame.draw.circle(player_img, (150, 230, 255, 150), (16, 16), 7, 2)

    # Robot head
    pygame.draw.rect(player_img, (60, 110, 200), (10, 0, 12, 8), border_radius=2)

    # Eyes (glowing)
    pygame.draw.circle(player_img, (0, 255, 255), (13, 4), 2)
    pygame.draw.circle(player_img, (0, 255, 255), (19, 4), 2)

    # Limbs
    pygame.draw.rect(
        player_img, (50, 100, 190), (2, 10, 4, 16), border_radius=2
    )  # Left arm
    pygame.draw.rect(
        player_img, (50, 100, 190), (26, 10, 4, 16), border_radius=2
    )  # Right arm
    pygame.draw.rect(
        player_img, (50, 100, 190), (8, 26, 6, 6), border_radius=1
    )  # Left leg
    pygame.draw.rect(
        player_img, (50, 100, 190), (18, 26, 6, 6), border_radius=1
    )  # Right leg

    # Circuit patterns
    for i in range(3):
        x = random.randint(8, 24)
        y = random.randint(8, 24)
        pygame.draw.line(player_img, (100, 200, 255), (x, y), (x + 4, y), 1)
        pygame.draw.line(player_img, (100, 200, 255), (x, y), (x, y + 4), 1)

    # Create a more detailed zombie
    zombie_img = pygame.Surface((ZOMBIE_WIDTH, ZOMBIE_HEIGHT), pygame.SRCALPHA)

    # Zombie body (decaying green)
    body_color = (
        60 + random.randint(-20, 20),
        120 + random.randint(-20, 20),
        60 + random.randint(-20, 20),
    )
    pygame.draw.rect(zombie_img, body_color, (6, 6, 20, 20), border_radius=2)

    # Zombie head
    head_color = (
        70 + random.randint(-20, 20),
        110 + random.randint(-20, 20),
        70 + random.randint(-20, 20),
    )
    pygame.draw.rect(zombie_img, head_color, (10, 0, 12, 8), border_radius=2)

    # Glowing red eyes
    pygame.draw.circle(zombie_img, (255, 0, 0), (13, 4), 2)
    pygame.draw.circle(zombie_img, (255, 0, 0), (19, 4), 2)

    # Zombie limbs (asymmetrical and decaying)
    pygame.draw.rect(
        zombie_img, body_color, (2, 10, 4, 14), border_radius=1
    )  # Left arm
    pygame.draw.rect(
        zombie_img, body_color, (26, 12, 4, 12), border_radius=1
    )  # Right arm
    pygame.draw.rect(zombie_img, body_color, (8, 26, 6, 6), border_radius=1)  # Left leg
    pygame.draw.rect(
        zombie_img, body_color, (18, 26, 6, 6), border_radius=1
    )  # Right leg

    # Blood stains
    for _ in range(4):
        x = random.randint(4, 28)
        y = random.randint(4, 28)
        size = random.randint(2, 4)
        pygame.draw.circle(zombie_img, (200, 0, 0, 150), (x, y), size)

    # Create a more impressive bullet (energy projectile)
    bullet_img = pygame.Surface((BULLET_WIDTH * 3, BULLET_HEIGHT * 3), pygame.SRCALPHA)

    # Glowing core
    pygame.draw.circle(
        bullet_img,
        (0, 200, 255),
        (BULLET_WIDTH * 3 // 2, BULLET_HEIGHT * 3 // 2),
        BULLET_WIDTH,
    )

    # Outer glow
    pygame.draw.circle(
        bullet_img,
        (100, 220, 255, 150),
        (BULLET_WIDTH * 3 // 2, BULLET_HEIGHT * 3 // 2),
        BULLET_WIDTH * 1.5,
    )

    # Energy trails
    for i in range(3):
        angle = random.uniform(0, 2 * math.pi)
        length = random.randint(3, 6)
        end_x = BULLET_WIDTH * 3 // 2 + math.cos(angle) * length
        end_y = BULLET_HEIGHT * 3 // 2 + math.sin(angle) * length
        pygame.draw.line(
            bullet_img,
            (0, 255, 255, 100),
            (BULLET_WIDTH * 3 // 2, BULLET_HEIGHT * 3 // 2),
            (end_x, end_y),
            2,
        )

    # Create a more detailed background (cyberpunk grid with glow effects)
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill((5, 7, 15))  # Very dark blue

    # Draw main grid
    for x in range(0, SCREEN_WIDTH, 40):
        intensity = 30 + 10 * math.sin(x / 100)  # Pulsing effect
        pygame.draw.line(
            background_img, (0, intensity, intensity * 2), (x, 0), (x, SCREEN_HEIGHT)
        )

    for y in range(0, SCREEN_HEIGHT, 40):
        intensity = 30 + 10 * math.sin(y / 100)  # Pulsing effect
        pygame.draw.line(
            background_img, (0, intensity, intensity * 2), (0, y), (SCREEN_WIDTH, y)
        )

    # Add some random glowing nodes at grid intersections
    for _ in range(15):
        x = random.randint(0, 16) * 40
        y = random.randint(0, 12) * 40
        size = random.randint(3, 6)
        pygame.draw.circle(background_img, (0, 150, 255, 150), (x, y), size)
        # Add glow effect
        pygame.draw.circle(background_img, (0, 100, 200, 50), (x, y), size * 2)

    # Create blood splatter animation frames
    blood_splatter_imgs = []
    for i in range(5):
        splatter = pygame.Surface((40, 40), pygame.SRCALPHA)
        num_drops = 5 + i * 3
        for _ in range(num_drops):
            x = random.randint(10, 30)
            y = random.randint(10, 30)
            size = random.randint(2, 5)
            pygame.draw.circle(splatter, (200, 0, 0, 200 - i * 30), (x, y), size)
        blood_splatter_imgs.append(splatter)

    # Create explosion animation frames
    explosion_imgs = []
    for i in range(6):
        explosion = pygame.Surface((60, 60), pygame.SRCALPHA)
        # Inner bright core
        pygame.draw.circle(
            explosion, (255, 255, 200, 255 - i * 40), (30, 30), 5 + i * 4
        )
        # Middle layer
        pygame.draw.circle(
            explosion, (255, 150, 50, 200 - i * 30), (30, 30), 10 + i * 5
        )
        # Outer layer
        pygame.draw.circle(explosion, (200, 50, 0, 150 - i * 20), (30, 30), 15 + i * 6)
        explosion_imgs.append(explosion)

    # Create rocks - all decorative blue rocks now
    rocks = []

    # Create medium rocks
    for _ in range(ROCK_COUNT):
        size = random.randint(25, 40)
        x = random.randint(0, SCREEN_WIDTH - size)
        y = random.randint(0, SCREEN_HEIGHT - size)
        rocks.append(Rock(x, y, size, is_obstacle=False))

    # Create small rocks
    for _ in range(SMALL_ROCK_COUNT):
        size = random.randint(10, 20)
        x = random.randint(0, SCREEN_WIDTH - size)
        y = random.randint(0, SCREEN_HEIGHT - size)
        rocks.append(Rock(x, y, size, is_obstacle=False))


# Player class
class Player:
    def __init__(self):
        """Initialize the player at the center of the screen."""
        self.x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2 - PLAYER_HEIGHT // 2
        self.health = 100
        self.score = 0
        self.direction = "right"  # Default direction player is facing
        self.mouse_x = 0  # Track mouse position
        self.mouse_y = 0
        self.angle = 0  # Angle to mouse cursor

        # Power-up states
        self.active_powerups = {
            "AI Assistant": 0,
            "Speed Boost": 0,
            "Shield": 0,
            "Rapid Fire": 0,
        }
        self.base_speed = PLAYER_SPEED
        self.speed = self.base_speed
        self.shoot_cooldown = 0
        self.base_cooldown = 10

    def update_aim(self, mouse_x, mouse_y):
        """Update the aim direction based on mouse position."""
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

        # Calculate angle to mouse cursor
        dx = mouse_x - (self.x + PLAYER_WIDTH // 2)
        dy = mouse_y - (self.y + PLAYER_HEIGHT // 2)
        self.angle = math.atan2(dy, dx)

        # Update direction for player sprite rotation
        if -math.pi / 4 <= self.angle < math.pi / 4:
            self.direction = "right"
        elif math.pi / 4 <= self.angle < 3 * math.pi / 4:
            self.direction = "down"
        elif -3 * math.pi / 4 <= self.angle < -math.pi / 4:
            self.direction = "up"
        else:
            self.direction = "left"

    def move(self, direction):
        """Move the player in four directions within screen bounds."""
        if direction == "left" and self.x > 0:
            self.x -= PLAYER_SPEED
        elif direction == "right" and self.x < SCREEN_WIDTH - PLAYER_WIDTH:
            self.x += PLAYER_SPEED
        elif direction == "up" and self.y > 0:
            self.y -= PLAYER_SPEED
        elif direction == "down" and self.y < SCREEN_HEIGHT - PLAYER_HEIGHT:
            self.y += PLAYER_SPEED

        self.direction = direction

    def shoot(self):
        """Create a bullet at the player's position aimed at the mouse cursor."""
        bullet_x = self.x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
        bullet_y = self.y + PLAYER_HEIGHT // 2 - BULLET_HEIGHT // 2

        # Create multiple bullets if Rapid Fire is active
        bullets = []
        if self.active_powerups["Rapid Fire"] > 0:
            # Create 3 bullets with slight spread
            for i in range(-1, 2):
                spread_angle = self.angle + (i * 0.1)  # Small angle spread
                bullets.append(Bullet(bullet_x, bullet_y, spread_angle))
        else:
            bullets.append(Bullet(bullet_x, bullet_y, self.angle))

        return bullets

    def draw(self):
        """Draw the player using the player image."""
        # Create a rotated version based on direction
        if self.direction == "right":
            rotated_img = player_img
        elif self.direction == "left":
            rotated_img = pygame.transform.flip(player_img, True, False)
        elif self.direction == "up":
            rotated_img = pygame.transform.rotate(player_img, 90)
        else:  # down
            rotated_img = pygame.transform.rotate(player_img, -90)

        screen.blit(rotated_img, (self.x, self.y))

    def apply_powerup(self, powerup):
        self.active_powerups[powerup.name] = powerup.duration

        # Apply immediate effects
        if powerup.name == "Speed Boost":
            self.speed = self.base_speed * 1.5

        return f"{powerup.name} activated!"

    def update_powerups(self):
        # Update all active power-ups
        for name in self.active_powerups:
            if self.active_powerups[name] > 0:
                self.active_powerups[name] -= 1

                # Handle expiration
                if self.active_powerups[name] <= 0:
                    if name == "Speed Boost":
                        self.speed = self.base_speed

    def take_damage(self, amount):
        """Reduce player health when hit by a zombie."""
        # If Shield is active, don't take damage
        if self.active_powerups["Shield"] > 0:
            play_sound("shield_hit")
            return

        self.health -= amount
        play_sound("player_damage")

        if self.health <= 0:
            self.health = 0
            play_sound("game_over")
            return True  # Player is dead
        return False


# Zombie class
class Zombie:
    def __init__(self):
        """Initialize a zombie at a random edge of the screen."""
        # Randomly choose which edge to spawn from
        edge = random.choice(["top", "right", "bottom", "left"])

        if edge == "top":
            self.x = random.randint(0, SCREEN_WIDTH - ZOMBIE_WIDTH)
            self.y = -ZOMBIE_HEIGHT
        elif edge == "right":
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT - ZOMBIE_HEIGHT)
        elif edge == "bottom":
            self.x = random.randint(0, SCREEN_WIDTH - ZOMBIE_WIDTH)
            self.y = SCREEN_HEIGHT
        else:  # left
            self.x = -ZOMBIE_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT - ZOMBIE_HEIGHT)

        self.speed = ZOMBIE_SPEED  # Default speed that can be modified

    def move(self, target_x, target_y):
        # Calculate direction to player
        dx = target_x - (self.x + ZOMBIE_WIDTH // 2)
        dy = target_y - (self.y + ZOMBIE_HEIGHT // 2)

        # Normalize the direction
        length = max(0.1, math.sqrt(dx * dx + dy * dy))
        dx /= length
        dy /= length

        # Move towards player with the zombie's current speed
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Update direction for animation
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

    def draw(self):
        """Draw the zombie using the zombie image."""
        screen.blit(zombie_img, (self.x, self.y))


# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        """Create a bullet at the given position with the given angle."""
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.color = BULLET_COLOR  # Default color, can be changed for AI bullets

    def move(self):
        """Move the bullet in the direction of its angle."""
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self):
        """Draw the bullet on the screen."""
        # Use the bullet's color (which might be changed for AI bullets)
        pygame.draw.rect(
            screen, self.color, (self.x, self.y, BULLET_WIDTH, BULLET_HEIGHT)
        )

        # Add a small glow effect for bullets
        glow_surf = pygame.Surface(
            (BULLET_WIDTH + 4, BULLET_HEIGHT + 4), pygame.SRCALPHA
        )
        pygame.draw.rect(
            glow_surf, (*self.color, 100), (0, 0, BULLET_WIDTH + 4, BULLET_HEIGHT + 4)
        )
        screen.blit(glow_surf, (self.x - 2, self.y - 2))


# Add these classes for visual effects
class BloodSplatter:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = len(blood_splatter_imgs)
        self.frame_delay = 3
        self.frame_counter = 0

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame += 1
            self.frame_counter = 0
        return self.frame < self.max_frames

    def draw(self):
        if self.frame < self.max_frames:
            screen.blit(blood_splatter_imgs[self.frame], (self.x - 20, self.y - 20))


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.max_frames = len(explosion_imgs)
        self.frame_delay = 2
        self.frame_counter = 0

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame += 1
            self.frame_counter = 0
        return self.frame < self.max_frames

    def draw(self):
        if self.frame < self.max_frames:
            screen.blit(explosion_imgs[self.frame], (self.x - 30, self.y - 30))


# Text input class for email entry
class TextInput:
    def __init__(self, x, y, width, height, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (100, 100, 100)
        self.active_color = (150, 150, 255)
        self.text_color = (255, 255, 255)
        self.active = False
        self.text = ""
        self.font = pygame.font.SysFont("arial", font_size)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 30  # Frames between cursor blinks

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state if clicked
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True  # Signal that Enter was pressed
            elif event.unicode.isprintable():
                self.text += event.unicode
        return False

    def update(self):
        # Update cursor blink
        self.cursor_timer += 1
        if self.cursor_timer >= self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface):
        # Draw the text input box
        color = self.active_color if self.active else self.color
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)

        # Render text
        text_surface = self.font.render(self.text, True, self.text_color)

        # Calculate text position (centered vertically, left-aligned with padding)
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surface.get_height()) // 2

        # Draw text
        surface.blit(text_surface, (text_x, text_y))

        # Draw cursor when active
        if self.active and self.cursor_visible:
            cursor_x = text_x + text_surface.get_width()
            cursor_y = text_y
            cursor_height = text_surface.get_height()
            pygame.draw.line(
                surface,
                self.text_color,
                (cursor_x, cursor_y),
                (cursor_x, cursor_y + cursor_height),
                2,
            )

    def is_valid_email(self):
        # Simple email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, self.text) is not None


# Function to submit score to leaderboard
def submit_score_to_leaderboard(email, score):
    if supabase is None:
        print(f"Offline mode: Would submit score {score} for {email}")
        return True

    try:
        # Insert the score into the scores table with correct column names
        data = (
            supabase.table("scores")
            .insert({"player_name": "Player", "email": email, "score": score})
            .execute()
        )
        print(f"Score submitted: {score} for {email}")
        return True
    except Exception as e:
        print(f"Error submitting score: {e}")
        return False


# Function to get top scores from leaderboard
def get_leaderboard():
    if supabase is None:
        # Return placeholder data in offline mode
        return [
            {"email": "example1@example.com", "score": 1000},
            {"email": "example2@example.com", "score": 800},
            {"email": "example3@example.com", "score": 600},
            {"email": "example4@example.com", "score": 400},
            {"email": "example5@example.com", "score": 200},
        ]

    try:
        # Get top 10 scores, ordered by score descending with correct column names
        response = (
            supabase.table("scores")
            .select("email,score")
            .order("score", desc=True)
            .limit(10)
            .execute()
        )
        return response.data
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []


# Function to mask email for privacy
def mask_email(email):
    if not email or "@" not in email:
        return email

    parts = email.split("@")
    username = parts[0]
    domain = parts[1]

    # Keep first character, mask the rest until @
    if len(username) > 1:
        masked_username = username[0] + "*" * (len(username) - 1)
    else:
        masked_username = username

    return f"{masked_username}@{domain}"


# Email input screen
def show_email_input_screen(score):
    email_input = TextInput(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 40)

    title_font = pygame.font.SysFont("arial", 36)
    instruction_font = pygame.font.SysFont("arial", 20)
    error_font = pygame.font.SysFont("arial", 18)

    title_text = title_font.render(f"Your Score: {score}", True, (0, 200, 255))
    instruction_text = instruction_font.render(
        "Enter your email for the leaderboard:", True, (200, 200, 200)
    )
    privacy_text = error_font.render(
        "Your email will be partially hidden on the leaderboard", True, (150, 150, 150)
    )
    error_text = error_font.render(
        "Please enter a valid email address", True, (255, 100, 100)
    )

    submit_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 60, 200, 40
    )
    submit_text = instruction_font.render("Submit", True, (255, 255, 255))

    skip_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 120, 200, 40
    )
    skip_text = instruction_font.render("Skip", True, (200, 200, 200))

    show_error = False
    submitted = False

    while not submitted:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if email_input.handle_event(event):
                # Enter key was pressed
                if email_input.is_valid_email():
                    submit_score_to_leaderboard(email_input.text, score)
                    submitted = True
                else:
                    show_error = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if submit_button.collidepoint(event.pos):
                    if email_input.is_valid_email():
                        submit_score_to_leaderboard(email_input.text, score)
                        submitted = True
                    else:
                        show_error = True
                elif skip_button.collidepoint(event.pos):
                    submitted = True

        # Update
        email_input.update()

        # Draw
        # Background with grid effect
        screen.fill((5, 7, 15))
        for x in range(0, SCREEN_WIDTH, 40):
            alpha = 30 + 10 * math.sin(x / 100 + pygame.time.get_ticks() / 1000)
            pygame.draw.line(
                screen, (0, int(alpha), int(alpha * 2)), (x, 0), (x, SCREEN_HEIGHT)
            )

        for y in range(0, SCREEN_HEIGHT, 40):
            alpha = 30 + 10 * math.sin(y / 100 + pygame.time.get_ticks() / 1000)
            pygame.draw.line(
                screen, (0, int(alpha), int(alpha * 2)), (0, y), (SCREEN_WIDTH, y)
            )

        # Draw title and instructions
        screen.blit(
            title_text,
            (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3),
        )
        screen.blit(
            instruction_text,
            (
                SCREEN_WIDTH // 2 - instruction_text.get_width() // 2,
                SCREEN_HEIGHT // 2 - 50,
            ),
        )

        # Draw input field
        email_input.draw(screen)

        # Draw privacy notice
        screen.blit(
            privacy_text,
            (
                SCREEN_WIDTH // 2 - privacy_text.get_width() // 2,
                SCREEN_HEIGHT // 2 + 45,
            ),
        )

        # Draw error message if needed
        if show_error:
            screen.blit(
                error_text,
                (
                    SCREEN_WIDTH // 2 - error_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 + 180,
                ),
            )

        # Draw submit button
        button_color = (0, 120, 200) if email_input.is_valid_email() else (80, 80, 80)
        pygame.draw.rect(screen, button_color, submit_button, border_radius=5)
        screen.blit(
            submit_text,
            (
                submit_button.x + (submit_button.width - submit_text.get_width()) // 2,
                submit_button.y
                + (submit_button.height - submit_text.get_height()) // 2,
            ),
        )

        # Draw skip button
        pygame.draw.rect(screen, (50, 50, 50), skip_button, border_radius=5)
        screen.blit(
            skip_text,
            (
                skip_button.x + (skip_button.width - skip_text.get_width()) // 2,
                skip_button.y + (skip_button.height - skip_text.get_height()) // 2,
            ),
        )

        pygame.display.flip()

    # Show leaderboard after submission
    show_leaderboard_screen()
    return True


# Leaderboard display screen
def show_leaderboard_screen():
    leaderboard_data = get_leaderboard()

    title_font = pygame.font.SysFont("arial", 40)
    entry_font = pygame.font.SysFont("arial", 24)
    instruction_font = pygame.font.SysFont("arial", 20)

    title_text = title_font.render("LEADERBOARD", True, (0, 200, 255))
    instruction_text = instruction_font.render(
        "Press any key to continue", True, (200, 200, 200)
    )

    # Animation variables
    entry_positions = [SCREEN_WIDTH for _ in range(len(leaderboard_data))]
    target_positions = [SCREEN_WIDTH // 2 - 150 for _ in range(len(leaderboard_data))]

    waiting = True
    clock = pygame.time.Clock()

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

        # Update entry animations
        for i in range(len(entry_positions)):
            # Stagger the animations
            if i > 0 and entry_positions[i - 1] > target_positions[i - 1] + 100:
                continue

            # Move entries toward their target positions
            if entry_positions[i] > target_positions[i]:
                entry_positions[i] -= (entry_positions[i] - target_positions[i]) * 0.1
                if entry_positions[i] < target_positions[i] + 1:
                    entry_positions[i] = target_positions[i]

        # Draw
        # Background with grid effect
        screen.fill((5, 7, 15))
        for x in range(0, SCREEN_WIDTH, 40):
            alpha = 30 + 10 * math.sin(x / 100 + pygame.time.get_ticks() / 1000)
            pygame.draw.line(
                screen, (0, int(alpha), int(alpha * 2)), (x, 0), (x, SCREEN_HEIGHT)
            )

        for y in range(0, SCREEN_HEIGHT, 40):
            alpha = 30 + 10 * math.sin(y / 100 + pygame.time.get_ticks() / 1000)
            pygame.draw.line(
                screen, (0, int(alpha), int(alpha * 2)), (0, y), (SCREEN_WIDTH, y)
            )

        # Draw title
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        # Draw leaderboard entries
        for i, entry in enumerate(leaderboard_data):
            rank = i + 1
            email = mask_email(entry["email"])
            score = entry["score"]

            # Determine color based on rank
            if rank == 1:
                color = (255, 215, 0)  # Gold
            elif rank == 2:
                color = (192, 192, 192)  # Silver
            elif rank == 3:
                color = (205, 127, 50)  # Bronze
            else:
                color = (200, 200, 200)  # White

            # Create entry text
            entry_text = entry_font.render(f"{rank}. {email}: {score}", True, color)

            # Draw entry with animation
            y_pos = 120 + i * 40
            screen.blit(entry_text, (entry_positions[i], y_pos))

            # Draw a subtle glow behind top 3
            if rank <= 3:
                glow_surf = pygame.Surface(
                    (entry_text.get_width() + 20, entry_text.get_height() + 10),
                    pygame.SRCALPHA,
                )
                glow_alpha = 100 - i * 20
                glow_color = (*color, glow_alpha)
                pygame.draw.rect(
                    glow_surf,
                    glow_color,
                    (0, 0, glow_surf.get_width(), glow_surf.get_height()),
                    border_radius=5,
                )
                screen.blit(glow_surf, (entry_positions[i] - 10, y_pos - 5))
                screen.blit(entry_text, (entry_positions[i], y_pos))

        # Draw instruction
        screen.blit(
            instruction_text,
            (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT - 50),
        )

        pygame.display.flip()
        clock.tick(60)

    return True


# Main game loop
def game_loop():
    """Run the main game loop."""
    clock = pygame.time.Clock()
    player = Player()
    zombies = []
    bullets = []
    zombie_spawn_timer = 0
    game_over = False
    powerup_timer = 0
    powerups = []
    mouse_cooldown = 0
    blood_splatters = []
    explosions = []
    message_text = ""
    message_timer = 0
    game_tick = 0  # Add a game tick counter

    # Wave system variables
    current_wave = 1
    wave_timer = 0
    wave_duration = 1800  # 30 seconds per wave at 60 FPS
    zombies_per_wave = 1  # Base number of zombies to spawn per second
    wave_message = ""
    wave_message_timer = 0

    while not game_over:
        # Increment game tick each frame
        game_tick += 1

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # Get mouse position and update player aim
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player.update_aim(mouse_x, mouse_y)

        # Handle mouse shooting with cooldown
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and mouse_cooldown <= 0:  # Left mouse button
            new_bullets = player.shoot()
            bullets.extend(new_bullets)
            # Set cooldown based on power-up status
            mouse_cooldown = 5 if player.active_powerups["Rapid Fire"] > 0 else 10
            play_sound("shoot")  # Play shooting sound

        if mouse_cooldown > 0:
            mouse_cooldown -= 1

        # Also keep keyboard shooting for those who prefer it
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and mouse_cooldown <= 0:
            bullets.extend(player.shoot())
            mouse_cooldown = 10
            play_sound("shoot")  # Play shooting sound

        # Handle player input
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move("left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move("right")
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move("up")
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move("down")

        # Replace the zombie spawning code with this wave-based system
        # Update wave timer
        wave_timer += 1
        if wave_timer >= wave_duration:
            current_wave += 1
            wave_timer = 0
            wave_message = f"Wave {current_wave} incoming!"
            wave_message_timer = 180  # Show for 3 seconds
            play_sound("wave_start")  # Play wave start sound

            # Increase difficulty with each wave
            zombies_per_wave = (
                1 + current_wave // 2
            )  # Increase zombies per second every 2 waves

        # Spawn zombies based on current wave
        zombie_spawn_timer += 1
        spawn_rate = max(
            10, 60 // zombies_per_wave
        )  # Adjust spawn rate based on zombies per wave
        if zombie_spawn_timer >= spawn_rate:  # Spawn rate increases with wave
            # Spawn multiple zombies at once in later waves
            zombies_to_spawn = (
                1 + current_wave // 3
            )  # Spawn more zombies at once in later waves
            for _ in range(zombies_to_spawn):
                new_zombie = Zombie()
                # Make zombies faster in later waves
                new_zombie.speed = min(
                    4.0, ZOMBIE_SPEED * (1 + current_wave * 0.1)
                )  # Cap at 4.0
                zombies.append(new_zombie)
            zombie_spawn_timer = 0

        # Update zombies and check collisions
        for zombie in zombies[:]:
            zombie.move(player.x + PLAYER_WIDTH // 2, player.y + PLAYER_HEIGHT // 2)

            # Check if zombie collides with player
            if (
                zombie.x < player.x + PLAYER_WIDTH
                and zombie.x + ZOMBIE_WIDTH > player.x
                and zombie.y < player.y + PLAYER_HEIGHT
                and zombie.y + ZOMBIE_HEIGHT > player.y
            ):
                # Add blood splatter effect
                blood_splatters.append(
                    BloodSplatter(
                        zombie.x + ZOMBIE_WIDTH // 2, zombie.y + ZOMBIE_HEIGHT // 2
                    )
                )

                zombies.remove(zombie)

                # Only take damage if shield is not active
                if player.active_powerups["Shield"] <= 0:
                    player.take_damage(25)  # Increased from 10 to 25 (4 hits to kill)
                    play_sound("player_damage")  # Play player damage sound
                else:
                    # Shield absorbs the hit
                    player.score += 5  # Bonus for blocking with shield
                    play_sound("shield_hit")  # Play shield hit sound
                continue

            # Check bullet collisions
            for bullet in bullets[:]:
                if (
                    zombie.x < bullet.x < zombie.x + ZOMBIE_WIDTH
                    and zombie.y < bullet.y < zombie.y + ZOMBIE_HEIGHT
                ):
                    # Add blood splatter effect
                    blood_splatters.append(
                        BloodSplatter(
                            zombie.x + ZOMBIE_WIDTH // 2, zombie.y + ZOMBIE_HEIGHT // 2
                        )
                    )
                    # Add explosion effect for the bullet impact
                    explosions.append(Explosion(bullet.x, bullet.y))

                    play_sound("zombie_hit")  # Play zombie hit sound

                    zombies.remove(zombie)
                    bullets.remove(bullet)
                    player.score += 10
                    break

        # Update bullets
        for bullet in bullets[:]:
            bullet.move()
            # Remove bullets that go off-screen
            if (
                bullet.x < 0
                or bullet.x > SCREEN_WIDTH
                or bullet.y < 0
                or bullet.y > SCREEN_HEIGHT
            ):
                bullets.remove(bullet)

        # Check for game over
        if player.health <= 0:
            game_over = True
            play_sound("game_over")  # Play game over sound

        # Update player power-ups
        player.update_powerups()

        # Spawn power-ups periodically
        powerup_timer += 1
        if powerup_timer >= 600:  # Every 10 seconds
            power_up_x = random.randint(50, SCREEN_WIDTH - 50)
            power_up_y = random.randint(50, SCREEN_HEIGHT - 50)

            # Make sure it doesn't spawn on a rock
            valid_position = True
            for rock in rocks:
                if rock.collides_with(power_up_x - 15, power_up_y - 15, 30, 30):
                    valid_position = False
                    break

            if valid_position:
                powerups.append(PowerUp(power_up_x, power_up_y))
                powerup_timer = 0

        # Check if player collects power-ups
        for powerup in powerups[:]:
            if (
                powerup.x - 20 < player.x + PLAYER_WIDTH // 2 < powerup.x + 20
                and powerup.y - 20 < player.y + PLAYER_HEIGHT // 2 < powerup.y + 20
            ):
                message_text = player.apply_powerup(powerup)
                message_timer = 120  # Show message for 2 seconds
                powerups.remove(powerup)
                play_sound("powerup")  # Play powerup sound

                # Special handling for AI Assistant
                if powerup.name == "AI Assistant" and zombies:
                    # Set the power-up as active, the actual shooting will happen in the main loop
                    player.active_powerups["AI Assistant"] = powerup.duration
                    message_text = "AI Assistant activated!"
                    message_timer = 120

        # Update power-ups
        for powerup in powerups:
            powerup.update()

        # Update visual effects
        for splatter in blood_splatters[:]:
            if not splatter.update():
                blood_splatters.remove(splatter)

        for explosion in explosions[:]:
            if not explosion.update():
                explosions.remove(explosion)

        # Draw background
        screen.blit(background_img, (0, 0))

        # Draw rocks
        for rock in rocks:
            rock.draw()

        # Draw visual effects under entities
        for splatter in blood_splatters:
            splatter.draw()

        # Draw entities
        player.draw()
        for zombie in zombies:
            zombie.draw()
        for bullet in bullets:
            bullet.draw()

        # Draw explosions on top
        for explosion in explosions:
            explosion.draw()

        # Draw health bar
        pygame.draw.rect(screen, RED, (10, 10, 200, 20))  # Background
        pygame.draw.rect(
            screen, GREEN, (10, 10, (player.health / 100) * 200, 20)  # Health
        )

        # Draw score
        score_text = SCORE_FONT.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Draw power-ups
        for powerup in powerups:
            powerup.draw()

        # Draw active power-up indicators
        active_powerup_count = 0
        for name, duration in player.active_powerups.items():
            if duration > 0:
                # Find the color for this power-up type
                color = next(
                    (p["color"] for p in POWERUP_TYPES if p["name"] == name),
                    (255, 255, 255),
                )

                # Draw indicator
                indicator_text = SCORE_FONT.render(
                    f"{name}: {duration//60}s", True, color
                )
                screen.blit(indicator_text, (10, 40 + active_powerup_count * 25))
                active_powerup_count += 1

        # Draw message if active
        if message_timer > 0:
            message_timer -= 1
            message_surf = SCORE_FONT.render(message_text, True, (255, 255, 255))
            # Fade out near the end
            if message_timer < 30:
                alpha = int(255 * (message_timer / 30))
                temp_surf = pygame.Surface(message_surf.get_size(), pygame.SRCALPHA)
                temp_surf.fill((255, 255, 255, alpha))
                message_surf.blit(
                    temp_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
                )

            screen.blit(
                message_surf, (SCREEN_WIDTH // 2 - message_surf.get_width() // 2, 50)
            )

        # Draw shield effect if active
        if player.active_powerups["Shield"] > 0:
            shield_radius = 25 + int(5 * math.sin(pygame.time.get_ticks() / 100))
            shield_surf = pygame.Surface(
                (shield_radius * 2, shield_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                shield_surf,
                (200, 0, 255, 100),
                (shield_radius, shield_radius),
                shield_radius,
                3,
            )
            screen.blit(
                shield_surf,
                (
                    player.x + PLAYER_WIDTH // 2 - shield_radius,
                    player.y + PLAYER_HEIGHT // 2 - shield_radius,
                ),
            )

        # AI Assistant logic - continuously target zombies while active
        if player.active_powerups["AI Assistant"] > 0:
            if (
                game_tick % 10 == 0
            ):  # Fire every 10 frames (6 times per second at 60 FPS)
                # Find the nearest zombie
                if zombies:
                    nearest_zombie = min(
                        zombies,
                        key=lambda z: ((z.x - player.x) ** 2 + (z.y - player.y) ** 2)
                        ** 0.5,
                    )

                    # Calculate direction to the zombie
                    dx = nearest_zombie.x - (player.x + PLAYER_WIDTH // 2)
                    dy = nearest_zombie.y - (player.y + PLAYER_HEIGHT // 2)

                    # Calculate angle
                    angle = math.atan2(dy, dx)

                    # Create a bullet
                    bullet_x = player.x + PLAYER_WIDTH // 2 - BULLET_WIDTH // 2
                    bullet_y = player.y + PLAYER_HEIGHT // 2 - BULLET_HEIGHT // 2

                    # Create the AI bullet with a special color
                    ai_bullet = Bullet(bullet_x, bullet_y, angle)
                    ai_bullet.color = (
                        0,
                        200,
                        255,
                    )  # Special color for AI bullets
                    bullets.append(ai_bullet)

                    # Visual effect for AI shooting
                    # Create a temporary line showing the targeting
                    pygame.draw.line(
                        screen,
                        (0, 200, 255, 150),
                        (
                            player.x + PLAYER_WIDTH // 2,
                            player.y + PLAYER_HEIGHT // 2,
                        ),
                        (
                            nearest_zombie.x + ZOMBIE_WIDTH // 2,
                            nearest_zombie.y + ZOMBIE_HEIGHT // 2,
                        ),
                        1,
                    )

        # Add this to the drawing section, after drawing the score
        # Draw wave number
        wave_text = SCORE_FONT.render(f"Wave: {current_wave}", True, (200, 200, 255))
        screen.blit(wave_text, (SCREEN_WIDTH - 150, 40))

        # Draw wave message if active
        if wave_message_timer > 0:
            wave_message_timer -= 1
            wave_msg_font = pygame.font.SysFont("arial", 36)
            wave_msg_surf = wave_msg_font.render(wave_message, True, (255, 100, 100))

            # Fade out near the end
            if wave_message_timer < 60:
                alpha = int(255 * (wave_message_timer / 60))
                temp_surf = pygame.Surface(wave_msg_surf.get_size(), pygame.SRCALPHA)
                temp_surf.fill((255, 255, 255, alpha))
                wave_msg_surf.blit(
                    temp_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
                )

            screen.blit(
                wave_msg_surf,
                (
                    SCREEN_WIDTH // 2 - wave_msg_surf.get_width() // 2,
                    SCREEN_HEIGHT // 3,
                ),
            )

        pygame.display.flip()
        clock.tick(FPS)

    # Display game over screen
    if show_game_over_screen(player.score):
        # Restart the game if the function returns True
        return True
    else:
        return False  # Return to title screen instead of restarting


def show_title_screen():
    """Display an AI-themed title screen with leaderboard option."""
    global SOUND_ENABLED, SOUND_VOLUME  # Declare globals at the beginning of the function

    title_screen = True
    title_font = pygame.font.SysFont("arial", 50)
    subtitle_font = pygame.font.SysFont("arial", 24)
    instruction_font = pygame.font.SysFont("arial", 18)

    # Create pulsing effect variables
    pulse_value = 0
    pulse_direction = 1

    # Create menu buttons
    start_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 40
    )
    leaderboard_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 130, 200, 40
    )

    start_text = subtitle_font.render("Start Game", True, (255, 255, 255))
    leaderboard_text = subtitle_font.render("Leaderboard", True, (255, 255, 255))

    # Create background elements
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill((10, 10, 20))

    # Draw grid lines with fading effect
    for x in range(0, SCREEN_WIDTH, 40):
        alpha = 30 + 10 * math.sin(x / 100 + pygame.time.get_ticks() / 1000)
        pygame.draw.line(
            screen, (0, int(alpha), int(alpha * 2)), (x, 0), (x, SCREEN_HEIGHT)
        )

    for y in range(0, SCREEN_HEIGHT, 40):
        alpha = 30 + 10 * math.sin(y / 100 + pygame.time.get_ticks() / 1000)
        pygame.draw.line(
            screen, (0, int(alpha), int(alpha * 2)), (0, y), (SCREEN_WIDTH, y)
        )

    # Add some glowing nodes at grid intersections
    for _ in range(15):
        x = random.randint(0, 16) * 40
        y = random.randint(0, 12) * 40
        size = random.randint(3, 6)
        pygame.draw.circle(background_img, (0, 150, 255, 150), (x, y), size)
        # Add glow effect
        pygame.draw.circle(background_img, (0, 100, 200, 50), (x, y), size * 2)

    while title_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    title_screen = False
                elif leaderboard_button.collidepoint(event.pos):
                    show_leaderboard_screen()

        # Update pulse effect
        pulse_value += 0.05 * pulse_direction
        if pulse_value >= 1.0:
            pulse_direction = -1
        elif pulse_value <= 0.0:
            pulse_direction = 1

        # Draw background
        screen.blit(background_img, (0, 0))

        # Draw title with glow effect
        title_text = title_font.render("AI ZOMBIE APOCALYPSE", True, (0, 200, 255))
        glow_surf = pygame.Surface(
            (title_text.get_width() + 20, title_text.get_height() + 20), pygame.SRCALPHA
        )

        # Pulsing glow effect
        glow_intensity = 128 + 64 * math.sin(pygame.time.get_ticks() / 500)
        pygame.draw.rect(
            glow_surf,
            (0, 150, 255, int(glow_intensity)),
            (0, 0, glow_surf.get_width(), glow_surf.get_height()),
            border_radius=10,
        )

        # Position title higher on screen
        title_y = SCREEN_HEIGHT // 4 - glow_surf.get_height() // 2

        screen.blit(
            glow_surf,
            (
                SCREEN_WIDTH // 2 - glow_surf.get_width() // 2,
                title_y,
            ),
        )
        screen.blit(
            title_text,
            (
                SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                title_y + 10,
            ),
        )

        # Draw subtitle with more space
        subtitle = subtitle_font.render(
            "Can your AI assistant save humanity?", True, (200, 200, 200)
        )
        screen.blit(
            subtitle,
            (
                SCREEN_WIDTH // 2 - subtitle.get_width() // 2,
                title_y + title_text.get_height() + 20,
            ),
        )

        # Draw instructions with proper spacing
        instructions = [
            "WASD or Arrow Keys to move",
            "Mouse to aim and shoot",
            "Collect AI power-ups for automated assistance",
            "Survive the zombie horde as long as possible",
        ]

        instruction_y = title_y + title_text.get_height() + subtitle.get_height() + 40

        for i, line in enumerate(instructions):
            instruction_text = instruction_font.render(line, True, (200, 200, 200))
            screen.blit(
                instruction_text,
                (
                    SCREEN_WIDTH // 2 - instruction_text.get_width() // 2,
                    instruction_y + i * 25,
                ),
            )

        # Draw buttons with hover effect
        mouse_pos = pygame.mouse.get_pos()

        # Start button
        start_color = (
            (0, 150, 250) if start_button.collidepoint(mouse_pos) else (0, 120, 200)
        )
        pygame.draw.rect(screen, start_color, start_button, border_radius=5)
        screen.blit(
            start_text,
            (
                start_button.x + (start_button.width - start_text.get_width()) // 2,
                start_button.y + (start_button.height - start_text.get_height()) // 2,
            ),
        )

        # Leaderboard button
        leaderboard_color = (
            (0, 130, 220)
            if leaderboard_button.collidepoint(mouse_pos)
            else (0, 100, 170)
        )
        pygame.draw.rect(screen, leaderboard_color, leaderboard_button, border_radius=5)
        screen.blit(
            leaderboard_text,
            (
                leaderboard_button.x
                + (leaderboard_button.width - leaderboard_text.get_width()) // 2,
                leaderboard_button.y
                + (leaderboard_button.height - leaderboard_text.get_height()) // 2,
            ),
        )
        pygame.display.flip()
        pygame.time.Clock().tick(60)


def show_game_over_screen(score):
    """Display an enhanced game over screen with integrated email input."""
    screen.fill((5, 7, 15))  # Dark background

    email = ""
    input_active = True
    submitted = False
    message = ""

    # Create input box
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40, 300, 40)
    submit_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 40
    )
    skip_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 150, 200, 40
    )

    # Fonts
    game_over_font = pygame.font.SysFont("arial", 60, bold=True)
    score_font = pygame.font.SysFont("arial", 36)
    input_font = pygame.font.SysFont("arial", 24)
    button_font = pygame.font.SysFont("arial", 24)
    message_font = pygame.font.SysFont("arial", 18)
    note_font = pygame.font.SysFont("arial", 12)  # Even smaller for better fit

    # Render button text
    submit_text = button_font.render("Submit", True, WHITE)
    skip_text = button_font.render("Skip", True, WHITE)

    # Email validation regex
    email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    # Calculate optimal spacing - move title higher to create more space
    title_y = SCREEN_HEIGHT // 8  # Move even higher
    spacing = 20  # Reduce spacing further

    # Adjust positions based on title_y
    email_prompt_y = title_y + 120  # Position for the email prompt text
    input_box.y = (
        email_prompt_y + 30
    )  # Position input box below the prompt with enough space
    submit_button.y = input_box.y + input_box.height + spacing
    skip_button.y = submit_button.y + submit_button.height + spacing

    # Main loop
    waiting = True
    clock = pygame.time.Clock()

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if input box clicked
                if input_box.collidepoint(event.pos):
                    input_active = True
                # Check if submit button clicked
                elif submit_button.collidepoint(event.pos) and email:
                    if email_regex.match(email):
                        # Submit score to leaderboard
                        if submit_score_to_leaderboard(email, score):
                            message = "Score submitted successfully!"
                            submitted = True
                            waiting = False
                        else:
                            message = "Error submitting score. Please try again."
                    else:
                        message = "Please enter a valid email address."
                # Check if skip button clicked
                elif skip_button.collidepoint(event.pos):
                    waiting = False

            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        # Submit on Enter key
                        if email and email_regex.match(email):
                            if submit_score_to_leaderboard(email, score):
                                message = "Score submitted successfully!"
                                submitted = True
                                waiting = False
                            else:
                                message = "Error submitting score. Please try again."
                        else:
                            message = "Please enter a valid email address."
                    elif event.key == pygame.K_BACKSPACE:
                        email = email[:-1]
                    else:
                        # Add character to email if it's a valid character
                        if len(email) < 30 and event.unicode.isprintable():
                            email += event.unicode

        # Draw background with grid effect
        screen.fill((5, 7, 15))
        for x in range(0, SCREEN_WIDTH, 20):
            alpha = 50 + 20 * math.sin(x / 100 + pygame.time.get_ticks() / 1000)
            pygame.draw.line(
                screen, (0, 100, 200, int(alpha)), (x, 0), (x, SCREEN_HEIGHT)
            )

        for y in range(0, SCREEN_HEIGHT, 20):
            alpha = 50 + 20 * math.sin(y / 100 + pygame.time.get_ticks() / 1000)
            pygame.draw.line(
                screen, (0, 100, 200, int(alpha)), (0, y), (SCREEN_WIDTH, y)
            )

        # Game Over text with glow
        game_over_text = game_over_font.render("GAME OVER", True, (0, 200, 255))
        glow_surf = pygame.Surface(
            (game_over_text.get_width() + 20, game_over_text.get_height() + 20),
            pygame.SRCALPHA,
        )

        # Pulsing glow effect
        glow_intensity = 128 + 64 * math.sin(pygame.time.get_ticks() / 500)
        pygame.draw.rect(
            glow_surf,
            (0, 150, 255, int(glow_intensity)),
            (0, 0, glow_surf.get_width(), glow_surf.get_height()),
            border_radius=10,
        )

        # Draw the glowing background and text
        screen.blit(
            glow_surf,
            (
                SCREEN_WIDTH // 2 - glow_surf.get_width() // 2,
                title_y - glow_surf.get_height() // 2,
            ),
        )
        screen.blit(
            game_over_text,
            (
                SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                title_y - game_over_text.get_height() // 2,
            ),
        )

        # Score text
        score_text = score_font.render(f"Your Score: {score}", True, (200, 255, 255))
        screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, title_y + 70),
        )

        # Email input prompt - positioned with more space above the input box
        email_prompt = input_font.render(
            "Enter your email for the leaderboard:", True, WHITE
        )
        screen.blit(
            email_prompt,
            (SCREEN_WIDTH // 2 - email_prompt.get_width() // 2, email_prompt_y),
        )

        # Draw input box with different color when active
        input_color = (0, 150, 255) if input_active else (100, 100, 100)
        pygame.draw.rect(screen, input_color, input_box, 2, border_radius=5)

        # Render and display the email text
        email_surface = input_font.render(email, True, WHITE)
        screen.blit(email_surface, (input_box.x + 10, input_box.y + 10))

        # Draw cursor when input is active
        if input_active and int(pygame.time.get_ticks() / 500) % 2 == 0:
            cursor_pos = input_box.x + 10 + email_surface.get_width()
            pygame.draw.line(
                screen,
                WHITE,
                (cursor_pos, input_box.y + 10),
                (cursor_pos, input_box.y + 30),
                2,
            )

        # Draw submit button with hover effect
        mouse_pos = pygame.mouse.get_pos()
        submit_color = (
            (0, 150, 250) if submit_button.collidepoint(mouse_pos) else (100, 100, 100)
        )
        pygame.draw.rect(screen, submit_color, submit_button, border_radius=5)
        screen.blit(
            submit_text,
            (
                submit_button.x + (submit_button.width - submit_text.get_width()) // 2,
                submit_button.y
                + (submit_button.height - submit_text.get_height()) // 2,
            ),
        )

        # Draw skip button
        skip_color = (
            (100, 100, 100) if skip_button.collidepoint(mouse_pos) else (80, 80, 80)
        )
        pygame.draw.rect(screen, skip_color, skip_button, border_radius=5)
        screen.blit(
            skip_text,
            (
                skip_button.x + (skip_button.width - skip_text.get_width()) // 2,
                skip_button.y + (skip_button.height - skip_text.get_height()) // 2,
            ),
        )

        # Split the newsletter message into two shorter lines
        newsletter_note = note_font.render(
            "By submitting, you're signing up for the HackerHall newsletter",
            True,
            (180, 180, 180),
        )
        screen.blit(
            newsletter_note,
            (
                SCREEN_WIDTH // 2 - newsletter_note.get_width() // 2,
                skip_button.y + skip_button.height + 12,
            ),
        )

        # Privacy note on a separate line
        privacy_note = note_font.render(
            "Your email will be partially hidden on the leaderboard",
            True,
            (180, 180, 180),
        )
        screen.blit(
            privacy_note,
            (
                SCREEN_WIDTH // 2 - privacy_note.get_width() // 2,
                skip_button.y + skip_button.height + 28,
            ),
        )

        # Prize claim note with emphasis
        prize_note = note_font.render(
            "Use a real email to claim your prize if you win!",
            True,
            (255, 220, 100),  # Gold color for emphasis
        )
        screen.blit(
            prize_note,
            (
                SCREEN_WIDTH // 2 - prize_note.get_width() // 2,
                skip_button.y + skip_button.height + 44,
            ),
        )

        # Display message if any
        if message:
            message_surface = message_font.render(
                message,
                True,
                (255, 200, 200) if "Error" in message else (200, 255, 200),
            )
            screen.blit(
                message_surface,
                (
                    SCREEN_WIDTH // 2 - message_surface.get_width() // 2,
                    skip_button.y + skip_button.height + 64,
                ),
            )

        pygame.display.flip()
        clock.tick(60)

        # If submitted, wait a moment then continue
        if submitted:
            pygame.time.delay(1500)
            if random.random() < 0.5:  # 50% chance to show leaderboard first
                show_leaderboard_screen()
            return False  # Return to title screen instead of restarting

    # If skipped, just return to title screen
    return False  # Return to title screen instead of restarting


# Update the Rock class to use blue colors
class Rock:
    def __init__(self, x, y, size, is_obstacle=False):
        self.x = x
        self.y = y
        self.size = size
        self.is_obstacle = is_obstacle  # Always False now
        self.color = (40, 80, 120)  # Blue-gray color for rocks

        # Create a detailed rock surface
        self.surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Base rock shape
        pygame.draw.circle(self.surface, self.color, (size // 2, size // 2), size // 2)

        # Add some texture/details to the rock with blue tones
        for _ in range(5):
            detail_x = random.randint(size // 4, 3 * size // 4)
            detail_y = random.randint(size // 4, 3 * size // 4)
            detail_size = random.randint(size // 8, size // 4)
            # Use blue color variations
            detail_color = (
                random.randint(30, 60),  # Dark blue
                random.randint(70, 120),  # Medium blue
                random.randint(140, 200),  # Light blue
            )
            pygame.draw.circle(
                self.surface, detail_color, (detail_x, detail_y), detail_size
            )

        # Add highlights with cyan glow
        highlight_pos = (size // 3, size // 3)
        pygame.draw.circle(self.surface, (100, 200, 255), highlight_pos, size // 8)

        # Add subtle glow effect
        glow = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            glow, (0, 150, 255, 30), (size // 2, size // 2), size // 2 + 2
        )
        self.surface.blit(glow, (0, 0))

        # Create a collision rect - but it won't be used for collision detection
        self.rect = pygame.Rect(x, y, size, size)

    def draw(self):
        # Add a subtle pulsing effect to match the environment
        pulse = math.sin(pygame.time.get_ticks() / 1000) * 0.2 + 0.8
        temp_surf = self.surface.copy()

        # Apply pulsing to the highlights
        if random.random() < 0.01:  # Occasional stronger pulse
            glow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(
                glow,
                (0, 200, 255, 40),
                (self.size // 2, self.size // 2),
                self.size // 2 + 4,
            )
            temp_surf.blit(glow, (0, 0))

        screen.blit(temp_surf, (self.x, self.y))

    def collides_with(self, x, y, width, height):
        # Always return False - no collision detection
        return False


# Add this class for power-ups
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(POWERUP_TYPES)
        self.name = self.type["name"]
        self.color = self.type["color"]
        self.duration = self.type["duration"]
        self.pulse = 0
        self.pulse_dir = 1

    def update(self):
        # Update pulse animation
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse >= 1.0:
            self.pulse_dir = -1
        elif self.pulse <= 0.0:
            self.pulse_dir = 1

    def draw(self):
        # Draw glowing orb
        glow_size = 15 + int(5 * math.sin(pygame.time.get_ticks() / 200))

        # Outer glow
        for radius in range(glow_size, glow_size - 10, -2):
            alpha = max(0, 150 - (glow_size - radius) * 30)
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf, (*self.color, alpha), (radius, radius), radius
            )
            screen.blit(glow_surf, (self.x - radius, self.y - radius))

        # Core
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 6)

        # Symbol based on power-up type
        if self.name == "AI Assistant":
            # AI symbol (resembling a circuit)
            pygame.draw.line(
                screen, (255, 255, 255), (self.x - 4, self.y), (self.x + 4, self.y), 2
            )
            pygame.draw.line(
                screen, (255, 255, 255), (self.x, self.y - 4), (self.x, self.y + 4), 2
            )
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 2)
        elif self.name == "Speed Boost":
            # Lightning bolt symbol
            points = [
                (self.x - 3, self.y - 5),
                (self.x + 1, self.y - 1),
                (self.x - 1, self.y + 1),
                (self.x + 3, self.y + 5),
            ]
            pygame.draw.lines(screen, (255, 255, 255), False, points, 2)
        elif self.name == "Shield":
            # Shield symbol
            pygame.draw.arc(
                screen,
                (255, 255, 255),
                (self.x - 5, self.y - 5, 10, 10),
                math.pi * 0.75,
                math.pi * 2.25,
                2,
            )
        elif self.name == "Rapid Fire":
            # Rapid fire symbol
            pygame.draw.circle(screen, (255, 255, 255), (self.x - 2, self.y), 1)
            pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 1)
            pygame.draw.circle(screen, (255, 255, 255), (self.x + 2, self.y), 1)


# Modify your game_loop function to be async-compatible
async def async_game_loop():
    """Async version of game_loop for browser compatibility"""
    # Create game objects - same as in game_loop
    clock = pygame.time.Clock()
    player = Player()
    zombies = []
    bullets = []
    zombie_spawn_timer = 0
    game_over = False
    powerup_timer = 0
    powerups = []
    mouse_cooldown = 0
    blood_splatters = []
    explosions = []
    message_text = ""
    message_timer = 0
    game_tick = 0

    # Wave system variables
    current_wave = 1
    wave_timer = 0
    wave_duration = 1800
    zombies_per_wave = 1
    wave_message = ""
    wave_message_timer = 0

    # Create rocks
    rocks = []
    for _ in range(ROCK_COUNT):
        size = random.randint(30, 50)
        x = random.randint(0, SCREEN_WIDTH - size)
        y = random.randint(0, SCREEN_HEIGHT - size)
        rocks.append(Rock(x, y, size, False))  # No obstacles

    for _ in range(SMALL_ROCK_COUNT):
        size = random.randint(10, 25)
        x = random.randint(0, SCREEN_WIDTH - size)
        y = random.randint(0, SCREEN_HEIGHT - size)
        rocks.append(Rock(x, y, size, False))

    while not game_over:
        # Allow browser to update
        await asyncio.sleep(0)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get input state
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Rest of your game loop code - copy from game_loop but add await asyncio.sleep(0) periodically

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    # Game over handling
    if show_game_over_screen(player.score):
        return True
    else:
        return False


# Create an async version of your main function
async def async_main():
    """Async version of main for browser compatibility"""
    global player_img, zombie_img, bullet_img, background_img, blood_splatter_imgs, explosion_imgs, rocks

    print("Starting async_main for browser")
    browser_debug_info()  # Print debug info

    # Initialize game assets
    await initialize_images_async()

    while True:
        # Show title screen and wait for player to start
        restart = await async_show_title_screen()
        if restart:
            # Run game loop
            play_again = await async_game_loop()
            if not play_again:
                # If player doesn't want to play again, show title screen
                continue

        # Allow browser to update
        await asyncio.sleep(0)


# Create an async version of initialize_images
async def initialize_images_async():
    """Async version of initialize_images for browser compatibility"""
    global player_img, zombie_img, bullet_img, background_img, blood_splatter_imgs, explosion_imgs, rocks

    print("Initializing images in async mode")

    # Load sounds with browser compatibility
    if not IN_BROWSER:
        load_sounds()
        ensure_sound_directory()
        play_background_music()
    else:
        # Simplified sound loading for browser
        try:
            load_sounds()
            print("Sounds loaded in browser mode")
        except Exception as e:
            print(f"Error loading sounds in browser: {e}")

    # Create player image
    player_img = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(player_img, (40, 90, 180), (6, 6, 20, 20), border_radius=3)
    pygame.draw.circle(player_img, (0, 200, 255, 200), (16, 16), 5)

    # Create zombie image
    zombie_img = pygame.Surface((ZOMBIE_WIDTH, ZOMBIE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(zombie_img, (100, 150, 50), (6, 6, 20, 20), border_radius=3)

    # Create bullet image
    bullet_img = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(
        bullet_img,
        (255, 100, 50),
        (BULLET_WIDTH // 2, BULLET_HEIGHT // 2),
        BULLET_WIDTH // 2,
    )

    # Create background
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background_img.fill((10, 10, 20))

    # Create blood splatter images
    blood_splatter_imgs = []
    for _ in range(3):
        img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(img, (150, 0, 0, 200), (10, 10), random.randint(5, 10))
        blood_splatter_imgs.append(img)

    # Create explosion images
    explosion_imgs = []
    for size in range(5, 20, 5):
        img = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(img, (255, 200, 50, 200), (size, size), size)
        explosion_imgs.append(img)

    # Allow browser to update
    await asyncio.sleep(0)
    print("Async image initialization complete")


# Create a proper async version of the title screen
async def async_show_title_screen():
    """Async version of show_title_screen for browser compatibility"""
    global SOUND_ENABLED, SOUND_VOLUME, MUSIC_ENABLED

    print("Showing async title screen")
    title_screen = True
    title_font = pygame.font.SysFont("arial", 50)
    subtitle_font = pygame.font.SysFont("arial", 24)

    # Create buttons
    start_button = pygame.Rect(
        SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 40
    )
    start_text = subtitle_font.render("Start Game", True, (255, 255, 255))

    # Background
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill((10, 10, 20))

    # Main loop
    while title_screen:
        # Allow browser to update
        await asyncio.sleep(0)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    title_screen = False
                    return True

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Draw background
        screen.blit(background, (0, 0))

        # Draw title
        title_text = title_font.render("Zombie Shooter", True, (0, 200, 255))
        screen.blit(
            title_text,
            (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 4),
        )

        # Draw start button
        start_color = (
            (0, 150, 250) if start_button.collidepoint(mouse_pos) else (0, 120, 200)
        )
        pygame.draw.rect(screen, start_color, start_button, border_radius=5)
        screen.blit(
            start_text,
            (
                start_button.x + (start_button.width - start_text.get_width()) // 2,
                start_button.y + (start_button.height - start_text.get_height()) // 2,
            ),
        )

        # Update display
        pygame.display.flip()

    return True


# Update the async_game_loop to be a complete implementation
async def async_game_loop():
    """Complete async version of game_loop for browser compatibility"""
    print("Starting async game loop")

    # Create game objects
    clock = pygame.time.Clock()
    player = Player()
    zombies = []
    bullets = []
    zombie_spawn_timer = 0
    game_over = False

    # Wave system variables
    current_wave = 1
    wave_timer = 0
    wave_duration = 1800  # 30 seconds at 60 FPS
    zombies_per_wave = 1

    # Main game loop
    while not game_over:
        # Allow browser to update
        await asyncio.sleep(0)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Get input state
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Move player based on keyboard input
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            player.move("up")
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            player.move("down")
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.move("right")

        # Shoot bullets
        if mouse_buttons[0]:  # Left mouse button
            new_bullet = Bullet(
                player.x + PLAYER_WIDTH // 2,
                player.y + PLAYER_HEIGHT // 2,
                mouse_pos[0],
                mouse_pos[1],
            )
            bullets.append(new_bullet)
            play_sound("shoot")

        # Update wave timer
        wave_timer += 1
        if wave_timer >= wave_duration:
            current_wave += 1
            wave_timer = 0
            play_sound("wave_start")
            zombies_per_wave = 1 + current_wave // 2

        # Spawn zombies
        zombie_spawn_timer += 1
        spawn_rate = max(10, 60 // zombies_per_wave)
        if zombie_spawn_timer >= spawn_rate:
            zombies_to_spawn = 1 + current_wave // 3
            for _ in range(zombies_to_spawn):
                new_zombie = Zombie()
                new_zombie.speed = min(4.0, ZOMBIE_SPEED * (1 + current_wave * 0.1))
                zombies.append(new_zombie)
            zombie_spawn_timer = 0

        # Update zombies
        for zombie in zombies[:]:
            zombie.move(player.x + PLAYER_WIDTH // 2, player.y + PLAYER_HEIGHT // 2)

            # Check collision with player
            if (
                zombie.x < player.x + PLAYER_WIDTH
                and zombie.x + ZOMBIE_WIDTH > player.x
                and zombie.y < player.y + PLAYER_HEIGHT
                and zombie.y + ZOMBIE_HEIGHT > player.y
            ):
                zombies.remove(zombie)
                player.take_damage(25)
                play_sound("player_damage")
                if player.health <= 0:
                    game_over = True
                    play_sound("game_over")

        # Update bullets
        for bullet in bullets[:]:
            bullet.move()

            # Remove bullets that go off screen
            if (
                bullet.x < 0
                or bullet.x > SCREEN_WIDTH
                or bullet.y < 0
                or bullet.y > SCREEN_HEIGHT
            ):
                bullets.remove(bullet)
                continue

            # Check bullet collisions with zombies
            for zombie in zombies[:]:
                if (
                    zombie.x < bullet.x < zombie.x + ZOMBIE_WIDTH
                    and zombie.y < bullet.y < zombie.y + ZOMBIE_HEIGHT
                ):
                    zombies.remove(zombie)
                    bullets.remove(bullet)
                    player.score += 10
                    play_sound("zombie_hit")
                    break

        # Draw everything
        screen.fill((10, 10, 20))

        # Draw player
        screen.blit(player_img, (player.x, player.y))

        # Draw zombies
        for zombie in zombies:
            screen.blit(zombie_img, (zombie.x, zombie.y))

        # Draw bullets
        for bullet in bullets:
            screen.blit(bullet_img, (bullet.x, bullet.y))

        # Draw UI
        health_text = SCORE_FONT.render(
            f"Health: {player.health}", True, (255, 255, 255)
        )
        score_text = SCORE_FONT.render(f"Score: {player.score}", True, (255, 255, 255))
        wave_text = SCORE_FONT.render(f"Wave: {current_wave}", True, (200, 200, 255))

        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 40))
        screen.blit(wave_text, (SCREEN_WIDTH - 150, 40))

        # Update display
        pygame.display.flip()
        clock.tick(FPS)

    # Game over
    print("Game over, score:", player.score)
    return False  # Don't restart automatically


# Move the test_sound_system function definition to before it's called
# Add this function before initialize_images
def test_sound_system():
    """Test if the sound system is working properly."""
    global SOUND_ENABLED

    # Initialize SOUND_ENABLED if not already defined
    if "SOUND_ENABLED" not in globals():
        global SOUND_ENABLED
        SOUND_ENABLED = True

    try:
        # Create a simple test sound
        test_sound = pygame.mixer.Sound(
            pygame.sndarray.array(np.ones((1000, 2)) * 32767 * 0.1)
        )
        test_sound.set_volume(0.1)  # Very quiet
        test_sound.play()
        pygame.time.wait(100)  # Wait a bit for the sound to play
        print("Sound system test successful.")
        return True
    except Exception as e:
        print(f"Sound system test failed: {e}")
        SOUND_ENABLED = False
        return False


# Add this after the load_sounds function to create the sound directory and explain how to add sounds
def ensure_sound_directory():
    """Create the sound directory and print instructions for adding sound files."""
    sounds_dir = os.path.join(ASSETS_DIR, "sounds")
    os.makedirs(sounds_dir, exist_ok=True)

    # Check if the directory is empty
    if not os.listdir(sounds_dir):
        print("\nSound Directory Information:")
        print(f"Sound files should be placed in: {os.path.abspath(sounds_dir)}")
        print("Expected sound files (WAV format):")
        print("  - shoot.wav       - Played when firing a bullet")
        print("  - zombie_hit.wav  - Played when a zombie is hit")
        print("  - player_damage.wav - Played when the player takes damage")
        print("  - game_over.wav   - Played when the game ends")
        print("  - powerup.wav     - Played when collecting a power-up")
        print("  - wave_start.wav  - Played when a new wave begins")
        print("  - shield_hit.wav  - Played when a shield blocks damage")
        print("\nUsing placeholder sounds until these files are added.\n")


# Add this function to help debug browser issues
def browser_debug_info():
    """Print debug information for browser environment."""
    if IN_BROWSER:
        print("Browser Environment Information:")
        print(f"- Screen size: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        print(f"- Pygame version: {pygame.version.ver}")
        print(f"- Sound enabled: {SOUND_ENABLED}")
        print(f"- Music enabled: {MUSIC_ENABLED}")

        # Add this call at the beginning of async_main
        # browser_debug_info()


# Update your entry point to handle both desktop and browser
if __name__ == "__main__":
    initialize_images()
    if IN_BROWSER:
        # Browser mode - use asyncio
        print("Running in browser mode")
        asyncio.run(async_main())
    else:
        # Desktop mode - use original code
        print("Running in desktop mode")
        while True:
            show_title_screen()
            restart = game_loop()
            if not restart:
                continue
