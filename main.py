#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚔️ COMBAT DE MOTS - Jeu Terminal Épique ⚔️
Un jeu où les joueurs s'affrontent avec des mots !
Différents modes de combat : longueur, lettres rares, voyelles, etc.
"""

import random
import time
import os
import sys
import string
import json
from collections import Counter

class Colors:
    """Couleurs ANSI pour le terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    END = '\033[0m'

class WordCombat:
    def __init__(self):
        self.player_names = ["", ""]
        self.player_hp = [100, 100]  # Points de vie
        self.player_scores = [0, 0]  # Score total
        self.round_number = 1
        self.combat_modes = [
            "longueur", "voyelles", "consonnes", "lettres_rares", 
            "palindrome", "alliteration", "score_scrabble"
        ]
        self.used_words = set()  # Mots déjà utilisés
        
        # Valeurs Scrabble des lettres
        self.scrabble_values = {
            'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4,
            'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3,
            'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
            'y': 4, 'z': 10
        }
        
        # Lettres rares (valeur élevée au Scrabble)
        self.rare_letters = set('jkqxwzvyf')
        
    def clear_screen(self):
        """Efface l'écran du terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def type_text(self, text, delay=0.03):
        """Affiche le texte avec un effet de machine à écrire"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def display_banner(self):
        """Affiche le banner du jeu"""
        banner = f"""
{Colors.RED}{Colors.BOLD}
╔═══════════════════════════════════════════════╗
║           ⚔️  COMBAT DE MOTS  ⚔️             ║
║         Que le meilleur mot gagne !           ║
╚═══════════════════════════════════════════════╝
{Colors.END}"""
        print(banner)
    
    def display_hp_bar(self, player_num):
        """Affiche la barre de vie du joueur"""
        hp = self.player_hp[player_num]
        name = self.player_names[player_num]
        
        # Couleur selon les HP
        if hp > 70:
            color = Colors.GREEN
        elif hp > 30:
            color = Colors.YELLOW
        else:
            color = Colors.RED
        
        # Barre de vie (20 caractères max)
        bar_length = 20
        filled_length = int(bar_length * hp / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        return f"{color}{name}: {bar} {hp}/100 HP{Colors.END}"
    
    def display_status(self):
        """Affiche le statut actuel du combat"""
        print(f"\n{Colors.CYAN}🏟️  ROUND {self.round_number} 🏟️{Colors.END}")
        print(f"{self.display_hp_bar(0)}")
        print(f"{self.display_hp_bar(1)}")
        print(f"\n{Colors.WHITE}Score: {self.player_names[0]} {self.player_scores[0]} - {self.player_scores[1]} {self.player_names[1]}{Colors.END}")
    
    def get_word_stats(self, word):
        """Calcule les statistiques d'un mot"""
        word = word.lower()
        
        stats = {
            'longueur': len(word),
            'voyelles': sum(1 for c in word if c in 'aeiouy'),
            'consonnes': sum(1 for c in word if c.isalpha() and c not in 'aeiouy'),
            'lettres_rares': sum(1 for c in word if c in self.rare_letters),
            'palindrome': 1 if word == word[::-1] else 0,
            'score_scrabble': sum(self.scrabble_values.get(c, 0) for c in word)
        }
        
        # Allitération : répétition de la première lettre
        if len(word) > 1:
            first_letter = word[0]
            stats['alliteration'] = sum(1 for c in word if c == first_letter)
        else:
            stats['alliteration'] = 1
            
        return stats
    
    def is_valid_word(self, word):
        """Vérifie si le mot est valide"""
        # Vérifie que c'est bien un mot (lettres seulement)
        if not word.isalpha():
            return False, "Le mot doit contenir uniquement des lettres !"
        
        # Vérifie la longueur minimale
        if len(word) < 2:
            return False, "Le mot doit faire au moins 2 lettres !"
        
        # Vérifie si le mot n'a pas déjà été utilisé
        if word.lower() in self.used_words:
            return False, "Ce mot a déjà été utilisé !"
        
        return True, ""
    
    def get_combat_mode(self):
        """Choisit un mode de combat aléatoire"""
        mode = random.choice(self.combat_modes)
        
        mode_descriptions = {
            "longueur": "⚡ Le mot le plus LONG gagne !",
            "voyelles": "🎵 Le mot avec le plus de VOYELLES gagne !",
            "consonnes": "💪 Le mot avec le plus de CONSONNES gagne !",
            "lettres_rares": "💎 Le mot avec le plus de LETTRES RARES gagne !",
            "palindrome": "🪞 Si c'est un PALINDROME, bonus énorme !",
            "alliteration": "🔄 Le mot avec le plus d'ALLITÉRATION gagne !",
            "score_scrabble": "🎯 Le mot avec le meilleur SCORE SCRABBLE gagne !"
        }
        
        return mode, mode_descriptions[mode]
    
    def calculate_damage(self, word, mode, stats):
        """Calcule les dégâts infligés par un mot"""
        base_damage = 10
        
        if mode == "longueur":
            damage = base_damage + (stats['longueur'] * 3)
        elif mode == "voyelles":
            damage = base_damage + (stats['voyelles'] * 5)
        elif mode == "consonnes":
            damage = base_damage + (stats['consonnes'] * 4)
        elif mode == "lettres_rares":
            damage = base_damage + (stats['lettres_rares'] * 8)
        elif mode == "palindrome":
            damage = base_damage + (stats['palindrome'] * 30)  # Bonus énorme !
        elif mode == "alliteration":
            damage = base_damage + (stats['alliteration'] * 6)
        elif mode == "score_scrabble":
            damage = base_damage + (stats['score_scrabble'] * 2)
        
        # Bonus pour les longs mots
        if stats['longueur'] >= 8:
            damage += 10
        
        return min(damage, 50)  # Limite à 50 dégâts max
    
    def display_word_analysis(self, word, stats, damage, mode):
        """Affiche l'analyse détaillée du mot"""
        print(f"\n{Colors.CYAN}📊 ANALYSE DU MOT: '{word.upper()}'{Colors.END}")
        print(f"{Colors.WHITE}Longueur: {stats['longueur']} lettres{Colors.END}")
        print(f"{Colors.WHITE}Voyelles: {stats['voyelles']} | Consonnes: {stats['consonnes']}{Colors.END}")
        print(f"{Colors.WHITE}Lettres rares: {stats['lettres_rares']}{Colors.END}")
        print(f"{Colors.WHITE}Score Scrabble: {stats['score_scrabble']} points{Colors.END}")
        
        if stats['palindrome']:
            print(f"{Colors.MAGENTA}🪞 PALINDROME DÉTECTÉ ! +30 dégâts !{Colors.END}")
        
        print(f"{Colors.YELLOW}⚔️ DÉGÂTS INFLIGÉS: {damage}{Colors.END}")
    
    def animate_attack(self, attacker_name, word, damage):
        """Animation d'attaque"""
        attacks = [
            f"🗡️ {attacker_name} brandit '{word.upper()}' !",
            f"⚡ {attacker_name} lance '{word.upper()}' avec fureur !",
            f"🔥 {attacker_name} déchaîne la puissance de '{word.upper()}' !",
            f"💫 {attacker_name} invoque '{word.upper()}' !",
            f"⚔️ {attacker_name} attaque avec '{word.upper()}' !"
        ]
        
        attack_msg = random.choice(attacks)
        
        print(f"\n{Colors.RED}{Colors.BOLD}{attack_msg}{Colors.END}")
        
        # Animation des dégâts
        for i in range(3):
            print(f"{Colors.YELLOW}💥{'!' * (i + 1)}{Colors.END}", end='\r', flush=True)
            time.sleep(0.4)
        
        print(f"\n{Colors.RED}{Colors.BOLD}💥 {damage} DÉGÂTS ! 💥{Colors.END}")
        time.sleep(1)
    
    def get_player_word(self, player_num, mode, mode_desc):
        """Récupère le mot du joueur"""
        player_name = self.player_names[player_num]
        
        print(f"\n{Colors.GREEN}🎯 {player_name}, à toi d'attaquer !{Colors.END}")
        print(f"{Colors.CYAN}{mode_desc}{Colors.END}")
        
        while True:
            try:
                word = input(f"\n{Colors.WHITE}Entre ton mot d'attaque: {Colors.END}").strip()
                
                if not word:
                    print(f"{Colors.RED}❌ Tu dois entrer un mot !{Colors.END}")
                    continue
                
                is_valid, error_msg = self.is_valid_word(word)
                if not is_valid:
                    print(f"{Colors.RED}❌ {error_msg}{Colors.END}")
                    continue
                
                return word.lower()
                
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}👋 Combat interrompu !{Colors.END}")
                sys.exit(0)
    
    def play_round(self):
        """Joue un round de combat"""
        self.clear_screen()
        self.display_banner()
        self.display_status()
        
        # Choix du mode de combat
        mode, mode_desc = self.get_combat_mode()
        
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}⚔️ MODE DE COMBAT: {mode.upper()} ⚔️{Colors.END}")
        print(f"{Colors.CYAN}{mode_desc}{Colors.END}")
        
        input(f"\n{Colors.WHITE}Appuyez sur Entrée pour commencer le round...{Colors.END}")
        
        # Tour de chaque joueur
        round_results = []
        
        for player_num in range(2):
            if self.player_hp[player_num] <= 0:
                continue
                
            word = self.get_player_word(player_num, mode, mode_desc)
            stats = self.get_word_stats(word)
            damage = self.calculate_damage(word, mode, stats)
            
            self.used_words.add(word)
            
            round_results.append({
                'player': player_num,
                'word': word,
                'stats': stats,
                'damage': damage
            })
        
        # Affichage des résultats et calcul des dégâts
        print(f"\n{Colors.YELLOW}{Colors.BOLD}📊 RÉSULTATS DU ROUND {self.round_number} 📊{Colors.END}")
        
        for result in round_results:
            player_name = self.player_names[result['player']]
            self.display_word_analysis(result['word'], result['stats'], result['damage'], mode)
            time.sleep(2)
        
        # Déterminer le gagnant du round
        if len(round_results) == 2:
            if round_results[0]['damage'] > round_results[1]['damage']:
                winner_idx = 0
                loser_idx = 1
            elif round_results[1]['damage'] > round_results[0]['damage']:
                winner_idx = 1
                loser_idx = 0
            else:
                # Égalité - les deux prennent des dégâts
                print(f"\n{Colors.YELLOW}⚖️ ÉGALITÉ ! Les deux guerriers se blessent !{Colors.END}")
                for result in round_results:
                    opponent = 1 - result['player']
                    self.player_hp[opponent] -= result['damage'] // 2
                    self.animate_attack(self.player_names[result['player']], result['word'], result['damage'] // 2)
                return
            
            # Le gagnant inflige des dégâts
            winner_name = self.player_names[winner_idx]
            winner_word = round_results[winner_idx]['word']
            damage_dealt = round_results[winner_idx]['damage']
            
            print(f"\n{Colors.GREEN}{Colors.BOLD}🏆 {winner_name} remporte le round !{Colors.END}")
            self.animate_attack(winner_name, winner_word, damage_dealt)
            
            self.player_hp[loser_idx] -= damage_dealt
            self.player_hp[loser_idx] = max(0, self.player_hp[loser_idx])  # Pas en dessous de 0
            
            self.player_scores[winner_idx] += 1
    
    def check_game_over(self):
        """Vérifie si le jeu est terminé"""
        return self.player_hp[0] <= 0 or self.player_hp[1] <= 0
    
    def display_winner(self):
        """Affiche le gagnant final"""
        if self.player_hp[0] <= 0 and self.player_hp[1] <= 0:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}💀 DOUBLE K.O. ! 💀{Colors.END}")
            print(f"{Colors.CYAN}Les deux guerriers s'effondrent en même temps !{Colors.END}")
        elif self.player_hp[0] <= 0:
            winner = self.player_names[1]
            print(f"\n{Colors.GREEN}{Colors.BOLD}👑 VICTOIRE DE {winner.upper()} ! 👑{Colors.END}")
        else:
            winner = self.player_names[0]
            print(f"\n{Colors.GREEN}{Colors.BOLD}👑 VICTOIRE DE {winner.upper()} ! 👑{Colors.END}")
        
        # Animation de victoire
        victory_effects = ["🎉", "🏆", "⭐", "💫", "🌟"]
        for i in range(5):
            effect = random.choice(victory_effects)
            print(f"{Colors.GREEN}{effect * 10}{Colors.END}")
            time.sleep(0.3)
    
    def display_final_stats(self):
        """Affiche les statistiques finales"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}📈 STATISTIQUES FINALES 📈{Colors.END}")
        print(f"{Colors.WHITE}Rounds joués: {self.round_number - 1}{Colors.END}")
        print(f"{Colors.WHITE}Mots utilisés: {len(self.used_words)}{Colors.END}")
        print(f"{Colors.WHITE}Score final: {self.player_names[0]} {self.player_scores[0]} - {self.player_scores[1]} {self.player_names[1]}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}🏆 Meilleurs mots utilisés:{Colors.END}")
        # Affiche quelques mots utilisés
        sample_words = list(self.used_words)[:10]  # Les 10 premiers
        for word in sample_words:
            print(f"{Colors.WHITE}• {word.upper()}{Colors.END}")
    
    def setup_game(self):
        """Configuration initiale du jeu"""
        self.clear_screen()
        self.display_banner()
        
        print(f"{Colors.WHITE}Bienvenue au Combat de Mots !{Colors.END}")
        print(f"{Colors.YELLOW}⚔️ Deux guerriers s'affrontent avec des mots !")
        print(f"Chaque round a un mode de combat différent.")
        print(f"Le premier à tomber à 0 HP perd !{Colors.END}\n")
        
        # Saisie des noms des joueurs
        self.player_names[0] = input(f"{Colors.GREEN}Nom du Guerrier 1: {Colors.END}") or "Guerrier 1"
        self.player_names[1] = input(f"{Colors.GREEN}Nom du Guerrier 2: {Colors.END}") or "Guerrier 2"
        
        print(f"\n{Colors.CYAN}⚔️ {self.player_names[0]} VS {self.player_names[1]} ⚔️{Colors.END}")
        print(f"{Colors.WHITE}Que le combat commence !{Colors.END}")
        
        input(f"\n{Colors.YELLOW}Appuyez sur Entrée pour commencer...{Colors.END}")
    
    def run(self):
        """Lance le jeu principal"""
        try:
            self.setup_game()
            
            while not self.check_game_over():
                self.play_round()
                self.round_number += 1
                
                if not self.check_game_over():
                    input(f"\n{Colors.WHITE}Appuyez sur Entrée pour le prochain round...{Colors.END}")
            
            self.display_winner()
            self.display_final_stats()
            
            print(f"\n{Colors.CYAN}Merci d'avoir joué au Combat de Mots ! ⚔️{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Combat interrompu ! À bientôt !{Colors.END}")

def main():
    """Fonction principale"""
    game = WordCombat()
    game.run()

if __name__ == "__main__":
    main()