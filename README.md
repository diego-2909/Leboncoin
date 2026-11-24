# Bot Leboncoin → Telegram (PS5)

Vérifie Leboncoin toutes les 25 à 45 secondes et t'envoie une notification Telegram
(photo, prix, ville, lien) dès qu'une nouvelle annonce correspond à ta recherche.

Réglages actuels (dans `config.toml`) :
- mots-clés **ps5**, catégorie **Consoles**
- prix **≤ 450 €**
- **50 km autour de Toulouse**
- annonces contenant **« recherche »** ignorées
- seulement les offres (pas les « demandes »)

---

## Installation sur Mac (environ 10 minutes, une seule fois)

### 1. Installer Python

1. Va sur <https://www.python.org/downloads/macos/> et télécharge la dernière version de **Python 3** (3.11 minimum).
2. Ouvre le fichier `.pkg` et suis l'installation.
3. Ouvre l'app **Terminal** (Cmd + Espace, tape « Terminal »).
4. Va dans le dossier du bot. Tape `cd ` (avec un espace), fais glisser le dossier du bot dans la fenêtre, puis appuie sur Entrée.
5. Installe la dépendance :
   ```bash
   python3 -m pip install -r requirements.txt
   ```

### 2. Créer ton bot Telegram

1. Dans Telegram, cherche **@BotFather** (compte officiel avec le badge bleu).
2. Envoie-lui `/newbot`, puis choisis un nom (ex. « Alerte PS5 ») et un identifiant qui finit par `bot` (ex. `alerte_ps5_toulouse_bot`).
3. BotFather te donne un **token** qui ressemble à `123456789:AAH...`.
4. Ouvre `config.toml` (clic droit → Ouvrir avec → TextEdit) et colle le token à la place de `COLLE_TON_TOKEN_ICI`.

> Garde ce token secret : avec, n'importe qui peut envoyer des messages via ton bot.

### 3. Récupérer ton chat_id

Dans le Terminal :
```bash
python3 bot.py --chat-id
```
Suis les instructions : écris « salut » à ton bot dans Telegram, puis appuie sur Entrée.
Copie le numéro affiché dans `config.toml`, à la place de `COLLE_TON_CHAT_ID_ICI`.

### 4. Tester

```bash
python3 bot.py --test
```
Tu dois recevoir sur ton iPhone un message de test, puis un exemple d'annonce.
Le Terminal affiche aussi les annonces trouvées en ce moment, en indiquant pour chacune si elle passe les filtres.

### 5. Lancer le bot

- **Option simple :** double-clique sur `lancer.command`.
  La première fois, macOS peut le bloquer. Dans ce cas, fais clic droit → Ouvrir → Ouvrir.
  Si tu vois « permission refusée », tape une fois `chmod +x lancer.command` dans le Terminal.
- **Option Terminal :** `caffeinate -i python3 bot.py`

Le bot tourne tant que la fenêtre reste ouverte. `caffeinate` empêche le Mac de se mettre en veille.
**Le Mac doit rester allumé et connecté à internet.** Si c'est un MacBook, laisse-le branché sur le secteur, couvercle ouvert.

---

## Notifications instantanées sur iPhone

Dans Réglages → Notifications → Telegram : active **Notifications immédiates** (ou « Time Sensitive »)
et vérifie que la conversation avec ton bot n'est pas en sourdine.

## Changer les réglages

Tout se modifie dans `config.toml`. Après chaque modification, arrête puis relance le bot.

| Réglage | Rôle |
|---|---|
| `mots_cles` | ce que tu taperais dans la recherche Leboncoin |
| `prix_min` / `prix_max` | fourchette de prix |
| `rayon_km`, `ville`, `latitude`, `longitude` | zone de recherche |
| `mots_exclus` | ex. `["recherche", "manette", "boite vide", "hs"]` |
| `mots_obligatoires_titre` | ex. `["ps5", "playstation 5"]` pour éviter les jeux et accessoires |
| `attente_min` / `attente_max` | délai entre deux vérifications (ne descends pas sous ~20 s) |

## Si Leboncoin bloque le bot

Leboncoin a une protection anti-bot (DataDome). Si elle te bloque, le bot :
1. t'envoie un message Telegram « bloqué temporairement » ;
2. attend (1 min, puis 2, 4… jusqu'à 30 min maximum) et réessaie tout seul ;
3. t'envoie « fonctionne à nouveau » dès que ça repasse.

Si ça arrive souvent, augmente `attente_min` et `attente_max` (par exemple 40 et 70).

## Attention aux arnaques

Une PS5 très en dessous du prix du marché est souvent une arnaque. Méfie-toi si le vendeur
veut passer sur WhatsApp, demande un virement ou un paiement hors Leboncoin, ou envoie un faux lien « paiement sécurisé ».
Privilégie la remise en main propre ou le paiement sécurisé **dans** l'app Leboncoin.

## Version en ligne 24h/24 (gratuite, configurable depuis un iPhone)

Voir [GUIDE_ORACLE_IPHONE.md](GUIDE_ORACLE_IPHONE.md) et le fichier `oracle-cloud-init.yaml`.
