#!/bin/bash
# Double-clique sur ce fichier pour lancer le bot sur Mac.
# "caffeinate" empêche le Mac de se mettre en veille tant que le bot tourne.
cd "$(dirname "$0")"
echo "Bot Leboncoin lancé. Ferme cette fenêtre (ou Ctrl+C) pour l'arrêter."
caffeinate -i python3 bot.py
