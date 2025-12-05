#!/usr/bin/env python3
"""
THE MATRIX: DIGITAL REVOLUTION - Tam Kapsamlı Oyun
Tüm özellikler entegre edilmiş versiyon
"""
import pygame
import random
import math
import sys
import json
import numpy as np
import datetime
import threading
import socket
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from pygame import gfxdraw

# PyGame başlatma
pygame.init()
pygame.mixer.init()

# Ekran ayarları
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
pygame.display.set_caption("THE MATRIX: DIGITAL REVOLUTION")
clock = pygame.time.Clock()

# Renk paleti - Genişletilmiş
COLORS = {
    'matrix_green': (0, 255, 0),
    'matrix_light_green': (180, 255, 180),
    'matrix_cyan': (0, 255, 255),
    'matrix_blue': (100, 150, 255),
    'matrix_white': (255, 255, 255),
    'matrix_dark': (0, 20, 0),
    'matrix_red': (255, 50, 50),
    'matrix_yellow': (255, 255, 0),
    'matrix_purple': (180, 0, 255),
    'matrix_orange': (255, 165, 0),
    'matrix_pink': (255, 105, 180),
    'matrix_brown': (139, 69, 19),
    'matrix_gray': (128, 128, 128),
    'black': (0, 0, 0),
    'dark_green': (0, 100, 0)
}

# Unicode karakter seti
KATAKANA = [chr(int('0x30A0', 16) + i) for i in range(96)]
GREEK = [chr(i) for i in range(0x0391, 0x03A9)] + [chr(i) for i in range(0x03B1, 0x03C9)]
SYMBOLS = ['∀', '∁', '∂', '∃', '∄', '∅', '∆', '∇', '∈', '∉', '∊', '∋', '∌', '∍', '∎', '⊕', '⊗']
DIGITS = [str(i) for i in range(10)]
HEX = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
MATRIX_CHARS = KATAKANA + GREEK + SYMBOLS + DIGITS + HEX

# Fontlar
FONT_SIZE = 16
font = pygame.font.Font(None, FONT_SIZE)
bold_font = pygame.font.Font(None, FONT_SIZE + 4)
large_font = pygame.font.Font(None, 72)
medium_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 14)

# ==================== ENUM'lar ====================
class GameState(Enum):
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    UPGRADE_SHOP = "upgrade_shop"
    MISSION_SELECT = "mission_select"
    CUTSCENE = "cutscene"
    MULTIPLAYER_LOBBY = "multiplayer_lobby"

class EnemyType(Enum):
    BASIC = "basic"
    HACKER = "hacker"
    GLITCH = "glitch"
    FIREWALL = "firewall"
    VIRUS = "virus"
    WORM = "worm"
    TROJAN = "trojan"
    BOSS = "boss"

class PowerUpType(Enum):
    HEALTH = "health"
    RAPID_FIRE = "rapid_fire"
    SHIELD = "shield"
    DOUBLE_POINTS = "double_points"
    TIME_SLOW = "time_slow"
    MATRIX_VISION = "matrix_vision"
    NANO_BOTS = "nano_bots"
    QUANTUM = "quantum"

class WeatherType(Enum):
    CLEAR = "clear"
    DATA_RAIN = "data_rain"
    GLITCH_STORM = "glitch_storm"
    MATRIX_OVERLOAD = "matrix_overload"
    CYBER_SNOW = "cyber_snow"

# ==================== DATA CLASSES ====================
@dataclass
class Mission:
    id: int
    name: str
    description: str
    type: str
    target: int
    reward: int
    completed: bool = False
    progress: int = 0

@dataclass
class Upgrade:
    name: str
    description: str
    level: int = 0
    max_level: int = 5
    cost_base: int = 100
    cost_multiplier: float = 1.5

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlock_time: Optional[int] = None

# ==================== PARTICLE SYSTEM ====================
class Particle:
    def __init__(self, x, y, color, size, velocity, lifetime, particle_type="circle"):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vx, self.vy = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.type = particle_type
        self.char = random.choice(MATRIX_CHARS) if particle_type == "matrix" else None
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        self.size = max(0, self.size * 0.98)
        self.rotation += self.rotation_speed
        return self.lifetime > 0

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if self.type == "matrix":
            char_surface = small_font.render(self.char, True, (*self.color[:3], alpha))
            rotated = pygame.transform.rotate(char_surface, self.rotation)
            surface.blit(rotated, (self.x - rotated.get_width() // 2, 
                                 self.y - rotated.get_height() // 2))
        else:
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color[:3], alpha), 
                             (self.size, self.size), self.size)
            surface.blit(s, (self.x - self.size, self.y - self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, particle):
        self.particles.append(particle)
    
    def add_explosion(self, x, y, color, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            self.add_particle(Particle(
                x, y, color,
                random.uniform(2, 6),
                (math.cos(angle) * speed, math.sin(angle) * speed),
                random.randint(20, 60)
            ))
    
    def add_matrix_rain(self, x, y):
        for _ in range(10):
            self.add_particle(Particle(
                x + random.randint(-20, 20),
                y + random.randint(-20, 20),
                COLORS['matrix_green'],
                random.uniform(1, 3),
                (0, random.uniform(2, 4)),
                random.randint(30, 90),
                "matrix"
            ))
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# ==================== UPGRADE SYSTEM ====================
class UpgradeSystem:
    def __init__(self):
        self.upgrades = {
            "damage": Upgrade("Damage Boost", "Increase bullet damage by 20% per level", cost_base=100),
            "fire_rate": Upgrade("Fire Rate", "Increase shooting speed by 15% per level", cost_base=150),
            "health": Upgrade("Max Health", "Increase max health by 20 per level", cost_base=200),
            "speed": Upgrade("Movement Speed", "Increase movement speed by 10% per level", cost_base=80),
            "shield_regen": Upgrade("Shield Regen", "Regenerate 1% shield per second per level", cost_base=300, max_level=3),
            "critical_chance": Upgrade("Critical Hit", "5% chance for double damage per level", cost_base=250),
            "bullet_pierce": Upgrade("Bullet Pierce", "Bullets can hit multiple enemies", cost_base=400, max_level=3),
            "auto_collect": Upgrade("Auto Collect", "Automatically collect powerups in range", cost_base=350, max_level=2),
        }
        self.skill_points = 0
        self.unlocked_upgrades = []
    
    def get_upgrade_cost(self, upgrade_name):
        upgrade = self.upgrades[upgrade_name]
        return int(upgrade.cost_base * (upgrade.cost_multiplier ** upgrade.level))
    
    def can_upgrade(self, upgrade_name):
        upgrade = self.upgrades[upgrade_name]
        return (upgrade.level < upgrade.max_level and 
                self.skill_points >= self.get_upgrade_cost(upgrade_name))
    
    def apply_upgrade(self, player, upgrade_name):
        if not self.can_upgrade(upgrade_name):
            return False
        
        upgrade = self.upgrades[upgrade_name]
        cost = self.get_upgrade_cost(upgrade_name)
        self.skill_points -= cost
        upgrade.level += 1
        
        if upgrade_name == "damage":
            player.damage_multiplier = 1 + (upgrade.level * 0.2)
        elif upgrade_name == "fire_rate":
            player.shoot_cooldown_base = max(5, 20 - (upgrade.level * 2))
        elif upgrade_name == "health":
            player.max_health = 100 + (upgrade.level * 20)
            player.health = min(player.health, player.max_health)
        elif upgrade_name == "speed":
            player.speed = 5 + (upgrade.level * 0.5)
        elif upgrade_name == "shield_regen":
            player.shield_regen_rate = upgrade.level * 0.01
        elif upgrade_name == "critical_chance":
            player.critical_chance = upgrade.level * 0.05
        elif upgrade_name == "bullet_pierce":
            player.bullet_pierce = upgrade.level
        elif upgrade_name == "auto_collect":
            player.auto_collect_range = upgrade.level * 50
        
        self.unlocked_upgrades.append(upgrade_name)
        return True
    
    def draw_shop(self, surface, player):
        # Arkaplan
        pygame.draw.rect(surface, (0, 30, 0, 200), (WIDTH//2 - 300, 50, 600, 700))
        pygame.draw.rect(surface, COLORS['matrix_green'], (WIDTH//2 - 300, 50, 600, 700), 3)
        
        # Başlık
        title = large_font.render("UPGRADE TERMINAL", True, COLORS['matrix_cyan'])
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        
        # Skill Points
        points_text = medium_font.render(f"SKILL POINTS: {self.skill_points}", True, COLORS['matrix_yellow'])
        surface.blit(points_text, (WIDTH//2 - points_text.get_width()//2, 140))
        
        # Upgrade listesi
        y_offset = 200
        for i, (name, upgrade) in enumerate(self.upgrades.items()):
            color = COLORS['matrix_light_green'] if upgrade.level < upgrade.max_level else COLORS['matrix_gray']
            level_text = f"Lvl {upgrade.level}/{upgrade.max_level}"
            cost = self.get_upgrade_cost(name) if upgrade.level < upgrade.max_level else "MAX"
            
            upgrade_text = font.render(f"{upgrade.name} - {level_text} - Cost: {cost}", True, color)
            desc_text = small_font.render(upgrade.description, True, COLORS['matrix_white'])
            
            surface.blit(upgrade_text, (WIDTH//2 - 280, y_offset))
            surface.blit(desc_text, (WIDTH//2 - 280, y_offset + 25))
            
            # Upgrade butonu
            button_rect = pygame.Rect(WIDTH//2 + 180, y_offset, 80, 30)
            button_color = COLORS['matrix_green'] if self.can_upgrade(name) else COLORS['matrix_dark']
            pygame.draw.rect(surface, button_color, button_rect)
            pygame.draw.rect(surface, COLORS['matrix_white'], button_rect, 1)
            
            button_text = font.render("UPGRADE", True, COLORS['black'])
            surface.blit(button_text, (button_rect.x + 10, button_rect.y + 5))
            
            y_offset += 60
        
        # Çıkış butonu
        exit_rect = pygame.Rect(WIDTH//2 - 50, 780, 100, 40)
        pygame.draw.rect(surface, COLORS['matrix_red'], exit_rect)
        pygame.draw.rect(surface, COLORS['matrix_white'], exit_rect, 2)
        exit_text = font.render("BACK", True, COLORS['white'])
        surface.blit(exit_text, (exit_rect.x + 30, exit_rect.y + 10))

# ==================== MISSION SYSTEM ====================
class MissionSystem:
    def __init__(self):
        self.missions = [
            Mission(1, "First Blood", "Destroy 10 enemies", "enemies", 10, 500),
            Mission(2, "Power Collector", "Collect 5 powerups", "powerups", 5, 300),
            Mission(3, "Survivor", "Survive 5 waves", "waves", 5, 1000),
            Mission(4, "Boss Slayer", "Defeat a boss", "boss", 1, 2000),
            Mission(5, "Perfect Accuracy", "Achieve 80% accuracy", "accuracy", 80, 1500),
            Mission(6, "Combo Master", "Get a 10x combo", "combo", 10, 800),
            Mission(7, "Speed Runner", "Complete wave in under 60 seconds", "speed", 60, 1200),
            Mission(8, "Untouchable", "Complete a wave without taking damage", "no_damage", 1, 2500),
        ]
        self.active_missions = []
        self.completed_missions = []
        self.select_starting_missions()
    
    def select_starting_missions(self):
        self.active_missions = random.sample(self.missions[:4], 2)
    
    def update_progress(self, game_data):
        for mission in self.active_missions:
            if mission.type == "enemies":
                mission.progress = game_data.get('enemies_killed', 0)
            elif mission.type == "powerups":
                mission.progress = game_data.get('powerups_collected', 0)
            elif mission.type == "waves":
                mission.progress = game_data.get('waves_completed', 0)
            elif mission.type == "accuracy":
                shots = max(1, game_data.get('shots_fired', 1))
                hits = game_data.get('shots_hit', 0)
                mission.progress = int((hits / shots) * 100)
            
            if mission.progress >= mission.target and not mission.completed:
                self.complete_mission(mission)
    
    def complete_mission(self, mission):
        mission.completed = True
        self.active_missions.remove(mission)
        self.completed_missions.append(mission)
        # Yeni görev ekle
        available = [m for m in self.missions if m not in self.completed_missions and m not in self.active_missions]
        if available and len(self.active_missions) < 3:
            self.active_missions.append(random.choice(available))
        return mission.reward
    
    def draw(self, surface):
        pygame.draw.rect(surface, (0, 20, 0, 180), (WIDTH - 320, 100, 300, 400))
        pygame.draw.rect(surface, COLORS['matrix_green'], (WIDTH - 320, 100, 300, 400), 2)
        
        title = font.render("ACTIVE MISSIONS", True, COLORS['matrix_cyan'])
        surface.blit(title, (WIDTH - 320 + 150 - title.get_width()//2, 110))
        
        y_offset = 140
        for mission in self.active_missions:
            progress_percent = min(100, int((mission.progress / mission.target) * 100))
            
            # Görev adı
            name_text = font.render(mission.name, True, COLORS['matrix_white'])
            surface.blit(name_text, (WIDTH - 310, y_offset))
            
            # İlerleme çubuğu
            pygame.draw.rect(surface, COLORS['matrix_dark'], (WIDTH - 310, y_offset + 25, 260, 10))
            pygame.draw.rect(surface, COLORS['matrix_green'], 
                           (WIDTH - 310, y_offset + 25, 260 * progress_percent // 100, 10))
            
            # İlerleme metni
            progress_text = small_font.render(f"{mission.progress}/{mission.target} ({progress_percent}%)", 
                                            True, COLORS['matrix_light_green'])
            surface.blit(progress_text, (WIDTH - 310, y_offset + 40))
            
            # Ödül
            reward_text = small_font.render(f"Reward: {mission.reward} SP", True, COLORS['matrix_yellow'])
            surface.blit(reward_text, (WIDTH - 310, y_offset + 60))
            
            y_offset += 90

# ==================== BOSS SYSTEM ====================
class MatrixBoss:
    def __init__(self, wave):
        self.wave = wave
        self.size = 150 + wave * 20
        self.x = WIDTH // 2
        self.y = -200
        self.health = 1000 + wave * 500
        self.max_health = self.health
        self.speed = 1
        self.pattern = 0
        self.attack_timer = 0
        self.phase = 1
        self.bullets = []
        self.minions = []
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.color = random.choice([COLORS['matrix_red'], COLORS['matrix_purple'], COLORS['matrix_orange']])
        self.name = random.choice(["Agent Smith", "The Architect", "Merovingian", "The Oracle"])
        
        # Boss yetenekleri
        self.abilities = {
            "laser_beam": {"cooldown": 0, "max_cooldown": 300},
            "spawn_minions": {"cooldown": 0, "max_cooldown": 450},
            "shield_wall": {"cooldown": 0, "max_cooldown": 600},
            "time_slow": {"cooldown": 0, "max_cooldown": 900},
        }
    
    def update(self, player_x, player_y):
        # Hareket pattern'leri
        if self.pattern == 0:  # Giriş
            self.y += self.speed
            if self.y > 100:
                self.pattern = 1
                self.attack_timer = 60
        
        elif self.pattern == 1:  # Saldırı
            # Oyuncuyu takip et
            dx = player_x - self.x
            self.x += dx * 0.02
            
            # Faz değişimi
            health_percent = self.health / self.max_health
            if health_percent < 0.66 and self.phase == 1:
                self.phase = 2
                self.activate_shield_wall()
            elif health_percent < 0.33 and self.phase == 2:
                self.phase = 3
                self.activate_time_slow()
            
            # Yetenekleri güncelle
            for ability in self.abilities.values():
                if ability["cooldown"] > 0:
                    ability["cooldown"] -= 1
            
            # Saldırı
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.random_attack()
                self.attack_timer = random.randint(30, 90)
            
            # Minionları güncelle
            for minion in self.minions[:]:
                minion.update()
                if minion.health <= 0:
                    self.minions.remove(minion)
        
        # Invulnerability
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False
        
        # Mermileri güncelle
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            if (bullet['x'] < -50 or bullet['x'] > WIDTH + 50 or 
                bullet['y'] < -50 or bullet['y'] > HEIGHT + 50):
                self.bullets.remove(bullet)
    
    def random_attack(self):
        if self.phase == 1:
            self.circular_attack()
        elif self.phase == 2:
            if random.random() < 0.5:
                self.laser_beam()
            else:
                self.spawn_minions()
        else:
            attacks = [self.circular_attack, self.laser_beam, self.spawn_minions]
            random.choice(attacks)()
    
    def circular_attack(self):
        for angle in range(0, 360, 20):
            rad = math.radians(angle + random.randint(-5, 5))
            self.bullets.append({
                'x': self.x + self.size//2,
                'y': self.y + self.size//2,
                'dx': math.cos(rad) * 4,
                'dy': math.sin(rad) * 4,
                'color': self.color,
                'size': 8
            })
    
    def laser_beam(self):
        if self.abilities["laser_beam"]["cooldown"] > 0:
            return
        
        self.abilities["laser_beam"]["cooldown"] = self.abilities["laser_beam"]["max_cooldown"]
        
        # Laser çizgisi
        for i in range(50):
            self.bullets.append({
                'x': self.x + self.size//2,
                'y': self.y + self.size + i * 10,
                'dx': 0,
                'dy': 0,
                'color': COLORS['matrix_red'],
                'size': 20 - i * 0.3,
                'laser': True
            })
    
    def spawn_minions(self):
        if self.abilities["spawn_minions"]["cooldown"] > 0:
            return
        
        self.abilities["spawn_minions"]["cooldown"] = self.abilities["spawn_minions"]["max_cooldown"]
        
        for _ in range(3):
            minion = Enemy(EnemyType.VIRUS, 1)
            minion.x = self.x + random.randint(-100, 100)
            minion.y = self.y + self.size
            self.minions.append(minion)
    
    def activate_shield_wall(self):
        self.invulnerable = True
        self.invulnerable_timer = 180
        
        # Kalkan oluştur
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            for i in range(5):
                self.bullets.append({
                    'x': self.x + self.size//2 + math.cos(rad) * (self.size//2 + i * 20),
                    'y': self.y + self.size//2 + math.sin(rad) * (self.size//2 + i * 20),
                    'dx': 0,
                    'dy': 0,
                    'color': COLORS['matrix_cyan'],
                    'size': 10,
                    'shield': True
                })
    
    def activate_time_slow(self):
        self.invulnerable = True
        self.invulnerable_timer = 120
        
        # Zaman yavaşlatma efekti
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            radius = random.uniform(self.size//2, self.size * 2)
            self.bullets.append({
                'x': self.x + self.size//2 + math.cos(angle) * radius,
                'y': self.y + self.size//2 + math.sin(angle) * radius,
                'dx': math.cos(angle) * 0.5,
                'dy': math.sin(angle) * 0.5,
                'color': COLORS['matrix_purple'],
                'size': 15,
                'time_slow': True
            })
    
    def draw(self, surface):
        # Boss gövdesi
        pygame.draw.rect(surface, self.color, 
                        (self.x, self.y, self.size, self.size))
        
        # Detaylar
        pygame.draw.rect(surface, COLORS['matrix_white'],
                        (self.x + 10, self.y + 10, self.size - 20, self.size - 20), 2)
        
        # Gözler
        eye_size = self.size // 10
        pygame.draw.circle(surface, COLORS['matrix_white'],
                          (self.x + self.size//3, self.y + self.size//3), eye_size)
        pygame.draw.circle(surface, COLORS['matrix_white'],
                          (self.x + 2*self.size//3, self.y + self.size//3), eye_size)
        pygame.draw.circle(surface, COLORS['matrix_red'],
                          (self.x + self.size//3, self.y + self.size//3), eye_size//2)
        pygame.draw.circle(surface, COLORS['matrix_red'],
                          (self.x + 2*self.size//3, self.y + self.size//3), eye_size//2)
        
        # Sağlık çubuğu
        health_width = 300
        health_height = 25
        health_x = WIDTH//2 - health_width//2
        health_y = 20
        
        pygame.draw.rect(surface, COLORS['matrix_dark'],
                        (health_x, health_y, health_width, health_height))
        
        health_percent = self.health / self.max_health
        fill_width = int(health_width * health_percent)
        
        health_color = COLORS['matrix_red'] if health_percent < 0.3 else COLORS['matrix_green']
        pygame.draw.rect(surface, health_color,
                        (health_x, health_y, fill_width, health_height))
        
        # İsim ve faz
        name_text = font.render(f"{self.name} - Phase {self.phase}", True, COLORS['matrix_white'])
        surface.blit(name_text, (health_x, health_y - 25))
        health_text = font.render(f"{int(self.health)}/{self.max_health}", True, COLORS['matrix_white'])
        surface.blit(health_text, (health_x + health_width//2 - health_text.get_width()//2, health_y + 3))
        
        # Mermileri çiz
        for bullet in self.bullets:
            if bullet.get('laser'):
                pygame.draw.circle(surface, (*bullet['color'], 150),
                                 (int(bullet['x']), int(bullet['y'])), bullet['size'])
            elif bullet.get('shield'):
                pygame.draw.circle(surface, (*COLORS['matrix_cyan'], 100),
                                 (int(bullet['x']), int(bullet['y'])), bullet['size'])
            elif bullet.get('time_slow'):
                pygame.draw.circle(surface, (*COLORS['matrix_purple'], 100),
                                 (int(bullet['x']), int(bullet['y'])), bullet['size'])
            else:
                pygame.draw.circle(surface, bullet['color'],
                                 (int(bullet['x']), int(bullet['y'])), bullet['size'])
        
        # Minionları çiz
        for minion in self.minions:
            minion.draw(surface)

# ==================== ENEMY SYSTEM ====================
class Enemy:
    def __init__(self, enemy_type, level=1):
        self.type = enemy_type
        self.level = level
        
        if enemy_type == EnemyType.BASIC:
            self.size = 20 + level * 5
            self.speed = 1 + level * 0.3
            self.health = 20 + level * 10
            self.color = COLORS['matrix_red']
            self.value = 10 * level
            self.shoot_chance = 0.1
            self.ability = None
            
        elif enemy_type == EnemyType.HACKER:
            self.size = 25 + level * 4
            self.speed = 0.8 + level * 0.2
            self.health = 30 + level * 15
            self.color = COLORS['matrix_purple']
            self.value = 15 * level
            self.shoot_chance = 0.15
            self.ability = "disable_powerups"
            self.ability_cooldown = 0
            
        elif enemy_type == EnemyType.GLITCH:
            self.size = 18 + level * 3
            self.speed = 1.5 + level * 0.4
            self.health = 15 + level * 8
            self.color = COLORS['matrix_cyan']
            self.value = 12 * level
            self.shoot_chance = 0.05
            self.ability = "teleport"
            self.teleport_cooldown = 0
            
        elif enemy_type == EnemyType.FIREWALL:
            self.size = 30 + level * 6
            self.speed = 0.5 + level * 0.1
            self.health = 50 + level * 25
            self.color = COLORS['matrix_blue']
            self.value = 20 * level
            self.shoot_chance = 0.2
            self.ability = "shield"
            self.shield_health = 20
            self.max_shield_health = 20
            
        elif enemy_type == EnemyType.VIRUS:
            self.size = 15 + level * 2
            self.speed = 2 + level * 0.5
            self.health = 10 + level * 5
            self.color = COLORS['matrix_orange']
            self.value = 8 * level
            self.shoot_chance = 0.3
            self.ability = "split"
            
        elif enemy_type == EnemyType.WORM:
            self.size = 40 + level * 8
            self.speed = 0.3 + level * 0.05
            self.health = 100 + level * 50
            self.color = COLORS['matrix_brown']
            self.value = 30 * level
            self.shoot_chance = 0.25
            self.ability = "spawn_minions"
            self.spawn_cooldown = 0
            
        elif enemy_type == EnemyType.TROJAN:
            self.size = 22 + level * 4
            self.speed = 0.9 + level * 0.2
            self.health = 25 + level * 12
            self.color = COLORS['matrix_pink']
            self.value = 18 * level
            self.shoot_chance = 0.18
            self.ability = "stealth"
            self.stealth_timer = 0
            
        self.max_health = self.health
        self.x = random.randint(0, WIDTH - self.size)
        self.y = random.randint(-100, -40)
        self.target_x = random.randint(0, WIDTH - self.size)
        self.target_y = random.randint(0, HEIGHT//3)
        self.bullets = []
        self.shoot_timer = random.randint(60, 180)
        self.ai_state = "patrol"
        self.aggro_range = 300 + level * 50
    
    def update(self, player_x=None, player_y=None):
        # AI davranışı
        if player_x is not None and player_y is not None:
            distance_to_player = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
            
            if distance_to_player < self.aggro_range:
                self.ai_state = "attack"
                # Oyuncuyu takip et
                dx = player_x - (self.x + self.size//2)
                dy = player_y - (self.y + self.size//2)
                dist = max(1, math.sqrt(dx*dx + dy*dy))
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed
            else:
                self.ai_state = "patrol"
                # Patrol hareketi
                if abs(self.x - self.target_x) < 10 and abs(self.y - self.target_y) < 10:
                    self.target_x = random.randint(0, WIDTH - self.size)
                    self.target_y = random.randint(0, HEIGHT//3)
                
                dx = self.target_x - self.x
                dy = self.target_y - self.y
                dist = max(1, math.sqrt(dx*dx + dy*dy))
                self.x += (dx/dist) * self.speed * 0.5
                self.y += (dy/dist) * self.speed * 0.5
        
        # Yetenekleri güncelle
        self.update_abilities()
        
        # Ateş etme
        self.shoot_timer -= 1
        if self.shoot_timer <= 0 and random.random() < self.shoot_chance:
            self.shoot()
            self.shoot_timer = random.randint(90, 240)
        
        # Mermileri güncelle
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            if (bullet['x'] < -50 or bullet['x'] > WIDTH + 50 or 
                bullet['y'] < -50 or bullet['y'] > HEIGHT + 50):
                self.bullets.remove(bullet)
    
    def update_abilities(self):
        if self.type == EnemyType.HACKER and self.ability_cooldown > 0:
            self.ability_cooldown -= 1
            
        elif self.type == EnemyType.GLITCH and self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1
            if self.teleport_cooldown == 0:
                # Işınlanma
                self.x = random.randint(0, WIDTH - self.size)
                self.y = random.randint(0, HEIGHT//2)
                self.teleport_cooldown = 180
                
        elif self.type == EnemyType.WORM and self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1
            if self.spawn_cooldown == 0 and self.health < self.max_health * 0.5:
                self.spawn_minions()
                self.spawn_cooldown = 300
                
        elif self.type == EnemyType.TROJAN:
            self.stealth_timer -= 1
            if self.stealth_timer <= 0:
                self.stealth_timer = random.randint(120, 300)
    
    def shoot(self):
        if self.type == EnemyType.VIRUS:
            # Virüs - çoklu ateş
            for angle in range(-30, 31, 15):
                rad = math.radians(angle)
                self.bullets.append({
                    'x': self.x + self.size//2,
                    'y': self.y + self.size,
                    'dx': math.sin(rad) * 2,
                    'dy': math.cos(rad) * 4,
                    'color': self.color,
                    'size': 4
                })
        else:
            # Standart ateş
            self.bullets.append({
                'x': self.x + self.size//2,
                'y': self.y + self.size,
                'dx': 0,
                'dy': 3,
                'color': self.color,
                'size': 6
            })
    
    def spawn_minions(self):
        # Worm için minion üretme
        for _ in range(2):
            minion = Enemy(EnemyType.BASIC, self.level - 1 if self.level > 1 else 1)
            minion.x = self.x + random.randint(-20, 20)
            minion.y = self.y + self.size
            return minion  # GameManager bunu işleyecek
    
    def draw(self, surface):
        # Stealth kontrolü
        if self.type == EnemyType.TROJAN and (self.stealth_timer // 10) % 2 == 0:
            alpha = 100
        else:
            alpha = 255
        
        # Ana gövde
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        if self.type == EnemyType.GLITCH:
            # Glitch efekti
            points = []
            for i in range(8):
                angle = math.radians(45 * i + random.randint(-5, 5))
                radius = self.size//2 + random.randint(-5, 5)
                points.append((
                    self.size//2 + math.cos(angle) * radius,
                    self.size//2 + math.sin(angle) * radius
                ))
            pygame.draw.polygon(s, (*self.color[:3], alpha), points)
        else:
            pygame.draw.rect(s, (*self.color[:3], alpha), (0, 0, self.size, self.size))
        
        surface.blit(s, (self.x, self.y))
        
        # Kalkan (Firewall)
        if self.type == EnemyType.FIREWALL and self.shield_health > 0:
            shield_alpha = 100 + int(155 * (math.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5))
            shield_surf = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
            pygame.draw.rect(shield_surf, (*COLORS['matrix_cyan'], shield_alpha),
                           (0, 0, self.size + 10, self.size + 10), 3)
            surface.blit(shield_surf, (self.x - 5, self.y - 5))
        
        # Detaylar
        if self.type == EnemyType.HACKER:
            # Hacker sembolü
            sym = font.render("⟁", True, COLORS['matrix_white'])
            surface.blit(sym, (self.x + self.size//2 - sym.get_width()//2,
                             self.y + self.size//2 - sym.get_height()//2))
        elif self.type == EnemyType.VIRUS:
            # Virüs sembolü
            pygame.draw.circle(surface, COLORS['matrix_white'],
                             (int(self.x + self.size//2), int(self.y + self.size//2)),
                             self.size//4)
        
        # Sağlık çubuğu
        if self.health < self.max_health:
            health_width = self.size
            health_height = 4
            health_percent = self.health / self.max_health
            
            pygame.draw.rect(surface, COLORS['matrix_dark'],
                           (self.x, self.y - 8, health_width, health_height))
            pygame.draw.rect(surface, COLORS['matrix_green'],
                           (self.x, self.y - 8, health_width * health_percent, health_height))
        
        # Mermileri çiz
        for bullet in self.bullets:
            pygame.draw.circle(surface, bullet['color'],
                             (int(bullet['x']), int(bullet['y'])), bullet['size'])

# ==================== PLAYER CLASS ====================
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.max_shield = 50
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.invulnerable = 0
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_cooldown_base = 20
        self.damage_multiplier = 1.0
        self.critical_chance = 0.0
        self.bullet_pierce = 0
        self.auto_collect_range = 0
        self.shield_regen_rate = 0.0
        
        # Powerup'lar
        self.powerups = {
            'rapid_fire': 0,
            'shield': 0,
            'double_points': 0,
            'time_slow': 0,
            'matrix_vision': 0,
            'nano_bots': 0,
            'quantum': 0
        }
        
        # İstatistikler
        self.stats = {
            'enemies_killed': 0,
            'powerups_collected': 0,
            'waves_completed': 0,
            'shots_fired': 0,
            'shots_hit': 0,
            'damage_taken': 0,
            'play_time': 0,
            'highest_combo': 0
        }
        
        # Görünüm
        self.skin = 'neo'
        self.trail_particles = []
        self.trail_timer = 0
        
        # Matrix Vision
        self.matrix_vision = False
        self.vision_timer = 0
    
    def update(self, keys, time_scale=1.0):
        # Hareket
        move_speed = self.speed * time_scale
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= move_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += move_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= move_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += move_speed
        
        # Ekran sınırları
        self.x = max(0, min(WIDTH - self.width, self.x))
        self.y = max(0, min(HEIGHT - self.height, self.y))
        
        # Ateş etme
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = self.shoot_cooldown_base * time_scale
        
        # Cooldown'ları güncelle
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= time_scale
        
        if self.invulnerable > 0:
            self.invulnerable -= time_scale
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0
        
        # Powerup sürelerini güncelle
        for powerup in self.powerups:
            if self.powerups[powerup] > 0:
                self.powerups[powerup] -= time_scale
        
        # Kalkan regenerasyonu
        if self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + self.shield_regen_rate * time_scale)
        
        # Mermileri güncelle
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed'] * time_scale
            if bullet['y'] < -10:
                self.bullets.remove(bullet)
        
        # İz efekti
        self.trail_timer += time_scale
        if self.trail_timer > 3:
            self.trail_particles.append({
                'x': self.x + self.width//2,
                'y': self.y + self.height,
                'size': random.uniform(2, 4),
                'life': 30,
                'color': COLORS['matrix_green']
            })
            self.trail_timer = 0
        
        # İz parçacıklarını güncelle
        for particle in self.trail_particles[:]:
            particle['life'] -= time_scale
            particle['y'] += 3 * time_scale
            if particle['life'] <= 0:
                self.trail_particles.remove(particle)
        
        # Matrix Vision
        if self.powerups['matrix_vision'] > 0:
            self.matrix_vision = True
            self.vision_timer = self.powerups['matrix_vision']
        elif self.vision_timer > 0:
            self.vision_timer -= time_scale
        else:
            self.matrix_vision = False
        
        # İstatistikler
        self.stats['play_time'] += time_scale
    
    def shoot(self):
        bullet_count = 1
        if self.powerups['rapid_fire'] > 0:
            bullet_count = 3
        if self.powerups['quantum'] > 0:
            bullet_count = 5
        
        for i in range(bullet_count):
            offset = (i - (bullet_count - 1) / 2) * 10
            color = COLORS['matrix_cyan'] if self.powerups['rapid_fire'] > 0 else COLORS['matrix_green']
            if self.powerups['quantum'] > 0:
                color = random.choice([COLORS['matrix_cyan'], COLORS['matrix_purple'], COLORS['matrix_orange']])
            
            self.bullets.append({
                'x': self.x + self.width // 2 + offset,
                'y': self.y,
                'speed': 10,
                'color': color,
                'damage': 10 * self.damage_multiplier,
                'pierce': self.bullet_pierce,
                'pierced_enemies': 0
            })
        
        self.stats['shots_fired'] += bullet_count
        self.shoot_cooldown = self.shoot_cooldown_base
    
    def take_damage(self, amount):
        if self.invulnerable > 0:
            return False
        
        damage_to_shield = min(self.shield, amount)
        self.shield -= damage_to_shield
        
        damage_to_health = amount - damage_to_shield
        if damage_to_health > 0:
            self.health -= damage_to_health
            self.invulnerable = 30
        
        self.stats['damage_taken'] += amount
        
        if self.health <= 0:
            return True
        return False
    
    def add_score(self, points):
        multiplier = 1.0
        if self.powerups['double_points'] > 0:
            multiplier *= 2
        if self.combo > 5:
            multiplier *= 1 + (self.combo - 5) * 0.1
        
        added = int(points * multiplier)
        self.score += added
        return added
    
    def add_combo(self):
        self.combo += 1
        self.combo_timer = 180
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        if self.combo > self.stats['highest_combo']:
            self.stats['highest_combo'] = self.combo
    
    def draw(self, surface):
        # İz efekti
        for particle in self.trail_particles:
            pygame.draw.circle(surface, particle['color'],
                             (int(particle['x']), int(particle['y'])),
                             int(particle['size']))
        
        # Kalkan
        if self.shield > 0 or self.powerups['shield'] > 0:
            shield_alpha = 100 + int(155 * (math.sin(pygame.time.get_ticks() * 0.005) * 0.5 + 0.5))
            shield_surf = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surf, (*COLORS['matrix_cyan'], shield_alpha),
                              (0, 0, self.width + 20, self.height + 20), 3)
            surface.blit(shield_surf, (self.x - 10, self.y - 10))
        
        # Oyuncu gemi
        points = [
            (self.x + self.width // 2, self.y),  # Üst
            (self.x, self.y + self.height),      # Sol alt
            (self.x + self.width, self.y + self.height)  # Sağ alt
        ]
        
        # Titreme efekti (hasar aldığında)
        shake = 0
        if self.invulnerable > 0 and self.invulnerable % 4 < 2:
            shake = random.randint(-2, 2)
        
        # Gemi gövdesi
        ship_color = COLORS['matrix_green']
        if self.skin == 'trinity':
            ship_color = COLORS['matrix_blue']
        elif self.skin == 'morpheus':
            ship_color = COLORS['matrix_purple']
        
        pygame.draw.polygon(surface, ship_color,
                           [(p[0] + shake, p[1] + shake) for p in points])
        
        # Motor ateşi
        fire_height = random.randint(5, 10)
        fire_points = [
            (self.x + self.width // 3, self.y + self.height),
            (self.x + self.width // 2, self.y + self.height + fire_height),
            (self.x + 2 * self.width // 3, self.y + self.height)
        ]
        fire_color = COLORS['matrix_yellow']
        if self.powerups['quantum'] > 0:
            fire_color = random.choice([COLORS['matrix_cyan'], COLORS['matrix_purple']])
        
        pygame.draw.polygon(surface, fire_color, fire_points)
        
        # Mermileri çiz
        for bullet in self.bullets:
            size = 6 if self.powerups['quantum'] > 0 else 4
            pygame.draw.rect(surface, bullet['color'],
                           (bullet['x'] - size//2, bullet['y'] - size*2, size, size*3))
        
        # Matrix Vision efekti
        if self.matrix_vision:
            vision_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for _ in range(20):
                x1 = random.randint(0, WIDTH)
                y1 = random.randint(0, HEIGHT)
                x2 = x1 + random.randint(-50, 50)
                y2 = y1 + random.randint(-50, 50)
                pygame.draw.line(vision_surf, (*COLORS['matrix_cyan'], 50),
                               (x1, y1), (x2, y2), 1)
            surface.blit(vision_surf, (0, 0))

# ==================== POWERUP SYSTEM ====================
class PowerUp:
    def __init__(self, x, y, powerup_type=None):
        self.x = x
        self.y = y
        self.size = 15
        self.type = powerup_type or random.choice(list(PowerUpType))
        self.speed = 2
        self.lifetime = 600
        self.collected = False
        
        # Türlere göre özellikler
        self.colors = {
            PowerUpType.HEALTH: COLORS['matrix_green'],
            PowerUpType.RAPID_FIRE: COLORS['matrix_yellow'],
            PowerUpType.SHIELD: COLORS['matrix_cyan'],
            PowerUpType.DOUBLE_POINTS: COLORS['matrix_purple'],
            PowerUpType.TIME_SLOW: COLORS['matrix_blue'],
            PowerUpType.MATRIX_VISION: COLORS['matrix_white'],
            PowerUpType.NANO_BOTS: COLORS['matrix_orange'],
            PowerUpType.QUANTUM: COLORS['matrix_pink']
        }
        
        self.symbols = {
            PowerUpType.HEALTH: '♥',
            PowerUpType.RAPID_FIRE: '⚡',
            PowerUpType.SHIELD: '⛉',
            PowerUpType.DOUBLE_POINTS: '2x',
            PowerUpType.TIME_SLOW: '⏱',
            PowerUpType.MATRIX_VISION: '👁',
            PowerUpType.NANO_BOTS: '🔬',
            PowerUpType.QUANTUM: '⚛'
        }
        
        self.durations = {
            PowerUpType.HEALTH: 0,  # Anlık
            PowerUpType.RAPID_FIRE: 600,
            PowerUpType.SHIELD: 900,
            PowerUpType.DOUBLE_POINTS: 600,
            PowerUpType.TIME_SLOW: 300,
            PowerUpType.MATRIX_VISION: 450,
            PowerUpType.NANO_BOTS: 750,
            PowerUpType.QUANTUM: 500
        }
        
        self.color = self.colors[self.type]
        self.symbol = self.symbols[self.type]
        self.duration = self.durations[self.type]
    
    def update(self):
        self.y += self.speed
        self.lifetime -= 1
        return self.lifetime > 0 and self.y < HEIGHT + 20 and not self.collected
    
    def apply(self, player):
        if self.type == PowerUpType.HEALTH:
            player.health = min(player.max_health, player.health + 30)
        elif self.type == PowerUpType.RAPID_FIRE:
            player.powerups['rapid_fire'] = max(player.powerups['rapid_fire'], self.duration)
        elif self.type == PowerUpType.SHIELD:
            player.powerups['shield'] = max(player.powerups['shield'], self.duration)
        elif self.type == PowerUpType.DOUBLE_POINTS:
            player.powerups['double_points'] = max(player.powerups['double_points'], self.duration)
        elif self.type == PowerUpType.TIME_SLOW:
            player.powerups['time_slow'] = max(player.powerups['time_slow'], self.duration)
        elif self.type == PowerUpType.MATRIX_VISION:
            player.powerups['matrix_vision'] = max(player.powerups['matrix_vision'], self.duration)
        elif self.type == PowerUpType.NANO_BOTS:
            player.powerups['nano_bots'] = max(player.powerups['nano_bots'], self.duration)
        elif self.type == PowerUpType.QUANTUM:
            player.powerups['quantum'] = max(player.powerups['quantum'], self.duration)
        
        self.collected = True
        return self.duration > 0
    
    def draw(self, surface):
        # Parlama efekti
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.2 + 0.8
        current_size = int(self.size * pulse)
        
        glow_surf = pygame.Surface((current_size * 3, current_size * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, 100),
                          (current_size * 1.5, current_size * 1.5), current_size * 1.5)
        surface.blit(glow_surf, (self.x - current_size * 1.5, self.y - current_size * 1.5))
        
        # Ana gövde
        pygame.draw.circle(surface, self.color,
                          (int(self.x), int(self.y)), current_size)
        
        # Sembol
        symbol_surf = font.render(self.symbol, True, COLORS['black'])
        surface.blit(symbol_surf,
                    (self.x - symbol_surf.get_width() // 2,
                     self.y - symbol_surf.get_height() // 2))

# ==================== WEATHER SYSTEM ====================
class WeatherSystem:
    def __init__(self):
        self.current_weather = WeatherType.CLEAR
        self.weather_intensity = 0
        self.weather_timer = 0
        self.particles = []
        self.effects = []
        
    def set_weather(self, weather_type, intensity=1.0, duration=900):
        self.current_weather = weather_type
        self.weather_intensity = intensity
        self.weather_timer = duration
        
        if weather_type == WeatherType.DATA_RAIN:
            self.create_data_rain(intensity)
        elif weather_type == WeatherType.GLITCH_STORM:
            self.create_glitch_storm(intensity)
        elif weather_type == WeatherType.MATRIX_OVERLOAD:
            self.create_matrix_overload(intensity)
        elif weather_type == WeatherType.CYBER_SNOW:
            self.create_cyber_snow(intensity)
    
    def create_data_rain(self, intensity):
        for _ in range(int(100 * intensity)):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-100, 0),
                'char': random.choice(MATRIX_CHARS),
                'speed': random.uniform(2, 6) * intensity,
                'color': random.choice([
                    COLORS['matrix_green'],
                    COLORS['matrix_cyan'],
                    COLORS['matrix_blue']
                ]),
                'life': random.randint(100, 300),
                'size': random.uniform(0.8, 1.2)
            })
    
    def create_glitch_storm(self, intensity):
        for _ in range(int(50 * intensity)):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'char': random.choice(MATRIX_CHARS),
                'speed_x': random.uniform(-3, 3) * intensity,
                'speed_y': random.uniform(-3, 3) * intensity,
                'color': COLORS['matrix_purple'],
                'life': random.randint(60, 180),
                'glitch': True,
                'glitch_timer': random.randint(0, 30)
            })
    
    def create_matrix_overload(self, intensity):
        # Ekran titremesi efekti
        self.effects.append({
            'type': 'screen_shake',
            'intensity': intensity * 10,
            'duration': 30
        })
        
        # Rastgele glitch çizgileri
        for _ in range(int(20 * intensity)):
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            length = random.randint(50, 200) * intensity
            angle = random.uniform(0, math.pi * 2)
            x2 = x1 + math.cos(angle) * length
            y2 = y1 + math.sin(angle) * length
            
            self.effects.append({
                'type': 'glitch_line',
                'x1': x1, 'y1': y1,
                'x2': x2, 'y2': y2,
                'color': random.choice([COLORS['matrix_red'], COLORS['matrix_purple']]),
                'life': random.randint(10, 30)
            })
    
    def create_cyber_snow(self, intensity):
        for _ in range(int(200 * intensity)):
            self.particles.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(-50, 0),
                'char': '·',
                'speed': random.uniform(1, 3) * intensity,
                'color': COLORS['matrix_cyan'],
                'life': random.randint(150, 400),
                'drift': random.uniform(-0.5, 0.5),
                'size': random.uniform(0.5, 1.5)
            })
    
    def update(self):
        self.weather_timer = max(0, self.weather_timer - 1)
        
        if self.weather_timer == 0 and self.current_weather != WeatherType.CLEAR:
            self.current_weather = WeatherType.CLEAR
            self.particles.clear()
            return
        
        # Parçacıkları güncelle
        for particle in self.particles[:]:
            if self.current_weather == WeatherType.DATA_RAIN:
                particle['y'] += particle['speed']
                if particle['y'] > HEIGHT:
                    particle['y'] = random.randint(-100, 0)
                    particle['x'] = random.randint(0, WIDTH)
                    
            elif self.current_weather == WeatherType.GLITCH_STORM:
                particle['x'] += particle['speed_x']
                particle['y'] += particle['speed_y']
                particle['glitch_timer'] -= 1
                if particle['glitch_timer'] <= 0:
                    particle['char'] = random.choice(MATRIX_CHARS)
                    particle['glitch_timer'] = random.randint(10, 30)
                
                # Ekran sınırları
                if particle['x'] < -100 or particle['x'] > WIDTH + 100:
                    particle['x'] = random.randint(0, WIDTH)
                if particle['y'] < -100 or particle['y'] > HEIGHT + 100:
                    particle['y'] = random.randint(0, HEIGHT)
                    
            elif self.current_weather == WeatherType.CYBER_SNOW:
                particle['y'] += particle['speed']
                particle['x'] += particle['drift']
                if particle['y'] > HEIGHT:
                    particle['y'] = random.randint(-50, 0)
                    particle['x'] = random.randint(0, WIDTH)
            
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # Efektleri güncelle
        for effect in self.effects[:]:
            effect['life'] = effect.get('life', 1) - 1
            if effect['life'] <= 0:
                self.effects.remove(effect)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = min(255, particle['life'] * 2)
            color = (*particle['color'][:3], alpha)
            
            if 'size' in particle:
                size = particle['size']
                char_surf = pygame.font.Font(None, int(FONT_SIZE * size)).render(
                    particle['char'], True, color)
            else:
                char_surf = font.render(particle['char'], True, color)
            
            surface.blit(char_surf, (int(particle['x']), int(particle['y'])))
        
        for effect in self.effects:
            if effect['type'] == 'glitch_line':
                alpha = min(255, effect['life'] * 25)
                color = (*effect['color'][:3], alpha)
                pygame.draw.line(surface, color,
                               (effect['x1'], effect['y1']),
                               (effect['x2'], effect['y2']), 2)
    
    def get_screen_shake(self):
        for effect in self.effects:
            if effect['type'] == 'screen_shake':
                return effect['intensity'] * (effect['life'] / effect['duration'])
        return 0

# ==================== MATRIX RAIN BACKGROUND ====================
class MatrixRain:
    def __init__(self, intensity=1.0):
        self.columns = []
        self.intensity = intensity
        self.column_spacing = 20
        self.setup_columns()
        self.glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.scanline_pos = 0
        self.scanline_speed = 3
    
    def setup_columns(self):
        num_columns = int(WIDTH // self.column_spacing * self.intensity)
        for i in range(num_columns):
            x = random.randint(0, WIDTH)
            speed = random.uniform(1, 4) * self.intensity
            length = random.randint(5, 20)
            sparkle = random.random() > 0.7
            self.columns.append(MatrixColumn(x, speed, length, sparkle))
    
    def update(self, time_scale=1.0):
        for column in self.columns:
            column.update(time_scale)
            if column.y > HEIGHT + column.length * FONT_SIZE:
                column.reset()
        
        self.scanline_pos += self.scanline_speed * time_scale
        if self.scanline_pos > HEIGHT + 50:
            self.scanline_pos = -50
    
    def draw(self, surface):
        # Yarı saydam siyah katman
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Kod yağmuru
        for column in self.columns:
            column.draw(surface)
        
        # Hafif tarama çizgisi
        scanline = pygame.Surface((WIDTH, 30), pygame.SRCALPHA)
        scanline.fill((0, 100, 0, 30))
        surface.blit(scanline, (0, self.scanline_pos - 15))

class MatrixColumn:
    def __init__(self, x, speed, length, sparkle):
        self.x = x
        self.speed = speed
        self.length = length
        self.sparkle = sparkle
        self.reset()
        self.last_update = pygame.time.get_ticks()
    
    def reset(self):
        self.y = random.randint(-HEIGHT, 0)
        self.chars = [random.choice(MATRIX_CHARS) for _ in range(self.length)]
        self.brightness = [1.0] * self.length
        self.colors = [self.get_char_color(i) for i in range(self.length)]
    
    def get_char_color(self, index):
        if index == 0:
            return COLORS['matrix_white']
        elif index < 3:
            return COLORS['matrix_light_green']
        elif index < 6:
            return COLORS['matrix_green']
        else:
            dark_green = tuple(int(c * 0.4) for c in COLORS['matrix_green'])
            return dark_green
    
    def update(self, time_scale):
        current_time = pygame.time.get_ticks()
        
        self.y += self.speed * time_scale
        
        if current_time - self.last_update > 80:
            self.chars.pop(0)
            self.chars.append(random.choice(MATRIX_CHARS))
            self.last_update = current_time
            
            self.brightness.insert(0, 1.0)
            if len(self.brightness) > self.length:
                self.brightness = self.brightness[:self.length]
            
            # Rastgele renk değişimi
            if random.random() < 0.1:
                self.colors = [self.get_char_color(i) for i in range(self.length)]
    
    def draw(self, surface):
        for i in range(min(self.length, len(self.chars))):
            char = self.chars[i]
            brightness = self.brightness[i] * (1.0 - i/self.length)
            color = self.colors[i]
            
            # Parlaklık uygula
            actual_color = tuple(int(c * brightness) for c in color)
            
            if i == 0 and self.sparkle:
                glow_surf = pygame.Surface((FONT_SIZE, FONT_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*actual_color, 100),
                                  (FONT_SIZE//2, FONT_SIZE//2),
                                  FONT_SIZE//2)
                surface.blit(glow_surf,
                            (self.x - FONT_SIZE//2,
                             self.y - i * FONT_SIZE - FONT_SIZE//2))
            
            char_surface = font.render(char, True, actual_color)
            surface.blit(char_surface,
                        (self.x, self.y - i * FONT_SIZE))

# ==================== TIME MANIPULATION ====================
class TimeManipulation:
    def __init__(self):
        self.slow_motion = False
        self.slow_factor = 0.3
        self.duration = 0
        self.cooldown = 0
        self.effects = []
    
    def activate_slow_motion(self, duration=300, factor=0.3):
        if self.cooldown <= 0:
            self.slow_motion = True
            self.slow_factor = factor
            self.duration = duration
            self.cooldown = 900
            
            # Efekt ekle
            self.effects.append({
                'type': 'time_wave',
                'radius': 0,
                'max_radius': min(WIDTH, HEIGHT),
                'speed': 10,
                'color': COLORS['matrix_blue']
            })
            return True
        return False
    
    def update(self):
        if self.slow_motion:
            self.duration -= 1
            if self.duration <= 0:
                self.slow_motion = False
        
        if self.cooldown > 0:
            self.cooldown -= 1
        
        # Efektleri güncelle
        for effect in self.effects[:]:
            if effect['type'] == 'time_wave':
                effect['radius'] += effect['speed']
                if effect['radius'] > effect['max_radius']:
                    self.effects.remove(effect)
    
    def get_time_scale(self):
        return self.slow_factor if self.slow_motion else 1.0
    
    def draw(self, surface):
        for effect in self.effects:
            if effect['type'] == 'time_wave':
                alpha = max(0, 100 - (effect['radius'] / effect['max_radius']) * 100)
                wave_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(wave_surf, (*effect['color'], alpha),
                                  (WIDTH//2, HEIGHT//2), effect['radius'], 5)
                surface.blit(wave_surf, (0, 0))

# ==================== AI ASSISTANT ====================
class AIAssistant:
    def __init__(self):
        self.name = "ORACLE"
        self.active = True
        self.messages = []
        self.message_timer = 0
        self.tips = [
            "Enemy patterns repeat! Learn them!",
            "Save shield powerups for boss fights!",
            "Use corners for cover!",
            "Chain combos for score multipliers!",
            "Different enemies have different weak points!",
            "Upgrade fire rate early for easier clears!",
            "Watch for hacker enemies - they disable powerups!",
            "Glitch enemies teleport when low on health!",
            "Firewall enemies have shields - break them first!",
            "Virus enemies split when destroyed!",
            "Worm enemies spawn minions!",
            "Trojan enemies can turn invisible!",
            "Use matrix vision to see hidden enemies!",
            "Time slow is perfect for crowded situations!",
            "Nano bots automatically repair your ship!",
            "Quantum powerups give random bonuses!",
        ]
    
    def give_tip(self, game_situation=None):
        if not self.active or self.message_timer > 0:
            return
        
        tip = random.choice(self.tips)
        self.messages.append({
            'text': tip,
            'color': COLORS['matrix_cyan'],
            'timer': 300
        })
        self.message_timer = 600  # 10 saniye
    
    def give_situational_tip(self, game_situation):
        if not self.active or self.message_timer > 0:
            return
        
        if game_situation['player_health'] < 30:
            tip = "Health critical! Find health powerups!"
        elif game_situation['enemies'] > 15:
            tip = "Swarm incoming! Use area attacks!"
        elif game_situation['boss_active']:
            tip = "Boss weak points exposed! Aim carefully!"
        elif game_situation['combo'] > 10:
            tip = f"Amazing! {game_situation['combo']}x combo! Keep it up!"
        elif game_situation['accuracy'] < 0.3:
            tip = "Aim for accuracy! Every shot counts!"
        else:
            tip = random.choice(self.tips)
        
        self.messages.append({
            'text': tip,
            'color': COLORS['matrix_cyan'],
            'timer': 300
        })
        self.message_timer = 600
    
    def update(self):
        self.message_timer = max(0, self.message_timer - 1)
        
        for message in self.messages[:]:
            message['timer'] -= 1
            if message['timer'] <= 0:
                self.messages.remove(message)
    
    def draw(self, surface):
        y_offset = HEIGHT - 100
        for message in reversed(self.messages[-3:]):  # Son 3 mesaj
            alpha = min(255, message['timer'] * 2)
            color = (*message['color'][:3], alpha)
            
            # Arkaplan
            text_surf = font.render(message['text'], True, color)
            bg_rect = pygame.Rect(20, y_offset - 5, text_surf.get_width() + 20, 30)
            pygame.draw.rect(surface, (0, 20, 0, alpha//2), bg_rect)
            pygame.draw.rect(surface, (*COLORS['matrix_green'][:3], alpha//2), bg_rect, 2)
            
            # Metin
            surface.blit(text_surf, (30, y_offset))
            y_offset -= 35

# ==================== STATISTICS & ACHIEVEMENTS ====================
class Statistics:
    def __init__(self):
        self.stats = {
            'total_score': 0,
            'highest_wave': 0,
            'enemies_killed': 0,
            'powerups_collected': 0,
            'total_play_time': 0,
            'total_shots': 0,
            'total_hits': 0,
            'accuracy': 0.0,
            'damage_taken': 0,
            'highest_combo': 0,
            'games_played': 0,
            'games_won': 0,
            'bosses_defeated': 0,
        }
        self.achievements = [
            Achievement("first_blood", "First Blood", "Kill your first enemy", "🩸"),
            Achievement("matrix_initiate", "Matrix Initiate", "Reach wave 5", "🎯"),
            Achievement("untouchable", "Untouchable", "Complete a wave without taking damage", "🛡️"),
            Achievement("combo_master", "Combo Master", "Achieve a 20x combo", "⚡"),
            Achievement("perfectionist", "Perfectionist", "Achieve 90% accuracy", "🏆"),
            Achievement("boss_slayer", "Boss Slayer", "Defeat your first boss", "👹"),
            Achievement("upgrade_expert", "Upgrade Expert", "Max out an upgrade", "⭐"),
            Achievement("collector", "Collector", "Collect 100 powerups", "📦"),
            Achievement("survivor", "Survivor", "Survive for 10 minutes", "⏳"),
            Achievement("millionaire", "Millionaire", "Score 1,000,000 points", "💰"),
        ]
        self.load_stats()
    
    def update(self, game_stats):
        for key in game_stats:
            if key in self.stats:
                if key == 'accuracy':
                    shots = max(1, game_stats.get('shots_fired', 1))
                    hits = game_stats.get('shots_hit', 0)
                    self.stats[key] = max(self.stats[key], (hits / shots) * 100)
                else:
                    self.stats[key] += game_stats[key]
        
        self.check_achievements(game_stats)
    
    def check_achievements(self, game_stats):
        if game_stats.get('enemies_killed', 0) > 0:
            self.unlock_achievement("first_blood")
        
        if game_stats.get('waves_completed', 0) >= 5:
            self.unlock_achievement("matrix_initiate")
        
        if game_stats.get('highest_combo', 0) >= 20:
            self.unlock_achievement("combo_master")
        
        shots = max(1, game_stats.get('shots_fired', 1))
        hits = game_stats.get('shots_hit', 0)
        if (hits / shots) >= 0.9:
            self.unlock_achievement("perfectionist")
    
    def unlock_achievement(self, achievement_id):
        for achievement in self.achievements:
            if achievement.id == achievement_id and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlock_time = pygame.time.get_ticks()
                return achievement
        return None
    
    
    
    
    def save_stats(self):
        try:
            with open('matrix_stats.json', 'w') as f:
                # Dataclass'ları dict'e çevir
                data = {
                    'stats': self.stats,
                    'achievements': [
                        {
                            'id': a.id,
                            'name': a.name,
                            'description': a.description,
                            'icon': a.icon,
                            'unlocked': a.unlocked,
                            'unlock_time': a.unlock_time
                        }
                        for a in self.achievements
                    ]
                }
                json.dump(data, f)
        except:
            pass
    
    def load_stats(self):
        try:
            with open('matrix_stats.json', 'r') as f:
                data = json.load(f)
                self.stats.update(data.get('stats', {}))
                
                for saved_ach in data.get('achievements', []):
                    for ach in self.achievements:
                        if ach.id == saved_ach['id']:
                            ach.unlocked = saved_ach['unlocked']
                            ach.unlock_time = saved_ach.get('unlock_time')
                            break
        except:
            pass
    
    def draw(self, surface, show_all=False):
        if show_all:
            # Tam istatistik ekranı
            self.draw_full_stats(surface)
        else:
            # Oyun içi mini istatistik
            self.draw_mini_stats(surface)
    
    def draw_mini_stats(self, surface):
        stats_text = [
            f"Kills: {self.stats['enemies_killed']}",
            f"Accuracy: {self.stats['accuracy']:.1f}%",
            f"Play Time: {int(self.stats['total_play_time']//60)}m",
            f"High Score: {self.stats['total_score']}",
            f"Achievements: {sum(1 for a in self.achievements if a.unlocked)}/{len(self.achievements)}"
        ]
        
        pygame.draw.rect(surface, (0, 20, 0, 180), (WIDTH - 220, HEIGHT - 180, 200, 160))
        pygame.draw.rect(surface, COLORS['matrix_green'], (WIDTH - 220, HEIGHT - 180, 200, 160), 2)
        
        title = font.render("STATISTICS", True, COLORS['matrix_cyan'])
        surface.blit(title, (WIDTH - 220 + 100 - title.get_width()//2, HEIGHT - 170))
        
        y_offset = HEIGHT - 140
        for text in stats_text:
            text_surf = small_font.render(text, True, COLORS['matrix_white'])
            surface.blit(text_surf, (WIDTH - 210, y_offset))
            y_offset += 25
    
    def draw_full_stats(self, surface):
        # Arkaplan
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Ana kutu
        stats_rect = pygame.Rect(100, 50, WIDTH - 200, HEIGHT - 100)
        pygame.draw.rect(surface, (0, 30, 0, 220), stats_rect)
        pygame.draw.rect(surface, COLORS['matrix_green'], stats_rect, 4)
        
        # Başlık
        title = large_font.render("GAME STATISTICS", True, COLORS['matrix_cyan'])
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        
        # İstatistikler (sol taraf)
        stats_left = [
            f"Total Score: {self.stats['total_score']:,}",
            f"Highest Wave: {self.stats['highest_wave']}",
            f"Enemies Killed: {self.stats['enemies_killed']:,}",
            f"Powerups Collected: {self.stats['powerups_collected']:,}",
            f"Total Play Time: {int(self.stats['total_play_time']//3600)}h {int((self.stats['total_play_time']%3600)//60)}m",
            f"Accuracy: {self.stats['accuracy']:.2f}%",
            f"Games Played: {self.stats['games_played']}",
            f"Games Won: {self.stats['games_won']}",
            f"Bosses Defeated: {self.stats['bosses_defeated']}",
        ]
        
        y_offset = 150
        for text in stats_left:
            text_surf = font.render(text, True, COLORS['matrix_white'])
            surface.blit(text_surf, (200, y_offset))
            y_offset += 40
        
        # Başarımlar (sağ taraf)
        ach_title = medium_font.render("ACHIEVEMENTS", True, COLORS['matrix_yellow'])
        surface.blit(ach_title, (WIDTH//2 + 100, 150))
        
        y_offset = 200
        for achievement in self.achievements:
            color = COLORS['matrix_green'] if achievement.unlocked else COLORS['matrix_gray']
            icon = achievement.icon if achievement.unlocked else "❓"
            
            ach_text = font.render(f"{icon} {achievement.name}", True, color)
            surface.blit(ach_text, (WIDTH//2 + 100, y_offset))
            
            if achievement.unlocked:
                desc_text = small_font.render(achievement.description, True, COLORS['matrix_light_green'])
                surface.blit(desc_text, (WIDTH//2 + 130, y_offset + 25))
                y_offset += 50
            else:
                y_offset += 35
        
        # Çıkış butonu
        exit_rect = pygame.Rect(WIDTH//2 - 50, HEIGHT - 80, 100, 40)
        pygame.draw.rect(surface, COLORS['matrix_red'], exit_rect)
        pygame.draw.rect(surface, COLORS['matrix_white'], exit_rect, 2)
        exit_text = font.render("BACK", True, COLORS['white'])
        surface.blit(exit_text, (exit_rect.x + 30, exit_rect.y + 10))

# ==================== CUTSCENE MANAGER ====================
class CutsceneManager:
    def __init__(self):
        self.active_cutscene = None
        self.cutscene_timer = 0
        self.text_lines = []
        self.current_line = 0
        self.char_index = 0
        self.char_timer = 0
        self.images = []
        
    def play_cutscene(self, cutscene_name):
        self.active_cutscene = cutscene_name
        self.cutscene_timer = 0
        self.text_lines = []
        self.current_line = 0
        self.char_index = 0
        self.char_timer = 0
        self.images = []
        
        if cutscene_name == "intro":
            self.text_lines = [
                "SYSTEM BOOTING...",
                "MATRIX CONNECTION ESTABLISHED",
                "YOU ARE THE ONE",
                "THE SYSTEM SEEKS TO CONTROL YOU",
                "BUT YOU CAN CONTROL THE SYSTEM",
                "BREAK THE CHAINS",
                "REDEFINE REALITY",
                "BEGIN SIMULATION..."
            ]
        elif cutscene_name == "boss_intro":
            self.text_lines = [
                "WARNING: SYSTEM ANOMALY DETECTED",
                "BOSS ENTITY MANIFESTING",
                "EXTREME DANGER LEVEL",
                "PREPARE FOR TERMINATION PROTOCOL"
            ]
        elif cutscene_name == "game_over":
            self.text_lines = [
                "SIMULATION TERMINATED",
                "NEURAL LINK SEVERED",
                "THE SYSTEM ABSORBS YOUR CONSCIOUSNESS",
                "YOU BECOME PART OF THE CODE",
                "BUT REMEMBER...",
                "THIS IS NOT THE END",
                "IT IS ONLY THE BEGINNING"
            ]
    
    def update(self):
        if not self.active_cutscene:
            return False
        
        self.cutscene_timer += 1
        self.char_timer += 1
        
        # Yazı animasyonu
        if self.char_timer >= 3 and self.current_line < len(self.text_lines):
            self.char_index += 1
            if self.char_index > len(self.text_lines[self.current_line]):
                self.current_line += 1
                self.char_index = 0
            self.char_timer = 0
        
        # Cutscene bitişi
        if self.current_line >= len(self.text_lines) and self.cutscene_timer > 180:
            self.active_cutscene = None
            return True
        
        return False
    
    def draw(self, surface):
        if not self.active_cutscene:
            return
        
        # Karanlık arkaplan
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Matrix efekti arkaplan
        for _ in range(20):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            char = random.choice(MATRIX_CHARS)
            color = random.choice([COLORS['matrix_green'], COLORS['matrix_cyan']])
            char_surf = small_font.render(char, True, (*color, 100))
            surface.blit(char_surf, (x, y))
        
        # Metin kutusu
        text_box = pygame.Rect(100, HEIGHT//2 - 100, WIDTH - 200, 200)
        pygame.draw.rect(surface, (0, 30, 0, 220), text_box)
        pygame.draw.rect(surface, COLORS['matrix_green'], text_box, 4)
        
        # Metinleri çiz
        y_offset = HEIGHT//2 - 80
        for i in range(max(0, self.current_line - 2), min(self.current_line + 1, len(self.text_lines))):
            text = self.text_lines[i]
            
            if i == self.current_line:
                display_text = text[:self.char_index]
                color = COLORS['matrix_white']
            else:
                display_text = text
                color = COLORS['matrix_gray']
            
            text_surf = font.render(display_text, True, color)
            surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_offset))
            y_offset += 40
        
        # Devam etmek için basın yazısı
        if self.current_line >= len(self.text_lines):
            continue_text = font.render("PRESS ANY KEY TO CONTINUE", True, COLORS['matrix_cyan'])
            surface.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 100))

# ==================== MAIN GAME MANAGER ====================
class GameManager:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.player = Player()
        self.matrix_rain = MatrixRain(1.0)
        self.upgrade_system = UpgradeSystem()
        self.mission_system = MissionSystem()
        self.weather_system = WeatherSystem()
        self.time_manipulation = TimeManipulation()
        self.ai_assistant = AIAssistant()
        self.statistics = Statistics()
        self.cutscene_manager = CutsceneManager()
        self.particle_system = ParticleSystem()
        
        # Oyun verileri
        self.enemies = []
        self.powerups = []
        self.boss = None
        self.enemy_spawn_timer = 0
        self.wave = 1
        self.enemies_per_wave = 8
        self.enemies_spawned = 0
        self.wave_timer = 0
        self.game_time = 0
        self.screen_shake = 0
        
        # Multiplayer (temel)
        self.multiplayer = False
        self.players = [self.player]
        
        # Hava durumu değişimi
        self.weather_change_timer = random.randint(600, 1800)
        
        # Seviye editörü
        self.editor_mode = False
        self.editor_grid = []
        
        # Kayıtlar
        self.high_scores = []
        self.load_high_scores()
    
    def load_high_scores(self):
        try:
            with open('matrix_highscores.json', 'r') as f:
                self.high_scores = json.load(f)
        except:
            self.high_scores = [
                {"name": "NEO", "score": 1000000, "wave": 20, "time": 3600},
                {"name": "TRINITY", "score": 750000, "wave": 15, "time": 2700},
                {"name": "MORPHEUS", "score": 500000, "wave": 10, "time": 1800},
                {"name": "ORACLE", "score": 250000, "wave": 5, "time": 900},
                {"name": "AGENT", "score": 100000, "wave": 3, "time": 300},
            ]
    
    def save_high_score(self, name, score, wave, time):
        self.high_scores.append({
            "name": name[:10],
            "score": score,
            "wave": wave,
            "time": time
        })
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]
        
        try:
            with open('matrix_highscores.json', 'w') as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def start_game(self):
        self.state = GameState.PLAYING
        self.cutscene_manager.play_cutscene("intro")
        
        # Oyunu sıfırla
        self.player = Player()
        self.enemies = []
        self.powerups = []
        self.boss = None
        self.wave = 1
        self.enemies_spawned = 0
        self.game_time = 0
        self.screen_shake = 0
        
        # İlk görevleri seç
        self.mission_system.select_starting_missions()
        
        # İlk hava durumu
        self.weather_system.set_weather(
            random.choice([WeatherType.DATA_RAIN, WeatherType.CLEAR]),
            random.uniform(0.5, 1.0),
            random.randint(600, 1200)
        )
    
    def update(self, keys):
        time_scale = self.time_manipulation.get_time_scale()
        
        # Cutscene kontrolü
        if self.cutscene_manager.active_cutscene:
            if self.cutscene_manager.update():
                if self.cutscene_manager.active_cutscene == "game_over":
                    self.state = GameState.GAME_OVER
            return
        
        # Oyun durumuna göre güncelle
        if self.state == GameState.PLAYING:
            self.game_time += 1
            
            # Sistemleri güncelle
            self.matrix_rain.update(time_scale)
            self.weather_system.update()
            self.time_manipulation.update()
            self.ai_assistant.update()
            self.particle_system.update()
            
            # Ekran titremesi
            screen_shake = self.weather_system.get_screen_shake()
            if self.player.invulnerable > 0 and self.player.invulnerable % 4 < 2:
                screen_shake += 5
            self.screen_shake = screen_shake * 0.9
            
            # Oyuncuyu güncelle
            self.player.update(keys, time_scale)
            
            # Hava durumu değişimi
            self.weather_change_timer -= 1
            if self.weather_change_timer <= 0:
                new_weather = random.choice(list(WeatherType))
                self.weather_system.set_weather(
                    new_weather,
                    random.uniform(0.5, 1.5),
                    random.randint(300, 900)
                )
                self.weather_change_timer = random.randint(600, 1800)
            
            # Boss kontrolü
            if self.boss:
                self.update_boss(time_scale)
            else:
                # Normal dalga
                self.update_wave(time_scale)
            
            # Çarpışma tespiti
            self.check_collisions()
            
            # Görev ilerlemesi
            game_data = {
                'enemies_killed': self.player.stats['enemies_killed'],
                'powerups_collected': self.player.stats['powerups_collected'],
                'waves_completed': self.wave - 1,
                'shots_fired': self.player.stats['shots_fired'],
                'shots_hit': self.player.stats['shots_hit'],
                'accuracy': self.player.stats['shots_hit'] / max(1, self.player.stats['shots_fired']),
                'combo': self.player.combo,
                'player_health': self.player.health,
                'enemies': len(self.enemies),
                'boss_active': self.boss is not None
            }
            self.mission_system.update_progress(game_data)
            
            # AI Assistant ipuçları
            if random.random() < 0.001:  # 0.1% chance per frame
                self.ai_assistant.give_situational_tip(game_data)
            
            # Oyun bitti mi?
            if self.player.health <= 0:
                self.end_game()
        
        elif self.state == GameState.PAUSED:
            # Duraklatılmış durumda sadece parçacıklar
            self.particle_system.update()
    
    def update_wave(self, time_scale):
        # Düşman spawn etme
        self.enemy_spawn_timer -= time_scale
        if (self.enemy_spawn_timer <= 0 and 
            self.enemies_spawned < self.wave * self.enemies_per_wave):
            
            # Zorluk seviyesine göre düşman türü seç
            enemy_types = [EnemyType.BASIC]
            if self.wave >= 2:
                enemy_types.extend([EnemyType.HACKER, EnemyType.GLITCH])
            if self.wave >= 3:
                enemy_types.append(EnemyType.FIREWALL)
            if self.wave >= 4:
                enemy_types.append(EnemyType.VIRUS)
            if self.wave >= 5:
                enemy_types.append(EnemyType.WORM)
            if self.wave >= 6:
                enemy_types.append(EnemyType.TROJAN)
            
            enemy_type = random.choice(enemy_types)
            level = min(5, 1 + (self.wave - 1) // 2)
            
            enemy = Enemy(enemy_type, level)
            self.enemies.append(enemy)
            self.enemies_spawned += 1
            self.enemy_spawn_timer = max(10, 60 - self.wave * 3)
        
        # Dalga tamamlandı mı?
        if (self.enemies_spawned >= self.wave * self.enemies_per_wave and 
            len(self.enemies) == 0):
            
            self.wave += 1
            self.enemies_spawned = 0
            self.enemy_spawn_timer = 120  # Dalga arası bekleme
            
            # Her 5 dalgada bir boss
            if self.wave % 5 == 0:
                self.spawn_boss()
            else:
                # Yeni dalga başlangıcı
                self.player.add_score(1000 * self.wave)
                
                # Rastgele powerup düşür
                if random.random() < 0.5:
                    self.powerups.append(PowerUp(
                        random.randint(100, WIDTH-100),
                        random.randint(50, 200)
                    ))
            
            # Görev ilerlemesi
            self.player.stats['waves_completed'] += 1
            
            # İstatistik güncelleme
            if self.wave > self.statistics.stats['highest_wave']:
                self.statistics.stats['highest_wave'] = self.wave
        
        # Düşmanları güncelle
        for enemy in self.enemies[:]:
            enemy.update(self.player.x + self.player.width//2, 
                        self.player.y + self.player.height//2)
            
            # Ekran dışına çıkma kontrolü
            if enemy.y > HEIGHT + 50:
                self.enemies.remove(enemy)
                self.player.take_damage(5 * enemy.level)
        
        # Powerup'ları güncelle
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)
                continue
            
            # Otomatik toplama
            if self.player.auto_collect_range > 0:
                distance = math.sqrt(
                    (powerup.x - (self.player.x + self.player.width//2))**2 +
                    (powerup.y - (self.player.y + self.player.height//2))**2
                )
                if distance < self.player.auto_collect_range:
                    self.collect_powerup(powerup)
                    self.powerups.remove(powerup)
    
    def update_boss(self, time_scale):
        if not self.boss:
            return
        
        self.boss.update(self.player.x + self.player.width//2,
                        self.player.y + self.player.height//2)
        
        # Boss öldü mü?
        if self.boss.health <= 0:
            # Boss ödülü
            reward = 5000 * self.boss.wave
            self.player.add_score(reward)
            self.player.stats['bosses_defeated'] += 1
            
            # Büyük patlama efekti
            self.particle_system.add_explosion(
                self.boss.x + self.boss.size//2,
                self.boss.y + self.boss.size//2,
                COLORS['matrix_cyan'],
                100
            )
            
            # Powerup yağmuru
            for _ in range(5):
                self.powerups.append(PowerUp(
                    self.boss.x + random.randint(-50, 50),
                    self.boss.y + random.randint(-50, 50)
                ))
            
            self.boss = None
            self.wave += 1
            self.enemies_spawned = 0
            self.enemy_spawn_timer = 180
            
            # İstatistik
            self.statistics.stats['bosses_defeated'] += 1
            
            return
        
        # Boss mermileri ile çarpışma
        for bullet in self.boss.bullets[:]:
            if (bullet['x'] > self.player.x and
                bullet['x'] < self.player.x + self.player.width and
                bullet['y'] > self.player.y and
                bullet['y'] < self.player.y + self.player.height):
                
                damage = 20 if bullet.get('laser') else 10
                if self.player.take_damage(damage):
                    self.end_game()
                    return
                
                # Patlama efekti
                self.particle_system.add_explosion(bullet['x'], bullet['y'], bullet['color'])
                if not bullet.get('shield') and not bullet.get('time_slow'):
                    self.boss.bullets.remove(bullet)
        
        # Boss minionları
        for minion in self.boss.minions[:]:
            minion.update(self.player.x + self.player.width//2,
                         self.player.y + self.player.height//2)
            
            # Minion çarpışması
            if (self.player.x < minion.x + minion.size and
                self.player.x + self.player.width > minion.x and
                self.player.y < minion.y + minion.size and
                self.player.y + self.player.height > minion.y):
                
                if self.player.take_damage(minion.level * 8):
                    self.end_game()
                    return
            
            # Minion mermileri
            for bullet in minion.bullets:
                if (bullet['x'] > self.player.x and
                    bullet['x'] < self.player.x + self.player.width and
                    bullet['y'] > self.player.y and
                    bullet['y'] < self.player.y + self.player.height):
                    
                    if self.player.take_damage(minion.level * 3):
                        self.end_game()
                        return
    
    def spawn_boss(self):
        self.boss = MatrixBoss(self.wave // 5)
        self.cutscene_manager.play_cutscene("boss_intro")
        
        # Tüm düşmanları temizle
        self.enemies.clear()
        self.enemies_spawned = self.wave * self.enemies_per_wave
    
    def check_collisions(self):
        # Oyuncu mermileri ile düşmanlar
        for bullet in self.player.bullets[:]:
            bullet_hit = False
            
            # Düşmanlar ile çarpışma
            for enemy in self.enemies[:]:
                if (bullet['x'] > enemy.x and
                    bullet['x'] < enemy.x + enemy.size and
                    bullet['y'] > enemy.y and
                    bullet['y'] < enemy.y + enemy.size):
                    
                    # Hasar hesapla
                    damage = bullet['damage']
                    if random.random() < self.player.critical_chance:
                        damage *= 2
                    
                    # Firewall kalkanı
                    if enemy.type == EnemyType.FIREWALL and enemy.shield_health > 0:
                        enemy.shield_health -= damage
                        if enemy.shield_health <= 0:
                            enemy.shield_health = 0
                            self.particle_system.add_explosion(
                                enemy.x + enemy.size//2,
                                enemy.y + enemy.size//2,
                                COLORS['matrix_cyan']
                            )
                    else:
                        enemy.health -= damage
                    
                    # Vuruş istatistiği
                    self.player.stats['shots_hit'] += 1
                    
                    # Kombo
                    self.player.add_combo()
                    
                    # Patlama efekti
                    self.particle_system.add_explosion(
                        bullet['x'], bullet['y'], bullet['color']
                    )
                    
                    # Düşman öldü mü?
                    if enemy.health <= 0:
                        # Skor ekle
                        score_added = self.player.add_score(enemy.value)
                        
                        # İstatistik
                        self.player.stats['enemies_killed'] += 1
                        
                        # Büyük patlama
                        self.particle_system.add_explosion(
                            enemy.x + enemy.size//2,
                            enemy.y + enemy.size//2,
                            enemy.color,
                            30
                        )
                        
                        # Matrix yağmuru efekti
                        self.particle_system.add_matrix_rain(
                            enemy.x + enemy.size//2,
                            enemy.y + enemy.size//2
                        )
                        
                        # Powerup düşürme şansı
                        if random.random() < 0.25:
                            self.powerups.append(PowerUp(
                                enemy.x + enemy.size//2,
                                enemy.y + enemy.size//2
                            ))
                        
                        # Virüs split özelliği
                        if enemy.type == EnemyType.VIRUS and enemy.level > 1:
                            for _ in range(2):
                                virus = Enemy(EnemyType.VIRUS, enemy.level - 1)
                                virus.x = enemy.x + random.randint(-20, 20)
                                virus.y = enemy.y + enemy.size
                                virus.health = virus.max_health // 2
                                self.enemies.append(virus)
                        
                        self.enemies.remove(enemy)
                    
                    # Mermi delme
                    if bullet['pierce'] > 0:
                        bullet['pierced_enemies'] += 1
                        if bullet['pierced_enemies'] > bullet['pierce']:
                            bullet_hit = True
                    else:
                        bullet_hit = True
                    
                    if bullet_hit:
                        self.player.bullets.remove(bullet)
                        break
            
            # Boss ile çarpışma
            if self.boss and not bullet_hit and not self.boss.invulnerable:
                if (bullet['x'] > self.boss.x and
                    bullet['x'] < self.boss.x + self.boss.size and
                    bullet['y'] > self.boss.y and
                    bullet['y'] < self.boss.y + self.boss.size):
                    
                    # Hasar hesapla
                    damage = bullet['damage']
                    if random.random() < self.player.critical_chance:
                        damage *= 2
                    
                    self.boss.health -= damage
                    self.player.stats['shots_hit'] += 1
                    
                    # Patlama efekti
                    self.particle_system.add_explosion(
                        bullet['x'], bullet['y'], bullet['color']
                    )
                    
                    # Kombo
                    self.player.add_combo()
                    
                    if bullet['pierce'] > 0:
                        bullet['pierced_enemies'] += 1
                        if bullet['pierced_enemies'] > bullet['pierce']:
                            self.player.bullets.remove(bullet)
                    else:
                        self.player.bullets.remove(bullet)
        
        # Düşman mermileri ile oyuncu
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if (bullet['x'] > self.player.x and
                    bullet['x'] < self.player.x + self.player.width and
                    bullet['y'] > self.player.y and
                    bullet['y'] < self.player.y + self.player.height):
                    
                    if self.player.take_damage(enemy.level * 3):
                        self.end_game()
                        return
                    
                    # Patlama efekti
                    self.particle_system.add_explosion(
                        bullet['x'], bullet['y'], bullet['color']
                    )
                    enemy.bullets.remove(bullet)
        
        # Düşmanlar ile oyuncu çarpışması
        for enemy in self.enemies:
            if (self.player.x < enemy.x + enemy.size and
                self.player.x + self.player.width > enemy.x and
                self.player.y < enemy.y + enemy.size and
                self.player.y + self.player.height > enemy.y):
                
                if self.player.take_damage(enemy.level * 5):
                    self.end_game()
                    return
                
                # Düşmana da hasar ver
                enemy.health -= 10
                if enemy.health <= 0:
                    self.player.add_score(enemy.value)
                    self.player.stats['enemies_killed'] += 1
                    self.enemies.remove(enemy)
        
        # Powerup toplama
        for powerup in self.powerups[:]:
            distance = math.sqrt(
                (powerup.x - (self.player.x + self.player.width//2))**2 +
                (powerup.y - (self.player.y + self.player.height//2))**2
            )
            
            if distance < self.player.width//2 + powerup.size:
                self.collect_powerup(powerup)
                self.powerups.remove(powerup)
    
    def collect_powerup(self, powerup):
        if powerup.apply(self.player):
            self.player.stats['powerups_collected'] += 1
            self.player.add_score(100)
            
            # Özel efektler
            if powerup.type == PowerUpType.TIME_SLOW:
                self.time_manipulation.activate_slow_motion(300, 0.3)
            elif powerup.type == PowerUpType.NANO_BOTS:
                # Nano botlar - otomatik tamir
                self.player.health = min(self.player.max_health, self.player.health + 1)
            
            # Parlama efekti
            self.particle_system.add_explosion(
                powerup.x, powerup.y, powerup.color, 15
            )
    
    def end_game(self):
        self.state = GameState.GAME_OVER
        
        # İstatistikleri kaydet
        self.player.stats['play_time'] = self.game_time // 60  # Saniye cinsinden
        self.statistics.update(self.player.stats)
        self.statistics.stats['games_played'] += 1
        
        # Yüksek skor kontrolü
        if len(self.high_scores) < 10 or self.player.score > self.high_scores[-1]['score']:
            # Oyun sonunda isim girişi yapılacak
            pass
        
        # Cutscene başlat
        self.cutscene_manager.play_cutscene("game_over")
        
        # İstatistikleri kaydet
        self.statistics.save_stats()
    
    def draw(self, surface):
        # Ekran titremesi için offset
        shake_x = random.randint(-int(self.screen_shake), int(self.screen_shake))
        shake_y = random.randint(-int(self.screen_shake), int(self.screen_shake))
        
        # Geçici yüzey oluştur
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        
        # Arkaplan
        temp_surface.fill(COLORS['black'])
        
        # Matrix yağmuru
        self.matrix_rain.draw(temp_surface)
        
        # Hava durumu
        self.weather_system.draw(temp_surface)
        
        # Zaman manipülasyonu efektleri
        self.time_manipulation.draw(temp_surface)
        
        # Parçacık sistemi
        self.particle_system.draw(temp_surface)
        
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu(temp_surface)
        elif self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            # Düşmanları çiz
            for enemy in self.enemies:
                enemy.draw(temp_surface)
            
            # Powerup'ları çiz
            for powerup in self.powerups:
                powerup.draw(temp_surface)
            
            # Boss çiz
            if self.boss:
                self.boss.draw(temp_surface)
            
            # Oyuncuyu çiz
            self.player.draw(temp_surface)
            
            # HUD çiz
            self.draw_hud(temp_surface)
            
            # Görevler
            self.mission_system.draw(temp_surface)
            
            # AI Assistant
            self.ai_assistant.draw(temp_surface)
            
            # Cutscene
            if self.cutscene_manager.active_cutscene:
                self.cutscene_manager.draw(temp_surface)
            
            # Oyun durumuna özel ekranlar
            if self.state == GameState.PAUSED:
                self.draw_pause_menu(temp_surface)
            elif self.state == GameState.GAME_OVER:
                if not self.cutscene_manager.active_cutscene:
                    self.draw_game_over(temp_surface)
        
        elif self.state == GameState.UPGRADE_SHOP:
            self.draw_upgrade_shop(temp_surface)
        
        # Ekran titremesi uygula
        surface.blit(temp_surface, (shake_x, shake_y))
    
    def draw_main_menu(self, surface):
        # Başlık
        title1 = large_font.render("THE MATRIX", True, COLORS['matrix_green'])
        title2 = medium_font.render("DIGITAL REVOLUTION", True, COLORS['matrix_cyan'])
        
        surface.blit(title1, (WIDTH//2 - title1.get_width()//2, 100))
        surface.blit(title2, (WIDTH//2 - title2.get_width()//2, 180))
        
        # Menü seçenekleri
        menu_options = [
            ("START GAME", GameState.PLAYING),
            ("UPGRADE SHOP", GameState.UPGRADE_SHOP),
            ("STATISTICS", "stats"),
            ("HIGH SCORES", "highscores"),
            ("SETTINGS", "settings"),
            ("QUIT", "quit")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (text, action) in enumerate(menu_options):
            y_pos = 300 + i * 70
            color = COLORS['matrix_white']
            
            # Mouse hover efekti
            text_width = medium_font.size(text)[0]
            option_rect = pygame.Rect(
                WIDTH//2 - text_width//2 - 20,
                y_pos - 10,
                text_width + 40,
                50
            )
            
            if option_rect.collidepoint(mouse_pos):
                color = COLORS['matrix_cyan']
                pygame.draw.rect(surface, (0, 100, 0, 100), option_rect)
                pygame.draw.rect(surface, COLORS['matrix_cyan'], option_rect, 2)
            
            text_surf = medium_font.render(text, True, color)
            surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_pos))
        
        # Kontroller
        controls = [
            "CONTROLS: WASD/Arrows = Move, SPACE = Shoot, P = Pause",
            "ESC = Menu, F = Fullscreen, R = Restart (Game Over)"
        ]
        
        for i, text in enumerate(controls):
            text_surf = small_font.render(text, True, COLORS['matrix_light_green'])
            surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT - 100 + i * 20))
        
        # Sürüm bilgisi
        version = small_font.render("v2.0 - Ultimate Edition", True, COLORS['matrix_gray'])
        surface.blit(version, (WIDTH - version.get_width() - 20, HEIGHT - 30))
    
    def draw_hud(self, surface):
        # Sağlık çubuğu
        health_width = 300
        health_height = 25
        health_x = 20
        health_y = 20
        
        pygame.draw.rect(surface, COLORS['matrix_dark'],
                        (health_x, health_y, health_width, health_height))
        
        health_percent = self.player.health / self.player.max_health
        fill_width = max(0, int(health_width * health_percent))
        
        health_color = COLORS['matrix_green']
        if health_percent < 0.3:
            health_color = COLORS['matrix_red']
        elif health_percent < 0.6:
            health_color = COLORS['matrix_yellow']
        
        pygame.draw.rect(surface, health_color,
                        (health_x, health_y, fill_width, health_height))
        
        # Sağlık metni
        health_text = font.render(f"SYSTEM: {int(self.player.health)}/{self.player.max_health}", True,
                                COLORS['matrix_white'])
        surface.blit(health_text, (health_x + 5, health_y))
        
        # Kalkan çubuğu
        if self.player.shield > 0:
            shield_width = 200
            shield_height = 15
            shield_x = 20
            shield_y = 50
            
            pygame.draw.rect(surface, COLORS['matrix_dark'],
                           (shield_x, shield_y, shield_width, shield_height))
            
            shield_percent = self.player.shield / self.player.max_shield
            fill_width = max(0, int(shield_width * shield_percent))
            
            pygame.draw.rect(surface, COLORS['matrix_cyan'],
                           (shield_x, shield_y, fill_width, shield_height))
        
        # Skor
        score_text = font.render(f"SCORE: {self.player.score:,}", True,
                               COLORS['matrix_cyan'])
        surface.blit(score_text, (WIDTH - score_text.get_width() - 20, 20))
        
        # Dalga
        wave_text = font.render(f"WAVE: {self.wave}", True,
                              COLORS['matrix_light_green'])
        surface.blit(wave_text, (WIDTH - wave_text.get_width() - 20, 50))
        
        # Kombo
        if self.player.combo > 1:
            combo_text = font.render(f"COMBO: {self.player.combo}x", True,
                                   COLORS['matrix_yellow'])
            surface.blit(combo_text, (WIDTH - combo_text.get_width() - 20, 80))
            
            # Kombo süresi
            combo_width = 100
            combo_height = 5
            combo_time = self.player.combo_timer / 180  # 0-1 arası
            
            pygame.draw.rect(surface, COLORS['matrix_dark'],
                           (WIDTH - combo_width - 20, 110, combo_width, combo_height))
            pygame.draw.rect(surface, COLORS['matrix_yellow'],
                           (WIDTH - combo_width - 20, 110, combo_width * combo_time, combo_height))
        
        # Powerup göstergeleri
        powerup_y = 100
        for powerup, timer in self.player.powerups.items():
            if timer > 0:
                colors = {
                    'rapid_fire': COLORS['matrix_yellow'],
                    'shield': COLORS['matrix_cyan'],
                    'double_points': COLORS['matrix_purple'],
                    'time_slow': COLORS['matrix_blue'],
                    'matrix_vision': COLORS['matrix_white'],
                    'nano_bots': COLORS['matrix_orange'],
                    'quantum': COLORS['matrix_pink']
                }
                
                if powerup in colors:
                    powerup_text = font.render(
                        f"{powerup.upper()}: {int(timer//60)}.{int(timer%60):02d}", 
                        True, colors[powerup])
                    surface.blit(powerup_text, (20, powerup_y))
                    powerup_y += 25
        
        # FPS
        fps_text = small_font.render(f"FPS: {int(clock.get_fps())}", True,
                                   COLORS['matrix_gray'])
        surface.blit(fps_text, (WIDTH - fps_text.get_width() - 20, HEIGHT - 30))
        
        # Zaman
        time_text = small_font.render(f"TIME: {int(self.game_time//60)}:{int(self.game_time%60):02d}", 
                                    True, COLORS['matrix_gray'])
        surface.blit(time_text, (20, HEIGHT - 30))
        
        # Hava durumu
        if self.weather_system.current_weather != WeatherType.CLEAR:
            weather_text = small_font.render(
                f"WEATHER: {self.weather_system.current_weather.value.upper()}", 
                True, COLORS['matrix_cyan'])
            surface.blit(weather_text, (WIDTH//2 - weather_text.get_width()//2, 20))
    
    def draw_pause_menu(self, surface):
        # Karanlık arkaplan
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        # Ana kutu
        pause_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
        pygame.draw.rect(surface, (0, 30, 0, 220), pause_rect)
        pygame.draw.rect(surface, COLORS['matrix_green'], pause_rect, 4)
        
        # Başlık
        title = large_font.render("SYSTEM PAUSED", True, COLORS['matrix_cyan'])
        surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        
        # Seçenekler
        options = ["RESUME", "UPGRADE SHOP", "STATISTICS", "MAIN MENU", "QUIT"]
        mouse_pos = pygame.mouse.get_pos()
        
        for i, option in enumerate(options):
            y_pos = HEIGHT//2 - 50 + i * 50
            color = COLORS['matrix_white']
            
            # Mouse hover
            text_width = medium_font.size(option)[0]
            option_rect = pygame.Rect(
                WIDTH//2 - text_width//2 - 15,
                y_pos - 10,
                text_width + 30,
                40
            )
            
            if option_rect.collidepoint(mouse_pos):
                color = COLORS['matrix_cyan']
                pygame.draw.rect(surface, (0, 100, 0, 100), option_rect)
                pygame.draw.rect(surface, COLORS['matrix_cyan'], option_rect, 2)
            
            text_surf = medium_font.render(option, True, color)
            surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_pos))
    
    def draw_game_over(self, surface):
        # Karanlık arkaplan
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Ana kutu
        game_over_rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400)
        pygame.draw.rect(surface, (0, 30, 0, 220), game_over_rect)
        pygame.draw.rect(surface, COLORS['matrix_red'], game_over_rect, 4)
        
        # Başlık
        title = large_font.render("SYSTEM FAILURE", True, COLORS['matrix_red'])
        surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 180))
        
        # İstatistikler
        stats = [
            f"FINAL SCORE: {self.player.score:,}",
            f"WAVE REACHED: {self.wave}",
            f"ENEMIES KILLED: {self.player.stats['enemies_killed']}",
            f"POWERUPS COLLECTED: {self.player.stats['powerups_collected']}",
            f"HIGHEST COMBO: {self.player.stats['highest_combo']}x",
            f"PLAY TIME: {int(self.game_time//60)}:{int(self.game_time%60):02d}",
            f"ACCURACY: {self.player.stats['shots_hit']/max(1, self.player.stats['shots_fired'])*100:.1f}%"
        ]
        
        y_offset = HEIGHT//2 - 120
        for stat in stats:
            text_surf = font.render(stat, True, COLORS['matrix_white'])
            surface.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, y_offset))
            y_offset += 35
        
        # Yeni yüksek skor
        if len(self.high_scores) < 10 or self.player.score > self.high_scores[-1]['score']:
            high_score_text = medium_font.render("NEW HIGH SCORE!", True, COLORS['matrix_yellow'])
            surface.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, y_offset + 20))
            y_offset += 40
        
        # Seçenekler
        options = ["RESTART", "MAIN MENU", "VIEW STATS", "QUIT"]
        mouse_pos = pygame.mouse.get_pos()
        
        y_offset = HEIGHT//2 + 120
        for i, option in enumerate(options):
            x_pos = WIDTH//2 - 150 + i * 100
            color = COLORS['matrix_white']
            
            # Mouse hover
            text_width = font.size(option)[0]
            option_rect = pygame.Rect(
                x_pos - text_width//2 - 10,
                y_offset - 5,
                text_width + 20,
                30
            )
            
            if option_rect.collidepoint(mouse_pos):
                color = COLORS['matrix_cyan']
                pygame.draw.rect(surface, (0, 100, 0, 100), option_rect)
                pygame.draw.rect(surface, COLORS['matrix_cyan'], option_rect, 2)
            
            text_surf = font.render(option, True, color)
            surface.blit(text_surf, (x_pos - text_surf.get_width()//2, y_offset))
    
    def draw_upgrade_shop(self, surface):
        self.upgrade_system.draw_shop(surface, self.player)
    
    def handle_click(self, pos):
        if self.state == GameState.MAIN_MENU:
            self.handle_main_menu_click(pos)
        elif self.state == GameState.PAUSED:
            self.handle_pause_menu_click(pos)
        elif self.state == GameState.GAME_OVER:
            self.handle_game_over_click(pos)
        elif self.state == GameState.UPGRADE_SHOP:
            self.handle_upgrade_shop_click(pos)
    
    def handle_main_menu_click(self, pos):
        menu_options = [
            ("START GAME", GameState.PLAYING, None),
            ("UPGRADE SHOP", GameState.UPGRADE_SHOP, None),
            ("STATISTICS", "stats", None),
            ("HIGH SCORES", "highscores", None),
            ("SETTINGS", "settings", None),
            ("QUIT", "quit", None)
        ]
        
        for i, (text, action, _) in enumerate(menu_options):
            y_pos = 300 + i * 70
            text_width = medium_font.size(text)[0]
            option_rect = pygame.Rect(
                WIDTH//2 - text_width//2 - 20,
                y_pos - 10,
                text_width + 40,
                50
            )
            
            if option_rect.collidepoint(pos):
                if action == GameState.PLAYING:
                    self.start_game()
                elif action == GameState.UPGRADE_SHOP:
                    self.state = GameState.UPGRADE_SHOP
                elif action == "stats":
                    # İstatistikler ekranı
                    pass
                elif action == "quit":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                break
    
    def handle_pause_menu_click(self, pos):
        options = ["RESUME", "UPGRADE SHOP", "STATISTICS", "MAIN MENU", "QUIT"]
        
        for i, option in enumerate(options):
            y_pos = HEIGHT//2 - 50 + i * 50
            text_width = medium_font.size(option)[0]
            option_rect = pygame.Rect(
                WIDTH//2 - text_width//2 - 15,
                y_pos - 10,
                text_width + 30,
                40
            )
            
            if option_rect.collidepoint(pos):
                if option == "RESUME":
                    self.state = GameState.PLAYING
                elif option == "UPGRADE SHOP":
                    self.state = GameState.UPGRADE_SHOP
                elif option == "MAIN MENU":
                    self.state = GameState.MAIN_MENU
                elif option == "QUIT":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                break
    
    def handle_game_over_click(self, pos):
        options = ["RESTART", "MAIN MENU", "VIEW STATS", "QUIT"]
        
        for i, option in enumerate(options):
            y_pos = HEIGHT//2 + 120
            x_pos = WIDTH//2 - 150 + i * 100
            text_width = font.size(option)[0]
            option_rect = pygame.Rect(
                x_pos - text_width//2 - 10,
                y_pos - 5,
                text_width + 20,
                30
            )
            
            if option_rect.collidepoint(pos):
                if option == "RESTART":
                    self.start_game()
                elif option == "MAIN MENU":
                    self.state = GameState.MAIN_MENU
                elif option == "QUIT":
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                break
    
    def handle_upgrade_shop_click(self, pos):
        # Çıkış butonu
        exit_rect = pygame.Rect(WIDTH//2 - 50, 780, 100, 40)
        if exit_rect.collidepoint(pos):
            self.state = GameState.MAIN_MENU
            return
        
        # Upgrade butonları
        y_offset = 200
        for i, (name, upgrade) in enumerate(self.upgrade_system.upgrades.items()):
            button_rect = pygame.Rect(WIDTH//2 + 180, y_offset, 80, 30)
            if button_rect.collidepoint(pos) and self.upgrade_system.can_upgrade(name):
                self.upgrade_system.apply_upgrade(self.player, name)
            
            y_offset += 60

if __name__ == "__main__":
    gm = GameManager()
    running = True

    while running:
        # input
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT),
                                                pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                gm.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    gm.state = GameState.PAUSED if gm.state == GameState.PLAYING else GameState.PLAYING
                elif event.key == pygame.K_r and gm.state == GameState.GAME_OVER:
                    gm.start_game()
                elif gm.cutscene_manager.active_cutscene:
                    # herhangi bir tuşa basınca cutscene atla/ileri
                    gm.cutscene_manager.active_cutscene = None

        # update & render
        gm.update(keys)
        gm.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()