// Game variables
let player;
let zombies = [];
let bullets = [];
let score = 0;
let health = 100;
let gameOver = false;
let gameStarted = false;
let powerups = [];
let bloodSplatters = [];
let explosions = [];
let rocks = [];
let messageText = "";
let messageTimer = 0;
let gameTick = 0;

// Wave system variables
let currentWave = 1;
let waveTimer = 0;
let waveDuration = 1800; // 30 seconds at 60 FPS
let zombiesPerWave = 1;
let waveMessage = "";
let waveMessageTimer = 0;

// Leaderboard variables
let leaderboardData = [];
let playerName = "";
let playerEmail = "";
let showLeaderboard = false;
let showNameInput = false;
let inputActive = false;
let inputField = "name"; // "name" or "email"
let leaderboardLoaded = false;
let connectionStatus = "unknown"; // "connected", "error", "unknown"

// Constants
const SCREEN_WIDTH = 800;
const SCREEN_HEIGHT = 600;
const PLAYER_WIDTH = 32;
const PLAYER_HEIGHT = 32;
const PLAYER_SPEED = 5;
const ZOMBIE_WIDTH = 32;
const ZOMBIE_HEIGHT = 32;
const ZOMBIE_SPEED = 2;
const BULLET_WIDTH = 4;
const BULLET_HEIGHT = 4;
const BULLET_SPEED = 10;
const ROCK_COUNT = 8;
const SMALL_ROCK_COUNT = 15;
const AI_ASSISTANT_DURATION = 300;

// Colors
const WHITE = [255, 255, 255];
const BLACK = [0, 0, 0];
const RED = [255, 0, 0];
const GREEN = [0, 255, 0];
const BLUE = [0, 0, 255];
const AI_ASSISTANT_COLOR = [0, 200, 255];

// Power-up types
const POWERUP_TYPES = [
  { name: "AI Assistant", color: [0, 200, 255], duration: 300 },
  { name: "Speed Boost", color: [255, 200, 0], duration: 180 },
  { name: "Shield", color: [200, 0, 255], duration: 240 },
  { name: "Rapid Fire", color: [255, 50, 50], duration: 200 }
];

// Graphics buffers for sprites
let playerBuffer;
let zombieBuffer;
let bulletBuffer;
let backgroundBuffer;
let bloodSplatterBuffers = [];
let explosionBuffers = [];

function preload() {
  // No external assets to preload
}

function setup() {
  createCanvas(SCREEN_WIDTH, SCREEN_HEIGHT);
  textAlign(LEFT, TOP);
  
  // Initialize game graphics
  createGameGraphics();
  
  // Initialize game
  player = new Player();
  createRocks();
  
  // Set up fonts
  scoreFont = textSize(20);
  gameOverFont = textSize(40);
  
  // Preload leaderboard data
  loadLeaderboard();
}

// Create all game graphics programmatically
function createGameGraphics() {
  // Create player sprite (AI robot with glowing elements)
  playerBuffer = createGraphics(PLAYER_WIDTH, PLAYER_HEIGHT);
  
  // Robot body (metallic blue)
  playerBuffer.fill(40, 90, 180);
  playerBuffer.noStroke();
  playerBuffer.rect(6, 6, 20, 20, 3);
  
  // Glowing core
  playerBuffer.fill(0, 200, 255, 200);
  playerBuffer.ellipse(16, 16, 10, 10);
  playerBuffer.stroke(150, 230, 255, 150);
  playerBuffer.noFill();
  playerBuffer.ellipse(16, 16, 14, 14);
  
  // Robot head
  playerBuffer.noStroke();
  playerBuffer.fill(60, 110, 200);
  playerBuffer.rect(10, 0, 12, 8, 2);
  
  // Eyes (glowing)
  playerBuffer.fill(0, 255, 255);
  playerBuffer.ellipse(13, 4, 4, 4);
  playerBuffer.ellipse(19, 4, 4, 4);
  
  // Limbs
  playerBuffer.fill(50, 100, 190);
  playerBuffer.rect(2, 10, 4, 16, 2);  // Left arm
  playerBuffer.rect(26, 10, 4, 16, 2); // Right arm
  playerBuffer.rect(8, 26, 6, 6, 1);   // Left leg
  playerBuffer.rect(18, 26, 6, 6, 1);  // Right leg
  
  // Circuit patterns
  playerBuffer.stroke(100, 200, 255);
  playerBuffer.line(10, 12, 14, 12);
  playerBuffer.line(18, 20, 22, 20);
  playerBuffer.line(10, 12, 10, 16);
  playerBuffer.line(22, 20, 22, 24);
  
  // Create zombie sprite
  zombieBuffer = createGraphics(ZOMBIE_WIDTH, ZOMBIE_HEIGHT);
  
  // Zombie body (decaying green)
  zombieBuffer.fill(60, 120, 60);
  zombieBuffer.noStroke();
  zombieBuffer.rect(6, 6, 20, 20, 3);
  
  // Zombie head
  zombieBuffer.fill(70, 130, 70);
  zombieBuffer.rect(10, 0, 12, 8, 2);
  
  // Zombie eyes (red)
  zombieBuffer.fill(255, 0, 0);
  zombieBuffer.ellipse(13, 4, 4, 4);
  zombieBuffer.ellipse(19, 4, 4, 4);
  
  // Zombie limbs (decaying)
  zombieBuffer.fill(50, 110, 50);
  zombieBuffer.rect(2, 10, 4, 16, 2);  // Left arm
  zombieBuffer.rect(26, 10, 4, 16, 2); // Right arm
  zombieBuffer.rect(8, 26, 6, 6, 1);   // Left leg
  zombieBuffer.rect(18, 26, 6, 6, 1);  // Right leg
  
  // Decay details
  zombieBuffer.fill(30, 80, 30, 150);
  zombieBuffer.ellipse(10, 15, 6, 6);
  zombieBuffer.ellipse(22, 12, 5, 5);
  zombieBuffer.ellipse(16, 22, 7, 7);
  
  // Create bullet sprite
  bulletBuffer = createGraphics(BULLET_WIDTH, BULLET_HEIGHT);
  bulletBuffer.fill(255, 100, 50);
  bulletBuffer.noStroke();
  bulletBuffer.ellipse(BULLET_WIDTH/2, BULLET_HEIGHT/2, BULLET_WIDTH, BULLET_HEIGHT);
  
  // Create background
  backgroundBuffer = createGraphics(SCREEN_WIDTH, SCREEN_HEIGHT);
  backgroundBuffer.background(10, 10, 20);
  
  // Add some stars/details to background
  backgroundBuffer.fill(255, 255, 255, 100);
  for (let i = 0; i < 100; i++) {
    let x = random(SCREEN_WIDTH);
    let y = random(SCREEN_HEIGHT);
    let size = random(1, 3);
    backgroundBuffer.ellipse(x, y, size, size);
  }
  
  // Create blood splatter effects
  for (let i = 0; i < 3; i++) {
    let buffer = createGraphics(20, 20);
    buffer.noStroke();
    buffer.fill(150, 0, 0, 200);
    buffer.ellipse(10, 10, random(10, 20), random(10, 20));
    
    // Add some blood droplets
    for (let j = 0; j < 5; j++) {
      let x = random(20);
      let y = random(20);
      let size = random(2, 5);
      buffer.ellipse(x, y, size, size);
    }
    
    bloodSplatterBuffers.push(buffer);
  }
  
  // Create explosion effects
  for (let i = 0; i < 3; i++) {
    let buffer = createGraphics(40, 40);
    buffer.noStroke();
    
    // Inner bright part
    buffer.fill(255, 200, 50, 200);
    buffer.ellipse(20, 20, 20 + i * 5, 20 + i * 5);
    
    // Outer part
    buffer.fill(255, 100, 0, 150 - i * 40);
    buffer.ellipse(20, 20, 30 + i * 8, 30 + i * 8);
    
    explosionBuffers.push(buffer);
  }
}

function draw() {
  gameTick++;
  
  if (showLeaderboard) {
    showLeaderboardScreen();
    return;
  }
  
  if (showNameInput) {
    showNameInputScreen();
    return;
  }
  
  if (!gameStarted) {
    showTitleScreen();
    return;
  }
  
  if (!gameOver) {
    // Game logic
    handleInput();
    updateWaveSystem();
    updateZombies();
    updateBullets();
    updatePowerups();
    updateVisualEffects();
    
    // AI Assistant logic
    if (player.activePowerups["AI Assistant"] > 0) {
      if (gameTick % 10 === 0 && zombies.length > 0) {
        // Find nearest zombie
        let nearestZombie = findNearestZombie();
        if (nearestZombie) {
          // Calculate direction to zombie
          let dx = nearestZombie.x - (player.x + PLAYER_WIDTH/2);
          let dy = nearestZombie.y - (player.y + PLAYER_HEIGHT/2);
          let angle = Math.atan2(dy, dx);
          
          // Create AI bullet
          let aiBullet = new Bullet(
            player.x + PLAYER_WIDTH/2 - BULLET_WIDTH/2,
            player.y + PLAYER_HEIGHT/2 - BULLET_HEIGHT/2,
            angle
          );
          aiBullet.color = AI_ASSISTANT_COLOR;
          bullets.push(aiBullet);
          
          // Visual effect for AI targeting
          stroke(...AI_ASSISTANT_COLOR, 150);
          line(
            player.x + PLAYER_WIDTH/2,
            player.y + PLAYER_HEIGHT/2,
            nearestZombie.x + ZOMBIE_WIDTH/2,
            nearestZombie.y + ZOMBIE_HEIGHT/2
          );
        }
      }
    }
    
    // Draw everything
    drawGame();
  } else {
    showGameOverScreen();
  }
}

function createRocks() {
  // Create medium rocks
  for (let i = 0; i < ROCK_COUNT; i++) {
    let size = random(25, 40);
    let x = random(0, SCREEN_WIDTH - size);
    let y = random(0, SCREEN_HEIGHT - size);
    rocks.push(new Rock(x, y, size, false));
  }
  
  // Create small rocks
  for (let i = 0; i < SMALL_ROCK_COUNT; i++) {
    let size = random(10, 20);
    let x = random(0, SCREEN_WIDTH - size);
    let y = random(0, SCREEN_HEIGHT - size);
    rocks.push(new Rock(x, y, size, false));
  }
}

function handleInput() {
  // Check if mouseX and mouseY are defined
  if (typeof mouseX === 'undefined' || typeof mouseY === 'undefined') {
    return; // Skip this frame if mouse coordinates aren't available yet
  }
  
  // Movement
  if (keyIsDown(LEFT_ARROW) || keyIsDown(65)) { // Left arrow or A
    player.move("left");
  }
  if (keyIsDown(RIGHT_ARROW) || keyIsDown(68)) { // Right arrow or D
    player.move("right");
  }
  if (keyIsDown(UP_ARROW) || keyIsDown(87)) { // Up arrow or W
    player.move("up");
  }
  if (keyIsDown(DOWN_ARROW) || keyIsDown(83)) { // Down arrow or S
    player.move("down");
  }
  
  // Aiming
  if (player && typeof player.updateAim === 'function') {
    player.updateAim(mouseX, mouseY);
  }
  
  // Shooting
  if (mouseIsPressed && mouseButton === LEFT && player && typeof player.shoot === 'function') {
    if (player.shootCooldown <= 0) {
      // Create bullet(s)
      let newBullets = player.shoot();
      if (newBullets && newBullets.length) {
        bullets.push(...newBullets);
      }
      
      // Set cooldown based on power-ups
      player.shootCooldown = player.activePowerups && player.activePowerups["Rapid Fire"] > 0 ? 5 : 10;
    }
  }
  
  // Update shoot cooldown
  if (player && player.shootCooldown > 0) {
    player.shootCooldown--;
  }
}

function updateWaveSystem() {
  waveTimer++;
  
  // Check if current wave is over
  if (waveTimer >= waveDuration) {
    // Start new wave
    currentWave++;
    waveTimer = 0;
    
    // Increase difficulty
    zombiesPerWave = Math.min(20, Math.floor(currentWave * 1.5));
    
    // Show wave message
    waveMessage = `Wave ${currentWave}`;
    waveMessageTimer = 180; // 3 seconds at 60 FPS
  }
  
  // Spawn zombies based on wave progress
  if (frameCount % 60 === 0) { // Every second
    let maxZombies = zombiesPerWave + Math.floor(currentWave / 3);
    
    if (zombies.length < maxZombies) {
      zombies.push(new Zombie());
    }
  }
  
  // Update wave message timer
  if (waveMessageTimer > 0) {
    waveMessageTimer--;
  }
}

function updateZombies() {
  for (let i = zombies.length - 1; i >= 0; i--) {
    // Move zombie toward player
    zombies[i].move(player.x + PLAYER_WIDTH/2, player.y + PLAYER_HEIGHT/2);
    
    // Check collision with player
    if (
      player.x < zombies[i].x + ZOMBIE_WIDTH &&
      player.x + PLAYER_WIDTH > zombies[i].x &&
      player.y < zombies[i].y + ZOMBIE_HEIGHT &&
      player.y + PLAYER_HEIGHT > zombies[i].y
    ) {
      // Player hit by zombie
      if (player.activePowerups["Shield"] > 0) {
        // Shield absorbs damage
      } else {
        player.health -= 10; // Each hit does 10 damage (4 hits to die)
      }
      
      // Remove zombie
      zombies.splice(i, 1);
      
      // Add blood splatter
      bloodSplatters.push(new BloodSplatter(
        player.x + PLAYER_WIDTH/2,
        player.y + PLAYER_HEIGHT/2
      ));
      
      // Check if player is dead
      if (player.health <= 0) {
        gameOver = true;
      }
      
      continue;
    }
  }
}

function updateBullets() {
  for (let i = bullets.length - 1; i >= 0; i--) {
    // Move bullet
    bullets[i].move();
    
    // Check if bullet is off-screen
    if (
      bullets[i].x < 0 ||
      bullets[i].x > SCREEN_WIDTH ||
      bullets[i].y < 0 ||
      bullets[i].y > SCREEN_HEIGHT
    ) {
      bullets.splice(i, 1);
      continue;
    }
    
    // Check collision with zombies
    for (let j = zombies.length - 1; j >= 0; j--) {
      if (
        bullets[i] && zombies[j] &&
        bullets[i].x < zombies[j].x + ZOMBIE_WIDTH &&
        bullets[i].x + BULLET_WIDTH > zombies[j].x &&
        bullets[i].y < zombies[j].y + ZOMBIE_HEIGHT &&
        bullets[i].y + BULLET_HEIGHT > zombies[j].y
      ) {
        // Store zombie position before removing it
        let zombieX = zombies[j].x;
        let zombieY = zombies[j].y;
        
        // Zombie hit by bullet
        zombies.splice(j, 1);
        
        // Remove bullet if it still exists
        if (i < bullets.length) {
          bullets.splice(i, 1);
        }
        
        // Add blood splatter
        bloodSplatters.push(new BloodSplatter(
          zombieX + ZOMBIE_WIDTH/2,
          zombieY + ZOMBIE_HEIGHT/2
        ));
        
        // Increase score
        player.score += 10;
        
        // Increase powerup spawn chance to 15%
        if (random() < 0.15) {
          powerups.push(new PowerUp(
            zombieX + ZOMBIE_WIDTH/2,
            zombieY + ZOMBIE_HEIGHT/2
          ));
        }
        
        break;
      }
    }
  }
}

function updatePowerups() {
  for (let i = powerups.length - 1; i >= 0; i--) {
    // Update power-up animation
    powerups[i].update();
    
    // Check collision with player
    if (
      player.x < powerups[i].x + 20 &&
      player.x + PLAYER_WIDTH > powerups[i].x - 20 &&
      player.y < powerups[i].y + 20 &&
      player.y + PLAYER_HEIGHT > powerups[i].y - 20
    ) {
      // Activate power-up
      let powerupName = powerups[i].name;
      let duration = powerups[i].duration;
      
      player.activePowerups[powerupName] = duration;
      
      // Apply power-up effects
      if (powerupName === "Speed Boost") {
        player.speed = player.baseSpeed * 1.5;
      }
      
      // Show message
      messageText = `${powerupName} activated!`;
      messageTimer = 120; // 2 seconds at 60 FPS
      
      // Remove power-up
      powerups.splice(i, 1);
    }
  }
  
  // Update active power-ups
  for (let powerup in player.activePowerups) {
    if (player.activePowerups[powerup] > 0) {
      player.activePowerups[powerup]--;
      
      // Handle power-up expiration
      if (player.activePowerups[powerup] === 0) {
        // Reset effects
        if (powerup === "Speed Boost") {
          player.speed = player.baseSpeed;
        }
        
        // Show message
        messageText = `${powerup} expired`;
        messageTimer = 60; // 1 second at 60 FPS
      }
    }
  }
  
  // Update message timer
  if (messageTimer > 0) {
    messageTimer--;
  }
}

function updateVisualEffects() {
  // Update blood splatters
  for (let i = bloodSplatters.length - 1; i >= 0; i--) {
    if (!bloodSplatters[i].update()) {
      bloodSplatters.splice(i, 1);
    }
  }
  
  // Update explosions
  for (let i = explosions.length - 1; i >= 0; i--) {
    if (!explosions[i].update()) {
      explosions.splice(i, 1);
    }
  }
}

function drawGame() {
  // Draw background
  background(10, 10, 20);
  
  // Draw rocks
  for (let rock of rocks) {
    rock.draw();
  }
  
  // Draw power-ups
  for (let powerup of powerups) {
    powerup.draw();
  }
  
  // Draw player
  player.draw();
  
  // Draw zombies
  for (let zombie of zombies) {
    zombie.draw();
  }
  
  // Draw bullets
  for (let bullet of bullets) {
    bullet.draw();
  }
  
  // Draw visual effects
  for (let splatter of bloodSplatters) {
    splatter.draw();
  }
  
  for (let explosion of explosions) {
    explosion.draw();
  }
  
  // Draw UI
  drawUI();
}

function drawUI() {
  // Health bar background
  fill(60, 60, 60);
  rect(10, 10, 200, 20, 5);
  
  // Health bar
  let healthPercent = player.health / 40; // Changed from 100 to 40
  let healthBarWidth = 200 * healthPercent;
  let healthColor;
  
  if (healthPercent > 0.6) {
    healthColor = color(0, 200, 0); // Green for high health
  } else if (healthPercent > 0.3) {
    healthColor = color(200, 200, 0); // Yellow for medium health
  } else {
    healthColor = color(200, 0, 0); // Red for low health
  }
  
  fill(healthColor);
  rect(10, 10, healthBarWidth, 20, 5);
  
  // Health text
  fill(255);
  textAlign(CENTER, CENTER);
  text(player.health + "/40", 110, 20); // Changed from 100 to 40
  textAlign(LEFT, TOP);
  
  // Score
  fill(255);
  textSize(24);
  text("Score: " + player.score, SCREEN_WIDTH - 150, 20);
  
  // Wave info
  fill(200, 200, 255);
  textSize(18);
  text("Wave: " + currentWave, SCREEN_WIDTH - 150, 50);
  
  // Wave progress bar
  let waveProgress = waveTimer / waveDuration;
  fill(60, 60, 60);
  rect(SCREEN_WIDTH - 150, 75, 100, 10, 5);
  fill(100, 100, 255);
  rect(SCREEN_WIDTH - 150, 75, 100 * waveProgress, 10, 5);
  
  // Active power-ups
  let powerupY = 100;
  for (let powerup in player.activePowerups) {
    if (player.activePowerups[powerup] > 0) {
      let duration = player.activePowerups[powerup];
      let maxDuration;
      let color;
      
      switch(powerup) {
        case "AI Assistant":
          maxDuration = AI_ASSISTANT_DURATION;
          color = [0, 200, 255];
          break;
        case "Speed Boost":
          maxDuration = 180;
          color = [255, 200, 0];
          break;
        case "Shield":
          maxDuration = 240;
          color = [200, 0, 255];
          break;
        case "Rapid Fire":
          maxDuration = 200;
          color = [255, 50, 50];
          break;
      }
      
      // Power-up background
      fill(60, 60, 60);
      rect(SCREEN_WIDTH - 150, powerupY, 100, 15, 5);
      
      // Power-up progress
      let progress = duration / maxDuration;
      fill(...color);
      rect(SCREEN_WIDTH - 150, powerupY, 100 * progress, 15, 5);
      
      // Power-up text
      fill(255);
      textSize(12);
      text(powerup, SCREEN_WIDTH - 145, powerupY + 2);
      
      powerupY += 20;
    }
  }
  
  // Wave message
  if (waveMessageTimer > 0) {
    let alpha = waveMessageTimer > 60 ? 255 : waveMessageTimer * 4.25;
    fill(255, 255, 255, alpha);
    textSize(36);
    textAlign(CENTER, CENTER);
    text(waveMessage, SCREEN_WIDTH/2, SCREEN_HEIGHT/4);
    textAlign(LEFT, TOP);
  }
  
  // Power-up message
  if (messageTimer > 0) {
    let alpha = messageTimer > 30 ? 255 : messageTimer * 8.5;
    fill(0, 200, 255, alpha);
    textSize(24);
    textAlign(CENTER, CENTER);
    text(messageText, SCREEN_WIDTH/2, SCREEN_HEIGHT/3);
    textAlign(LEFT, TOP);
  }
}

function showTitleScreen() {
  // Background with grid effect
  background(10, 10, 20);
  
  // Draw grid lines
  stroke(0, 100, 150, 50);
  strokeWeight(1);
  
  // Draw vertical grid lines
  for (let x = 0; x < SCREEN_WIDTH; x += 40) {
    line(x, 0, x, SCREEN_HEIGHT);
  }
  
  // Draw horizontal grid lines
  for (let y = 0; y < SCREEN_HEIGHT; y += 40) {
    line(0, y, SCREEN_WIDTH, y);
  }
  
  // Draw border
  strokeWeight(2);
  stroke(0, 150, 255);
  noFill();
  rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20);
  
  // Set text properties for measuring
  textSize(60);
  textAlign(CENTER, CENTER);
  
  // Measure the text width to make the background fit properly
  let titleText = "AI ZOMBIE APOCALYPSE";
  let titleWidth = textWidth(titleText);
  
  // Title with pulsing effect
  let glowIntensity = 128 + 64 * sin(frameCount / 30);
  
  // Title background with pulsing effect - make it wider to fit the text
  fill(0, 150, 255, glowIntensity);
  noStroke();
  rect(SCREEN_WIDTH/2 - titleWidth/2 - 30, 100, titleWidth + 60, 80, 10);
  
  // Title text
  fill(255);
  text(titleText, SCREEN_WIDTH/2, 140);
  
  // Subtitle
  fill(255);
  textSize(24);
  text("Can your AI assistant save humanity?", SCREEN_WIDTH/2, 220);
  
  // Instructions
  textSize(18);
  text("WASD or Arrow Keys to move", SCREEN_WIDTH/2, 280);
  text("Mouse to aim and shoot", SCREEN_WIDTH/2, 310);
  text("Collect AI power-ups for automated assistance", SCREEN_WIDTH/2, 340);
  text("Survive the zombie horde as long as possible", SCREEN_WIDTH/2, 370);
  
  // Start button
  let startButtonX = SCREEN_WIDTH/2 - 100;
  let startButtonY = 430;
  let buttonWidth = 200;
  let buttonHeight = 50;
  
  let mouseOverStart = mouseX > startButtonX && mouseX < startButtonX + buttonWidth &&
                       mouseY > startButtonY && mouseY < startButtonY + buttonHeight;
  
  fill(mouseOverStart ? color(0, 180, 255) : color(0, 120, 200));
  rect(startButtonX, startButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textSize(24);
  text("Start Game", SCREEN_WIDTH/2, startButtonY + buttonHeight/2);
  
  // Leaderboard button
  let leaderboardButtonX = SCREEN_WIDTH/2 - 100;
  let leaderboardButtonY = 500;
  
  let mouseOverLeaderboard = mouseX > leaderboardButtonX && mouseX < leaderboardButtonX + buttonWidth &&
                             mouseY > leaderboardButtonY && mouseY < leaderboardButtonY + buttonHeight;
  
  fill(mouseOverLeaderboard ? color(0, 150, 220) : color(0, 100, 170));
  rect(leaderboardButtonX, leaderboardButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textSize(24);
  text("Leaderboard", SCREEN_WIDTH/2, leaderboardButtonY + buttonHeight/2);
  
  // Pulsing effect for buttons
  let pulseSize = sin(frameCount * 0.05) * 5;
  
  if (mouseOverStart) {
    noFill();
    stroke(0, 200, 255, 150);
    rect(startButtonX - pulseSize/2, startButtonY - pulseSize/2, 
         buttonWidth + pulseSize, buttonHeight + pulseSize, 8);
  }
  
  if (mouseOverLeaderboard) {
    noFill();
    stroke(0, 200, 255, 150);
    rect(leaderboardButtonX - pulseSize/2, leaderboardButtonY - pulseSize/2, 
         buttonWidth + pulseSize, buttonHeight + pulseSize, 8);
  }
  
  // Reset text alignment
  textAlign(LEFT, TOP);
}

function showGameOverScreen() {
  // Background with grid effect
  background(10, 10, 20);
  
  // Draw grid lines
  stroke(0, 100, 150, 50);
  strokeWeight(1);
  
  for (let x = 0; x < SCREEN_WIDTH; x += 40) {
    line(x, 0, x, SCREEN_HEIGHT);
  }
  
  for (let y = 0; y < SCREEN_HEIGHT; y += 40) {
    line(0, y, SCREEN_WIDTH, y);
  }
  
  // Draw border
  strokeWeight(2);
  stroke(0, 150, 255);
  noFill();
  rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20);
  
  // Game Over title with pulsing effect
  let glowIntensity = 128 + 64 * sin(frameCount / 30);
  
  // Draw the title background
  fill(0, 100, 200);
  noStroke();
  rect(SCREEN_WIDTH/2 - 150, 80, 300, 80, 10);
  
  // Draw the title text with pulsing
  fill(0, 200 + glowIntensity/3, 255);
  textSize(60);
  textAlign(CENTER, CENTER);
  text("GAME OVER", SCREEN_WIDTH/2, 120);
  
  // Score
  fill(255);
  textSize(32);
  textAlign(CENTER, CENTER);
  text("Your Score: " + player.score, SCREEN_WIDTH/2, 200);
  
  // Email field
  let emailFieldX = SCREEN_WIDTH/2 - 150;
  let emailFieldY = 250;
  let fieldWidth = 300;
  let fieldHeight = 40;
  
  fill(30, 30, 50);
  rect(emailFieldX, emailFieldY, fieldWidth, fieldHeight, 5);
  
  fill(255);
  textSize(20);
  textAlign(RIGHT, CENTER);
  text("Email:", emailFieldX - 10, emailFieldY + fieldHeight/2);
  
  textAlign(LEFT, CENTER);
  text(playerEmail, emailFieldX + 10, emailFieldY + fieldHeight/2);
  
  if (frameCount % 60 < 30) {
    stroke(255);
    line(emailFieldX + 10 + textWidth(playerEmail), emailFieldY + 10, 
         emailFieldX + 10 + textWidth(playerEmail), emailFieldY + fieldHeight - 10);
    noStroke();
  }
  
  // Submit Score button
  let submitButtonX = SCREEN_WIDTH/2 - 100;
  let submitButtonY = 320;
  let buttonWidth = 200;
  let buttonHeight = 40;
  
  let canSubmit = playerEmail.length > 0;
  let mouseOverSubmit = mouseX > submitButtonX && mouseX < submitButtonX + buttonWidth &&
                        mouseY > submitButtonY && mouseY < submitButtonY + buttonHeight;
  
  fill(canSubmit ? (mouseOverSubmit ? color(0, 150, 250) : color(0, 100, 200)) : color(100, 100, 100));
  rect(submitButtonX, submitButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textSize(24);
  textAlign(CENTER, CENTER);
  text("Submit Score", SCREEN_WIDTH/2, submitButtonY + buttonHeight/2);
  
  // Main Menu button
  let menuButtonX = SCREEN_WIDTH/2 - 100;
  let menuButtonY = 380;
  
  let mouseOverMenu = mouseX > menuButtonX && mouseX < menuButtonX + buttonWidth &&
                      mouseY > menuButtonY && mouseY < menuButtonY + buttonHeight;
  
  fill(mouseOverMenu ? color(100, 100, 100) : color(80, 80, 80));
  rect(menuButtonX, menuButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textSize(24);
  textAlign(CENTER, CENTER);
  text("Main Menu", SCREEN_WIDTH/2, menuButtonY + buttonHeight/2);
  
  // View Leaderboard button
  let leaderboardButtonX = SCREEN_WIDTH/2 - 100;
  let leaderboardButtonY = 440;
  
  let mouseOverLeaderboard = mouseX > leaderboardButtonX && mouseX < leaderboardButtonX + buttonWidth &&
                             mouseY > leaderboardButtonY && mouseY < leaderboardButtonY + buttonHeight;
  
  fill(mouseOverLeaderboard ? color(0, 150, 250) : color(0, 100, 200));
  rect(leaderboardButtonX, leaderboardButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textSize(24);
  textAlign(CENTER, CENTER);
  text("View Leaderboard", SCREEN_WIDTH/2, leaderboardButtonY + buttonHeight/2);
  
  // Newsletter and privacy notes
  fill(180, 180, 180);
  textSize(14);
  textAlign(CENTER, CENTER);
  text("By submitting, you're signing up for the HackerHall newsletter", 
       SCREEN_WIDTH/2, leaderboardButtonY + buttonHeight + 30);
  
  text("Your email will be partially hidden on the leaderboard", 
       SCREEN_WIDTH/2, leaderboardButtonY + buttonHeight + 50);
  
  // Reset drawing state
  textAlign(LEFT, TOP);
}

function mousePressed() {
  if (!gameStarted && !showLeaderboard && !showNameInput) {
    // Check if Start Game button is clicked
    let startButtonX = SCREEN_WIDTH/2 - 100;
    let startButtonY = 430;
    let buttonWidth = 200;
    let buttonHeight = 50;
    
    if (mouseX > startButtonX && mouseX < startButtonX + buttonWidth &&
        mouseY > startButtonY && mouseY < startButtonY + buttonHeight) {
      gameStarted = true;
      resetGame();
      return;
    }
    
    // Check if Leaderboard button is clicked
    let leaderboardButtonX = SCREEN_WIDTH/2 - 100;
    let leaderboardButtonY = 500;
    
    if (mouseX > leaderboardButtonX && mouseX < leaderboardButtonX + buttonWidth &&
        mouseY > leaderboardButtonY && mouseY < leaderboardButtonY + buttonHeight) {
      showLeaderboard = true;
      loadLeaderboard(); // Refresh leaderboard data
      return;
    }
  } else if (showLeaderboard) {
    // Check if Back button is clicked
    let backButtonX = SCREEN_WIDTH/2 - 100;
    let backButtonY = SCREEN_HEIGHT - 100;
    let buttonWidth = 200;
    let buttonHeight = 40;
    
    if (mouseX > backButtonX && mouseX < backButtonX + buttonWidth &&
        mouseY > backButtonY && mouseY < backButtonY + buttonHeight) {
      showLeaderboard = false;
      gameStarted = false; // Ensure we go to the main menu, not the game
      gameOver = false;    // Reset game over state
      return;
    }
    
    // Check if Refresh button is clicked
    let refreshButtonX = SCREEN_WIDTH - 80;
    let refreshButtonY = 120;
    let refreshButtonSize = 40;
    
    if (mouseX > refreshButtonX && mouseX < refreshButtonX + refreshButtonSize &&
        mouseY > refreshButtonY && mouseY < refreshButtonY + refreshButtonSize) {
      loadLeaderboard();
      return;
    }
  } else if (showNameInput) {
    // Handle name input screen clicks
    let nameFieldX = SCREEN_WIDTH/2 - 150;
    let nameFieldY = 180;
    let emailFieldX = SCREEN_WIDTH/2 - 150;
    let emailFieldY = 240;
    let fieldWidth = 300;
    let fieldHeight = 40;
    
    // Check if name field is clicked
    if (mouseX > nameFieldX && mouseX < nameFieldX + fieldWidth &&
        mouseY > nameFieldY && mouseY < nameFieldY + fieldHeight) {
      inputField = "name";
      inputActive = true;
      return;
    }
    
    // Check if email field is clicked
    if (mouseX > emailFieldX && mouseX < emailFieldX + fieldWidth &&
        mouseY > emailFieldY && mouseY < emailFieldY + fieldHeight) {
      inputField = "email";
      inputActive = true;
      return;
    }
    
    // Check if Submit button is clicked
    let submitButtonX = SCREEN_WIDTH/2 - 100;
    let submitButtonY = 310;
    let buttonWidth = 200;
    let buttonHeight = 40;
    
    if (mouseX > submitButtonX && mouseX < submitButtonX + buttonWidth &&
        mouseY > submitButtonY && mouseY < submitButtonY + buttonHeight) {
      if (playerName.length > 0) {
        submitScore().then(success => {
          if (success) {
            showNameInput = false;
            showLeaderboard = true;
          }
        });
      }
      return;
    }
    
    // Check if Skip button is clicked
    let skipButtonX = SCREEN_WIDTH/2 - 100;
    let skipButtonY = 370;
    
    if (mouseX > skipButtonX && mouseX < skipButtonX + buttonWidth &&
        mouseY > skipButtonY && mouseY < skipButtonY + buttonHeight) {
      showNameInput = false;
      gameStarted = false;
      return;
    }
  } else if (gameOver) {
    // Handle Game Over screen clicks
    let buttonWidth = 200;
    let buttonHeight = 40;
    
    // Submit Score button
    let submitButtonX = SCREEN_WIDTH/2 - 100;
    let submitButtonY = 320;
    
    if (mouseX > submitButtonX && mouseX < submitButtonX + buttonWidth &&
        mouseY > submitButtonY && mouseY < submitButtonY + buttonHeight) {
      if (playerEmail.length > 0) {
        submitScore().then(success => {
          if (success) {
            gameOver = false;
            showLeaderboard = true;
          }
        });
      }
      return;
    }
    
    // Main Menu button
    let menuButtonX = SCREEN_WIDTH/2 - 100;
    let menuButtonY = SCREEN_WIDTH/2 - 100;
    
    if (mouseX > menuButtonX && mouseX < menuButtonX + buttonWidth &&
        mouseY > menuButtonY && mouseY < menuButtonY + buttonHeight) {
      gameOver = false;
      gameStarted = false;
      return;
    }
    
    // View Leaderboard button
    let leaderboardButtonX = SCREEN_WIDTH/2 - 100;
    let leaderboardButtonY = SCREEN_WIDTH/2 - 100;
    
    if (mouseX > leaderboardButtonX && mouseX < leaderboardButtonX + buttonWidth &&
        mouseY > leaderboardButtonY && mouseY < leaderboardButtonY + buttonHeight) {
      showLeaderboard = true;
      loadLeaderboard();
      return;
    }
  }
}

function resetGame() {
  player = new Player();
  zombies = [];
  bullets = [];
  powerups = [];
  bloodSplatters = [];
  explosions = [];
  
  currentWave = 1;
  waveTimer = 0;
  zombiesPerWave = 1;
  
  gameOver = false;
  
  // Reset player properties
  player.health = 40; // Changed from 100 to 40
  player.score = 0;
  player.activePowerups = {
    "AI Assistant": 0,
    "Speed Boost": 0,
    "Shield": 0,
    "Rapid Fire": 0
  };
}

function findNearestZombie() {
  if (zombies.length === 0) return null;
  
  let nearestZombie = zombies[0];
  let minDistance = dist(
    player.x + PLAYER_WIDTH/2,
    player.y + PLAYER_HEIGHT/2,
    zombies[0].x + ZOMBIE_WIDTH/2,
    zombies[0].y + ZOMBIE_HEIGHT/2
  );
  
  for (let i = 1; i < zombies.length; i++) {
    let distance = dist(
      player.x + PLAYER_WIDTH/2,
      player.y + PLAYER_HEIGHT/2,
      zombies[i].x + ZOMBIE_WIDTH/2,
      zombies[i].y + ZOMBIE_HEIGHT/2
    );
    
    if (distance < minDistance) {
      minDistance = distance;
      nearestZombie = zombies[i];
    }
  }
  
  return nearestZombie;
}

function playSound(soundName) {
  // Simply return without doing anything - all sound is disabled
  return;
}

// Player class
class Player {
  constructor() {
    this.x = SCREEN_WIDTH/2 - PLAYER_WIDTH/2;
    this.y = SCREEN_HEIGHT/2 - PLAYER_HEIGHT/2;
    this.angle = 0;
    this.direction = "right";
    this.speed = PLAYER_SPEED;
    this.baseSpeed = PLAYER_SPEED;
    this.health = 40;
    this.score = 0;
    this.shootCooldown = 0;
    this.activePowerups = {
      "AI Assistant": 0,
      "Speed Boost": 0,
      "Shield": 0,
      "Rapid Fire": 0
    };
  }
  
  updateAim(mouseX, mouseY) {
    // Safety check
    if (typeof mouseX === 'undefined' || typeof mouseY === 'undefined') {
      return;
    }
    
    // Calculate angle to mouse cursor
    let dx = mouseX - (this.x + PLAYER_WIDTH/2);
    let dy = mouseY - (this.y + PLAYER_HEIGHT/2);
    this.angle = Math.atan2(dy, dx);
    
    // Update direction for player sprite rotation
    if (this.angle > -Math.PI/4 && this.angle < Math.PI/4) {
      this.direction = "right";
    } else if (this.angle >= Math.PI/4 && this.angle < 3*Math.PI/4) {
      this.direction = "down";
    } else if (this.angle >= -3*Math.PI/4 && this.angle <= -Math.PI/4) {
      this.direction = "up";
    } else {
      this.direction = "left";
    }
  }
  
  move(direction) {
    // Apply speed boost if active
    let currentSpeed = this.activePowerups["Speed Boost"] > 0 ? 
                      this.baseSpeed * 1.5 : this.baseSpeed;
    
    if (direction === "left" && this.x > 0) {
      this.x -= currentSpeed;
    } else if (direction === "right" && this.x < SCREEN_WIDTH - PLAYER_WIDTH) {
      this.x += currentSpeed;
    } else if (direction === "up" && this.y > 0) {
      this.y -= currentSpeed;
    } else if (direction === "down" && this.y < SCREEN_HEIGHT - PLAYER_HEIGHT) {
      this.y += currentSpeed;
    }
  }
  
  shoot() {
    let bulletX = this.x + PLAYER_WIDTH/2 - BULLET_WIDTH/2;
    let bulletY = this.y + PLAYER_HEIGHT/2 - BULLET_HEIGHT/2;
    
    let bullets = [];
    
    // Create multiple bullets if Rapid Fire is active
    if (this.activePowerups["Rapid Fire"] > 0) {
      // Create 3 bullets with slight spread
      for (let i = -1; i <= 1; i++) {
        let spreadAngle = this.angle + (i * 0.1); // Small angle spread
        bullets.push(new Bullet(bulletX, bulletY, spreadAngle));
      }
    } else {
      bullets.push(new Bullet(bulletX, bulletY, this.angle));
    }
    
    return bullets;
  }
  
  draw() {
    push();
    translate(this.x + PLAYER_WIDTH/2, this.y + PLAYER_HEIGHT/2);
    
    // Rotate based on direction
    if (this.direction === "right") {
      rotate(0);
    } else if (this.direction === "down") {
      rotate(HALF_PI);
    } else if (this.direction === "left") {
      rotate(PI);
    } else { // up
      rotate(-HALF_PI);
    }
    
    // Draw player sprite
    imageMode(CENTER);
    image(playerBuffer, 0, 0);
    
    // Draw shield if active
    if (this.activePowerups["Shield"] > 0) {
      noFill();
      stroke(200, 0, 255, 150);
      strokeWeight(2);
      ellipse(0, 0, PLAYER_WIDTH * 1.5, PLAYER_HEIGHT * 1.5);
      strokeWeight(1);
    }
    
    pop();
  }
  
  applyPowerup(powerup) {
    this.activePowerups[powerup.name] = powerup.duration;
    
    // Apply immediate effects
    if (powerup.name === "Speed Boost") {
      this.speed = this.baseSpeed * 1.5;
    }
    
    return `${powerup.name} activated!`;
  }
  
  updatePowerups() {
    // Update all active power-ups
    for (let name in this.activePowerups) {
      if (this.activePowerups[name] > 0) {
        this.activePowerups[name]--;
        
        // Handle expiration
        if (this.activePowerups[name] <= 0) {
          if (name === "Speed Boost") {
            this.speed = this.baseSpeed;
          }
        }
      }
    }
  }
  
  takeDamage(amount) {
    // If Shield is active, don't take damage
    if (this.activePowerups["Shield"] > 0) {
      return false;
    }
    
    this.health -= amount;
    
    if (this.health <= 0) {
      this.health = 0;
      return true; // Player is dead
    }
    return false;
  }
}

// Zombie class
class Zombie {
  constructor(edge) {
    // Spawn from a random edge
    if (!edge) {
      edge = random(["top", "right", "bottom", "left"]);
    }
    
    if (edge === "top") {
      this.x = random(0, SCREEN_WIDTH - ZOMBIE_WIDTH);
      this.y = -ZOMBIE_HEIGHT;
    } else if (edge === "right") {
      this.x = SCREEN_WIDTH;
      this.y = random(0, SCREEN_HEIGHT - ZOMBIE_HEIGHT);
    } else if (edge === "bottom") {
      this.x = random(0, SCREEN_WIDTH - ZOMBIE_WIDTH);
      this.y = SCREEN_HEIGHT;
    } else { // left
      this.x = -ZOMBIE_WIDTH;
      this.y = random(0, SCREEN_HEIGHT - ZOMBIE_HEIGHT);
    }
    
    this.speed = ZOMBIE_SPEED;
    this.direction = "right"; // Default direction
  }
  
  move(targetX, targetY) {
    // Calculate direction to player
    let dx = targetX - (this.x + ZOMBIE_WIDTH/2);
    let dy = targetY - (this.y + ZOMBIE_HEIGHT/2);
    
    // Normalize the direction
    let length = max(0.1, sqrt(dx * dx + dy * dy));
    dx /= length;
    dy /= length;
    
    // Move towards player
    this.x += dx * this.speed;
    this.y += dy * this.speed;
    
    // Update direction for animation
    if (abs(dx) > abs(dy)) {
      this.direction = dx > 0 ? "right" : "left";
    } else {
      this.direction = dy > 0 ? "down" : "up";
    }
  }
  
  draw() {
    push();
    translate(this.x + ZOMBIE_WIDTH/2, this.y + ZOMBIE_HEIGHT/2);
    
    // Fix rotation - use atan2 to get the correct angle
    if (this.direction === "right") {
      rotate(0);
    } else if (this.direction === "down") {
      rotate(HALF_PI);
    } else if (this.direction === "left") {
      rotate(PI);
    } else { // up
      rotate(3*PI/2);
    }
    
    // Draw zombie sprite
    imageMode(CENTER);
    image(zombieBuffer, 0, 0);
    
    pop();
  }
}

// Bullet class
class Bullet {
  constructor(x, y, angle) {
    this.x = x;
    this.y = y;
    this.angle = angle;
    this.speed = BULLET_SPEED;
    this.color = [255, 100, 50]; // Default color
  }
  
  move() {
    this.x += cos(this.angle) * this.speed;
    this.y += sin(this.angle) * this.speed;
  }
  
  draw() {
    push();
    translate(this.x, this.y);
    rotate(this.angle);
    
    // Use the bullet's color (which might be changed for AI bullets)
    fill(this.color);
    rect(0, 0, BULLET_WIDTH, BULLET_HEIGHT);
    
    // Add a small glow effect
    noFill();
    stroke(...this.color, 100);
    rect(-2, -2, BULLET_WIDTH + 4, BULLET_HEIGHT + 4);
    
    pop();
  }
}

// Rock class
class Rock {
  constructor(x, y, size, isObstacle) {
    this.x = x;
    this.y = y;
    this.size = size;
    this.isObstacle = isObstacle;
    this.color = [40, 80, 120]; // Blue-gray color
    this.vertices = [];
    
    // Create a jagged rock shape
    let points = floor(random(5, 8));
    for (let i = 0; i < points; i++) {
      let angle = map(i, 0, points, 0, TWO_PI);
      let radius = size/2 * random(0.7, 1.0);
      let px = cos(angle) * radius;
      let py = sin(angle) * radius;
      this.vertices.push({x: px, y: py});
    }
  }
  
  draw() {
    push();
    translate(this.x + this.size/2, this.y + this.size/2);
    
    // Draw rock shape
    fill(...this.color);
    noStroke();
    beginShape();
    for (let v of this.vertices) {
      vertex(v.x, v.y);
    }
    endShape(CLOSE);
    
    // Add highlights
    fill(100, 150, 200, 50);
    ellipse(-this.size/4, -this.size/4, this.size/3, this.size/3);
    
    pop();
  }
}

// PowerUp class
class PowerUp {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.type = random(POWERUP_TYPES);
    this.name = this.type.name;
    this.color = this.type.color;
    this.duration = this.type.duration;
    this.pulse = 0;
    this.pulseDir = 1;
  }
  
  update() {
    // Update pulse animation
    this.pulse += 0.1 * this.pulseDir;
    if (this.pulse >= 1.0) {
      this.pulseDir = -1;
    } else if (this.pulse <= 0.0) {
      this.pulseDir = 1;
    }
  }
  
  draw() {
    // Draw glowing orb
    let glowSize = 15 + 5 * sin(frameCount/10);
    
    // Outer glow
    for (let radius = glowSize; radius > glowSize - 10; radius -= 2) {
      let alpha = max(0, 150 - (glowSize - radius) * 30);
      noFill();
      stroke(...this.color, alpha);
      ellipse(this.x, this.y, radius * 2, radius * 2);
    }
    
    // Core
    fill(255);
    noStroke();
    ellipse(this.x, this.y, 12, 12);
    
    // Symbol based on power-up type
    stroke(255);
    strokeWeight(2);
    
    if (this.name === "AI Assistant") {
      // AI symbol (resembling a circuit)
      line(this.x - 4, this.y, this.x + 4, this.y);
      line(this.x, this.y - 4, this.x, this.y + 4);
      fill(255);
      ellipse(this.x, this.y, 4, 4);
    } else if (this.name === "Speed Boost") {
      // Lightning bolt symbol
      noFill();
      beginShape();
      vertex(this.x - 3, this.y - 5);
      vertex(this.x + 1, this.y - 1);
      vertex(this.x - 1, this.y + 1);
      vertex(this.x + 3, this.y + 5);
      endShape();
    } else if (this.name === "Shield") {
      // Shield symbol
      noFill();
      arc(this.x, this.y, 10, 10, PI * 0.75, PI * 2.25);
    } else if (this.name === "Rapid Fire") {
      // Rapid fire symbol
      fill(255);
      ellipse(this.x - 2, this.y, 2, 2);
      ellipse(this.x, this.y, 2, 2);
      ellipse(this.x + 2, this.y, 2, 2);
    }
    
    strokeWeight(1);
  }
}

// BloodSplatter class
class BloodSplatter {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.frame = 0;
    this.maxFrames = 10;
    this.frameDelay = 3;
    this.frameCounter = 0;
    this.particles = [];
    
    // Create blood particles
    for (let i = 0; i < 8; i++) {
      this.particles.push({
        x: random(-10, 10),
        y: random(-10, 10),
        size: random(3, 8),
        alpha: 255
      });
    }
  }
  
  update() {
    this.frameCounter++;
    if (this.frameCounter >= this.frameDelay) {
      this.frame++;
      this.frameCounter = 0;
      
      // Fade out particles
      for (let particle of this.particles) {
        particle.alpha -= 25;
      }
    }
    return this.frame < this.maxFrames;
  }
  
  draw() {
    if (this.frame < this.maxFrames) {
      push();
      translate(this.x, this.y);
      
      // Draw blood particles
      for (let particle of this.particles) {
        fill(200, 0, 0, particle.alpha);
        noStroke();
        ellipse(particle.x, particle.y, particle.size, particle.size);
      }
      
      pop();
    }
  }
}

// Explosion class
class Explosion {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.frame = 0;
    this.maxFrames = 10;
    this.frameDelay = 2;
    this.frameCounter = 0;
  }
  
  update() {
    this.frameCounter++;
    if (this.frameCounter >= this.frameDelay) {
      this.frame++;
      this.frameCounter = 0;
    }
    return this.frame < this.maxFrames;
  }
  
  draw() {
    if (this.frame < this.maxFrames) {
      // Placeholder for explosion drawing
    }
  }
}

// Add this function to handle leaderboard display
function showLeaderboardScreen() {
  // Background with grid effect
  background(10, 10, 20);
  
  // Draw grid lines
  stroke(0, 100, 150, 50);
  strokeWeight(1);
  
  // Draw vertical grid lines
  for (let x = 0; x < SCREEN_WIDTH; x += 40) {
    line(x, 0, x, SCREEN_HEIGHT);
  }
  
  // Draw horizontal grid lines
  for (let y = 0; y < SCREEN_HEIGHT; y += 40) {
    line(0, y, SCREEN_WIDTH, y);
  }
  
  // Draw border
  strokeWeight(2);
  stroke(0, 150, 255);
  noFill();
  rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20);
  
  // Title
  fill(0, 200, 255);
  textSize(40);
  textAlign(CENTER, TOP);
  text("LEADERBOARD", SCREEN_WIDTH/2, 50);
  
  // Table setup
  let tableX = 100;
  let tableY = 120;
  let tableWidth = SCREEN_WIDTH - 200;
  let rowHeight = 40;
  let rankWidth = 50;
  let playerWidth = 350;
  let scoreWidth = 100;
  
  // Draw table outline
  stroke(0, 150, 255);
  strokeWeight(2);
  noFill();
  rect(tableX, tableY, tableWidth, rowHeight * 10, 5);
  
  // Leaderboard data
  if (leaderboardData && leaderboardData.length > 0) {
    for (let i = 0; i < Math.min(10, leaderboardData.length); i++) {
      let entry = leaderboardData[i];
      let rowY = tableY + i * rowHeight;
      
      // Row background with medal colors for top 3
      if (i < 3) {
        // Medal background colors
        let medalColors = [
          [255, 215, 0, 100],  // Gold
          [192, 192, 192, 100], // Silver
          [205, 127, 50, 100]   // Bronze
        ];
        
        noStroke();
        fill(medalColors[i][0], medalColors[i][1], medalColors[i][2], medalColors[i][3]);
        rect(tableX, rowY, tableWidth, rowHeight);
      } else {
        // Regular row background
        noStroke();
        fill(20, 40, 80, 150);
        rect(tableX, rowY, tableWidth, rowHeight);
      }
      
      // Draw row divider
      stroke(0, 100, 150);
      strokeWeight(1);
      line(tableX, rowY + rowHeight, tableX + tableWidth, rowY + rowHeight);
      
      // Rank with medal for top 3
      textAlign(CENTER, CENTER);
      if (i < 3) {
        // Medal colors: gold, silver, bronze
        let medalColors = [
          [255, 215, 0],  // Gold
          [192, 192, 192], // Silver
          [205, 127, 50]   // Bronze
        ];
        
        noStroke();
        fill(medalColors[i][0], medalColors[i][1], medalColors[i][2]);
        ellipse(tableX + rankWidth/2, rowY + rowHeight/2, 30, 30);
        fill(0);
        textSize(18);
        text(i + 1, tableX + rankWidth/2, rowY + rowHeight/2);
      } else {
        noStroke();
        fill(255);
        textSize(18);
        text(i + 1, tableX + rankWidth/2, rowY + rowHeight/2);
      }
      
      // Format player name to match Python version (r***@hackerhall.ai)
      let displayName = entry.email || "Anonymous";
      if (displayName.includes('@')) {
        let username = displayName.split('@')[0];
        let domain = displayName.split('@')[1];
        if (username.length > 0) {
          displayName = username.charAt(0) + "***@" + domain;
        }
      }
      
      // Player name
      noStroke();
      textAlign(CENTER, CENTER);
      fill(255);
      textSize(18);
      text(displayName, tableX + rankWidth + playerWidth/2, rowY + rowHeight/2);
      
      // Score
      textAlign(CENTER, CENTER);
      fill(255, 215, 0); // Gold color for scores
      textSize(18);
      text(entry.score, tableX + rankWidth + playerWidth + scoreWidth/2, rowY + rowHeight/2);
    }
  } else {
    fill(200);
    textSize(24);
    textAlign(CENTER, CENTER);
    text("No leaderboard data available", SCREEN_WIDTH/2, 200);
  }
  
  // Back button with text
  let backButtonX = SCREEN_WIDTH/2 - 100;
  let backButtonY = SCREEN_HEIGHT - 100;
  let buttonWidth = 200;
  let buttonHeight = 40;
  
  let mouseOverBack = mouseX > backButtonX && mouseX < backButtonX + buttonWidth &&
                      mouseY > backButtonY && mouseY < backButtonY + buttonHeight;
  
  fill(mouseOverBack ? color(0, 150, 250) : color(0, 100, 200));
  rect(backButtonX, backButtonY, buttonWidth, buttonHeight, 5);
  
  // Add "Back" text to the button
  fill(255);
  textSize(24);
  textAlign(CENTER, CENTER);
  text("Main Menu", SCREEN_WIDTH/2, backButtonY + buttonHeight/2);
  
  // Refresh button
  let refreshButtonX = SCREEN_WIDTH - 80;
  let refreshButtonY = 120;
  let refreshButtonSize = 40;
  
  let mouseOverRefresh = mouseX > refreshButtonX && mouseX < refreshButtonX + refreshButtonSize &&
                         mouseY > refreshButtonY && mouseY < refreshButtonY + refreshButtonSize;
  
  fill(mouseOverRefresh ? color(0, 170, 250) : color(0, 120, 200));
  ellipse(refreshButtonX + refreshButtonSize/2, refreshButtonY + refreshButtonSize/2, refreshButtonSize, refreshButtonSize);
  
  // Refresh icon
  stroke(255);
  strokeWeight(2);
  noFill();
  arc(refreshButtonX + refreshButtonSize/2, refreshButtonY + refreshButtonSize/2, 
      refreshButtonSize * 0.6, refreshButtonSize * 0.6, -PI/4, PI * 1.5);
  line(refreshButtonX + refreshButtonSize/2 + refreshButtonSize * 0.3, refreshButtonY + refreshButtonSize/2 - refreshButtonSize * 0.1,
       refreshButtonX + refreshButtonSize/2 + refreshButtonSize * 0.2, refreshButtonY + refreshButtonSize/2 - refreshButtonSize * 0.3);
  line(refreshButtonX + refreshButtonSize/2 + refreshButtonSize * 0.3, refreshButtonY + refreshButtonSize/2 - refreshButtonSize * 0.1,
       refreshButtonX + refreshButtonSize/2 + refreshButtonSize * 0.4, refreshButtonY + refreshButtonSize/2);
  strokeWeight(1);
  
  textAlign(LEFT, TOP);
}

// Add this function to handle name/email input
function showNameInputScreen() {
  background(5, 7, 15);
  
  // Draw grid lines
  stroke(0, 100, 150, 50);
  strokeWeight(1);
  
  // Draw vertical grid lines
  for (let x = 0; x < SCREEN_WIDTH; x += 40) {
    line(x, 0, x, SCREEN_HEIGHT);
  }
  
  // Draw horizontal grid lines
  for (let y = 0; y < SCREEN_HEIGHT; y += 40) {
    line(0, y, SCREEN_WIDTH, y);
  }
  
  // Draw border
  strokeWeight(2);
  stroke(0, 150, 255);
  noFill();
  rect(10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20);
  
  // Title
  fill(0, 200, 255);
  textSize(40);
  textAlign(CENTER, TOP);
  text("SUBMIT YOUR SCORE", SCREEN_WIDTH/2, 50);
  
  // Score display
  fill(255, 215, 0);
  textSize(32);
  text("Score: " + player.score, SCREEN_WIDTH/2, 120);
  
  // Name input field
  let nameFieldX = SCREEN_WIDTH/2 - 150;
  let nameFieldY = 180;
  let fieldWidth = 300;
  let fieldHeight = 40;
  
  fill(inputField === "name" ? color(40, 40, 60) : color(20, 20, 40));
  rect(nameFieldX, nameFieldY, fieldWidth, fieldHeight, 5);
  
  fill(255);
  textSize(20);
  textAlign(LEFT, CENTER);
  text("Name: ", nameFieldX - 80, nameFieldY + fieldHeight/2);
  
  textAlign(LEFT, CENTER);
  text(playerName, nameFieldX + 10, nameFieldY + fieldHeight/2);
  
  if (inputField === "name" && frameCount % 60 < 30) {
    // Blinking cursor
    let cursorX = nameFieldX + 10 + textWidth(playerName);
    stroke(255);
    line(cursorX, nameFieldY + 10, cursorX, nameFieldY + fieldHeight - 10);
    noStroke();
  }
  
  // Email input field
  let emailFieldX = SCREEN_WIDTH/2 - 150;
  let emailFieldY = 240;
  
  fill(inputField === "email" ? color(40, 40, 60) : color(20, 20, 40));
  rect(emailFieldX, emailFieldY, fieldWidth, fieldHeight, 5);
  
  fill(255);
  textAlign(LEFT, CENTER);
  text("Email: ", emailFieldX - 80, emailFieldY + fieldHeight/2);
  
  textAlign(LEFT, CENTER);
  text(playerEmail, emailFieldX + 10, emailFieldY + fieldHeight/2);
  
  if (inputField === "email" && frameCount % 60 < 30) {
    // Blinking cursor
    let cursorX = emailFieldX + 10 + textWidth(playerEmail);
    stroke(255);
    line(cursorX, emailFieldY + 10, cursorX, emailFieldY + fieldHeight - 10);
    noStroke();
  }
  
  // Submit button
  let submitButtonX = SCREEN_WIDTH/2 - 100;
  let submitButtonY = 310;
  let buttonWidth = 200;
  let buttonHeight = 40;
  
  let canSubmit = playerName.length > 0;
  let mouseOverSubmit = mouseX > submitButtonX && mouseX < submitButtonX + buttonWidth &&
                        mouseY > submitButtonY && mouseY < submitButtonY + buttonHeight;
  
  fill(canSubmit ? (mouseOverSubmit ? color(0, 150, 250) : color(0, 100, 200)) : color(100, 100, 100));
  rect(submitButtonX, submitButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textSize(24);
  textAlign(CENTER, CENTER);
  text("Submit", SCREEN_WIDTH/2, submitButtonY + buttonHeight/2);
  
  // Skip button
  let skipButtonX = SCREEN_WIDTH/2 - 100;
  let skipButtonY = 370;
  
  let mouseOverSkip = mouseX > skipButtonX && mouseX < skipButtonX + buttonWidth &&
                      mouseY > skipButtonY && mouseY < skipButtonY + buttonHeight;
  
  fill(mouseOverSkip ? color(0, 130, 220) : color(80, 80, 80));
  rect(skipButtonX, skipButtonY, buttonWidth, buttonHeight, 5);
  
  fill(255);
  textAlign(CENTER, CENTER);
  text("Skip", SCREEN_WIDTH/2, skipButtonY + buttonHeight/2);
  
  // Newsletter signup note
  fill(180, 180, 180);
  textSize(14);
  text("By submitting, you're signing up for the HackerHall newsletter", 
       SCREEN_WIDTH/2, skipButtonY + buttonHeight + 30);
  
  // Privacy note
  fill(180, 180, 180);
  textSize(14);
  text("Your email will be partially hidden on the leaderboard", 
       SCREEN_WIDTH/2, skipButtonY + buttonHeight + 50);
  
  // Prize claim note with emphasis
  fill(255, 220, 100); // Gold color for emphasis
  textSize(14);
  text("Use a real email to claim your prize if you win!", 
       SCREEN_WIDTH/2, skipButtonY + buttonHeight + 70);
  
  textAlign(LEFT, TOP);
}

// Update the loadLeaderboard function
function loadLeaderboard() {
  leaderboardLoaded = false;
  connectionStatus = "unknown";
  
  // Clear any existing data
  leaderboardData = [];
  
  // Check if Supabase client is available
  if (!window.supabaseClient) {
    console.warn("Supabase client not available - using mock data");
    connectionStatus = "error";
    
    // Use mock data when Supabase is not configured
    leaderboardData = [
      { player_name: "player1", email: "p***@example.com", score: 40 },
      { player_name: "player2", email: "p***@example.com", score: 30 },
      { player_name: "player3", email: "p***@example.com", score: 20 },
      { player_name: "player4", email: "p***@example.com", score: 10 },
      { player_name: "player5", email: "p***@example.com", score: 5 }
    ];
    
    leaderboardLoaded = true;
    return;
  }
  
  // Query the scores table
  window.supabaseClient
    .from('scores')
    .select('*')
    .order('score', { ascending: false })
    .limit(10)
    .then(response => {
      if (response.error) {
        console.error("Error loading leaderboard:", response.error);
        connectionStatus = "error";
        leaderboardLoaded = true;
        return;
      }
      
      if (response.data && response.data.length > 0) {
        leaderboardData = response.data;
        connectionStatus = "connected";
        console.log("Leaderboard loaded from Supabase:", leaderboardData);
      } else {
        console.log("No leaderboard data found in Supabase");
      }
      
      leaderboardLoaded = true;
    })
    .catch(error => {
      console.error("Exception loading leaderboard:", error);
      connectionStatus = "error";
      leaderboardLoaded = true;
    });
}

// Update the submitScore function
async function submitScore() {
  try {
    if (!window.supabaseClient) {
      console.warn("Supabase client not available - score not saved");
      alert("Score not saved: Database connection not configured");
      return false;
    }
    
    const { data, error } = await window.supabaseClient
      .from('scores')
      .insert([
        { 
          player_name: playerName || "Anonymous",
          email: playerEmail || "anonymous@example.com", 
          score: player.score,
        }
      ]);
    
    if (error) {
      console.error("Error submitting score:", error.message);
      alert("Error saving score: " + error.message);
      return false;
    } else {
      console.log("Score submitted successfully!");
      alert("Score submitted successfully!");
      await loadLeaderboard();
      return true;
    }
  } catch (e) {
    console.error("Exception submitting score:", e);
    alert("Error saving score: " + e.message);
    return false;
  }
}

// Update the keyPressed function to handle async calls
function keyPressed() {
  if (gameOver) {
    if (keyCode === ENTER || keyCode === RETURN) {
      if (playerEmail.length > 0 && playerEmail.includes('@')) {
        // Use a promise to handle the async submitScore function
        submitScore().then(() => {
          showLeaderboard = true;
        });
      }
      return false;
    } else if (keyCode === BACKSPACE) {
      if (playerEmail.length > 0) {
        playerEmail = playerEmail.substring(0, playerEmail.length - 1);
      }
      return false;
    }
  }
  return true;
}

function keyTyped() {
  if (gameOver) {
    if (playerEmail.length < 50) {
      playerEmail += key;
    }
    return false;
  }
  return true;
} 