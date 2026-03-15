//This is the installer for the game
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const https = require('https');
const unzipper = require('unzipper');

const GAME_URL = 'https://example.com/gta-v-files.zip'; // Replace with actual URL
const INSTALL_DIR = path.join(__dirname, 'game-files');
const CONFIG_FILE = path.join(INSTALL_DIR, 'config.json');

// Step 1: Download game files
async function downloadGameFiles() {
  console.log('📥 Downloading game files...');
  
  if (!fs.existsSync(INSTALL_DIR)) {
    fs.mkdirSync(INSTALL_DIR, { recursive: true });
  }

  return new Promise((resolve, reject) => {
    const zipPath = path.join(INSTALL_DIR, 'game.zip');
    const file = fs.createWriteStream(zipPath);

    https.get(GAME_URL, (response) => {
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        console.log('✅ Download complete');
        resolve(zipPath);
      });
    }).on('error', (err) => {
      fs.unlink(zipPath, () => {});
      reject(err);
    });
  });
}

// Step 2: Extract game files
async function extractGameFiles(zipPath) {
  console.log('📦 Extracting game files...');
  
  return new Promise((resolve, reject) => {
    fs.createReadStream(zipPath)
      .pipe(unzipper.Extract({ path: INSTALL_DIR }))
      .on('close', () => {
        fs.unlinkSync(zipPath); // Delete zip after extraction
        console.log('✅ Extraction complete');
        resolve();
      })
      .on('error', reject);
  });
}

// Step 3: Configure settings
function configureSettings() {
  console.log('⚙️ Configuring settings...');
  
  const defaultConfig = {
    version: '1.0.0',
    installDate: new Date().toISOString(),
    graphics: {
      resolution: '1920x1080',
      quality: 'ultra',
      vsync: true,
      fps: 60
    },
    audio: {
      masterVolume: 80,
      musicVolume: 60,
      sfxVolume: 80
    },
    gameplay: {
      difficulty: 'normal',
      language: 'en'
    }
  };

  fs.writeFileSync(CONFIG_FILE, JSON.stringify(defaultConfig, null, 2));
  console.log('✅ Configuration complete');
}

// Step 4: Launch the game
function launchGame() {
  console.log('🎮 Launching GTA-V Avery Edition...');
  
  const gamePath = path.join(INSTALL_DIR, 'game.exe');
  
  if (!fs.existsSync(gamePath)) {
    console.error('❌ Game executable not found at', gamePath);
    return;
  }

  try {
    execSync(gamePath, { stdio: 'inherit' });
    console.log('✅ Game launched successfully');
  } catch (error) {
    console.error('❌ Failed to launch game:', error.message);
  }
}

// Main installation flow
async function install() {
  try {
    console.log('🚀 Starting GTA-V Avery Edition Installation\n');
    
    const zipPath = await downloadGameFiles();
    await extractGameFiles(zipPath);
    configureSettings();
    
    console.log('\n✨ Installation complete! Starting game...\n');
    launchGame();
  } catch (error) {
    console.error('❌ Installation failed:', error);
    process.exit(1);
  }
}

// Run installer
install();