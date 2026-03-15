import json
import os
import sys
import time
import pygame
from panda3d.core import Point3, Vec3, TransformState
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import tkinter as tk
from tkinter import ttk, messagebox

# Model dimensions (file references)
# player_model.egg: dimensions 1.5x2.0x0.8 (width x height x depth)
# vehicle_model.egg: dimensions 4.0x2.0x1.5
# building_model.egg: dimensions 5.0x5.0x3.0

class WelcomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("GTAV - Avery Edition | Welcome")
        self.root.geometry("600x500")
        self.root.configure(bg='#1a1a1a')
        
        title = tk.Label(root, text="GTA V - Avery Edition", font=("Arial", 24, "bold"), fg="#FFD700", bg='#1a1a1a')
        title.pack(pady=20)
        
        self.play_btn = tk.Button(root, text="PLAY", command=self.start_game, font=("Arial", 14), bg="#FFD700", fg="black", width=20)
        self.play_btn.pack(pady=10)
        
        self.settings_btn = tk.Button(root, text="SETTINGS", command=self.open_settings, font=("Arial", 14), bg="#FFD700", fg="black", width=20)
        self.settings_btn.pack(pady=10)
        
        self.quit_btn = tk.Button(root, text="QUIT", command=root.quit, font=("Arial", 14), bg="#FF4444", fg="white", width=20)
        self.quit_btn.pack(pady=10)
    
    def start_game(self):
        self.root.destroy()
        game = GameEngine()
        game.run()
    
    def open_settings(self):
        messagebox.showinfo("Settings", "Settings menu coming soon!")

class Player:
    def __init__(self, game):
        self.game = game
        self.health = 100
        self.max_health = 100
        self.speed = 25
        self.position = Point3(0, 0, 0)
        self.velocity = Vec3(0, 0, 0)
        
        # Load player model
        self.model = game.loader.loadModel('models/player_model.egg')
        self.model.reparentTo(game.render)
        self.model.setScale(1.5, 2.0, 0.8)  # Set dimensions from file
        self.update_position()
    
    def move(self, direction, delta_time):
        """Move player in specified direction"""
        if direction == 'forward':
            self.velocity.setX(self.speed)
        elif direction == 'backward':
            self.velocity.setX(-self.speed)
        elif direction == 'left':
            self.velocity.setY(self.speed)
        elif direction == 'right':
            self.velocity.setY(-self.speed)
        
        self.position += self.velocity * delta_time
        self.update_position()
    
    def update_position(self):
        self.model.setPos(self.position)
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

class Environment:
    def __init__(self, game):
        self.game = game
        self.buildings = []
        self.vehicles = []
        self.obstacles = []
        self.load_world()
    
    def load_world(self):
        """Load 3D world models"""
        # Load buildings
        for i in range(5):
            building = self.game.loader.loadModel('models/building_model.egg')
            building.reparentTo(self.game.render)
            building.setPos(i * 10, 0, 0)
            building.setScale(5.0, 5.0, 3.0)  # Dimensions from file
            self.buildings.append(building)
        
        # Load sky
        sky = self.game.loader.loadModel('models/sky.egg')
        sky.reparentTo(self.game.render)
        sky.setScale(500, 500, 500)
        
        # Load ground
        ground = self.game.loader.loadModel('models/ground.egg')
        ground.reparentTo(self.game.render)

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.ambient_sound = None
        self.effects = {}
        self.load_sounds()
    
    def load_sounds(self):
        """Load ambient and effect sounds"""
        try:
            self.ambient_sound = pygame.mixer.Sound('audio/ambient.wav')
            self.effects['footstep'] = pygame.mixer.Sound('audio/footstep.wav')
            self.effects['punch'] = pygame.mixer.Sound('audio/punch.wav')
            self.effects['vehicle'] = pygame.mixer.Sound('audio/vehicle_engine.wav')
        except:
            print("Some sound files not found, continuing without audio...")
    
    def play_ambient(self):
        if self.ambient_sound:
            self.ambient_sound.play(-1)
    
    def play_effect(self, effect_name):
        if effect_name in self.effects:
            self.effects[effect_name].play()
    
    def stop_all(self):
        pygame.mixer.stop()

class GameUI:
    def __init__(self, game):
        self.game = game
    
    def update_hud(self, player):
        """Update HUD display with player stats"""
        health_text = f"Health: {player.health}/{player.max_health}"
        pos_text = f"Position: ({player.position.getX():.1f}, {player.position.getY():.1f}, {player.position.getZ():.1f})"

class Render:
    def __init__(self, game):
        self.game = game
        self.setup_lighting()
        self.setup_camera()
    
    def setup_lighting(self):
        """Setup 3D world lighting"""
        self.game.setBackgroundColor(0.1, 0.1, 0.15)
    
    def setup_camera(self):
        """Setup camera position and behavior"""
        self.game.camera.setPos(0, -30, 15)
        self.game.camera.lookAt(0, 0, 5)

class GameEngine(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.title("GTAV - Avery Edition | Game")
        
        # Initialize managers
        self.audio = AudioManager()
        self.render_system = Render(self)
        self.environment = None
        self.player = None
        self.ui = None
        
        # Game state
        self.is_running = True
        self.keys_pressed = set()
        
        # Setup game
        self.setup_game()
    
    def setup_game(self):
        """Initialize game components"""
        self.environment = Environment(self)
        self.player = Player(self)
        self.ui = GameUI(self)
        self.audio.play_ambient()
        
        # Setup controls
        self.setup_controls()
        
        # Add game loop
        self.taskMgr.add(self.game_loop, "gameLoop")
    
    def setup_controls(self):
        """Setup keyboard controls"""
        self.accept('w', self.on_key_press, ['forward'])
        self.accept('s', self.on_key_press, ['backward'])
        self.accept('a', self.on_key_press, ['left'])
        self.accept('d', self.on_key_press, ['right'])
        self.accept('space', self.on_key_press, ['jump'])
        
        self.accept('w-up', self.on_key_release, ['forward'])
        self.accept('s-up', self.on_key_release, ['backward'])
        self.accept('a-up', self.on_key_release, ['left'])
        self.accept('d-up', self.on_key_release, ['right'])
    
    def on_key_press(self, key):
        self.keys_pressed.add(key)
    
    def on_key_release(self, key):
        self.keys_pressed.discard(key)
    
    def game_loop(self, task):
        """Main game loop"""
        delta_time = globalClock.getDt()
        
        # Handle player movement
        for key in self.keys_pressed:
            self.player.move(key, delta_time)
        
        # Update camera to follow player
        camera_distance = 30
        self.camera.setPos(
            self.player.position.getX(),
            self.player.position.getY() - camera_distance,
            self.player.position.getZ() + 15
        )
        self.camera.lookAt(self.player.position + Point3(0, 0, 5))
        
        return task.cont

def main():
    root = tk.Tk()
    welcome = WelcomeScreen(root)
    root.mainloop()

if __name__ == '__main__':
    main()
