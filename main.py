import json
import os
import sys
import time
import pygame
import tkinter as tk

from PIW import Image
from tkinter import ttk
from tkinter import messagebox
#this is a fan made version of GTA V

class WelcomeScreen:
  def __init__(self):
    self.welcome_window = tk.Tk()
    self.welcome_window.title("GTAV - Avery Edition | welcome")
    self.welcome_window.geometry("500x400")

    self.play = tk.Button(self.welcome_window< text="PLAY", command=lambda)
    self.play.pack()

class Player:
  def __init__(self):
    self.health = 100
    self.speed = 6

  def move(dir):
    """add this later"""

class Render:
  def __init__(self):
    """do this"""


class Game:
  def __init__(self):
    """do this"""

