# Lancer le bot 24h/24 gratuitement sur Oracle Cloud, depuis un iPhone

Durée : environ 30 minutes. Aucune commande à taper.

**Ce qu'il te faut :** ton **token** Telegram (donné par @BotFather), ton **chat_id**, et une carte bancaire.
La carte sert seulement à vérifier ton identité : tu ne paies rien tant que tu restes sur les offres « Always Free ».

> Astuce : sur les pages Oracle, appuie sur **aA** dans la barre d'adresse de Safari puis sur
> **« Demander le site pour ordinateur »**. C'est beaucoup plus lisible.

---

## Étape 1 : préparer le script (dans l'app Notes)

1. Dans Safari ou l'app GitHub, ouvre le fichier **`oracle-cloud-init.yaml`** de ce dépôt.
2. Appuie sur **Raw** (ou « Afficher brut »), puis appui long → **Tout sélectionner** → **Copier**.
3. Colle le texte dans une nouvelle note.
4. Tout en haut de la note, remplace :
   - `COLLE_TON_TOKEN_ICI` par ton token (garde les guillemets) ;
   - `COLLE_TON_CHAT_ID_ICI` par ton chat_id (garde les guillemets).

   Le résultat doit ressembler à ça :
   ```
         token = "7123456789:AAH...ton token..."
         chat_id = "1594317636"
   ```
   ⚠️ Ne touche **pas** aux espaces au début des lignes : ils sont importants.
5. Sélectionne tout le texte de la note et **copie-le**.

> Notes peut remplacer les guillemets droits `"` par des guillemets courbes `“ ”`, ce qui casse le script.
> Avant de modifier, désactive Réglages → Général → Clavier → **Ponctuation intelligente**.
> Tu pourras la réactiver ensuite.

## Étape 2 : créer le compte Oracle

1. Va sur <https://signup.cloud.oracle.com>.
2. **Home Region** : choisis **France Central (Paris)** ou **France South (Marseille)**.
   ⚠️ Tu ne pourras plus la changer ensuite.
3. Termine l'inscription (e-mail, téléphone, carte). L'activation peut prendre quelques minutes.

## Étape 3 : créer le serveur

1. Dans la console Oracle : menu ☰ → **Compute** → **Instances** → **Create instance**.
2. **Name** : `bot-ps5`.
3. **Image and shape** → **Edit** :
   - **Change image** → **Canonical Ubuntu** (la dernière version, par ex. 24.04) → Select ;
   - **Change shape** → **Virtual machine** → **Specialty and previous generation** → **VM.Standard.E2.1.Micro**.
     Elle doit afficher le badge **« Always Free-eligible »**.
4. **Add SSH keys** : choisis **« No SSH keys »**. Tu n'en as pas besoin pour ce guide.
5. Descends jusqu'à **Show advanced options** → onglet **Management** →
   **Initialization script** → **Paste cloud-init script**, puis colle le texte copié à l'étape 1.
6. Appuie sur **Create**.

## Étape 4 : attendre

Après 5 à 10 minutes, tu reçois sur Telegram :
**« ✅ Bot démarré : ps5 ≤ 450 € à 50 km de Toulouse »**.

C'est fini. Le bot tourne en continu, même ton iPhone éteint, et redémarre tout seul en cas de problème.

Pour recevoir les alertes immédiatement : Réglages iPhone → Notifications → Telegram →
active **Notifications urgentes** (« Time Sensitive »).

---

## Ça ne marche pas ?

**Aucun message au bout de 15 minutes :**
- le token ou le chat_id est sans doute faux, ou des guillemets courbes `“ ”` se sont glissés dans le script ;
- dans ce cas, supprime l'instance (**More actions → Terminate**, coche « delete boot volume »), corrige la note et recommence l'étape 3.

**« Out of capacity » à la création :** réessaie un peu plus tard, ou choisis un autre « Availability domain ».

**Message « ⚠️ Leboncoin bloque temporairement le bot » :**
les adresses IP des serveurs cloud sont parfois bloquées par Leboncoin. Le bot réessaie tout seul.
Si ça arrive tout le temps, un Raspberry Pi ou un vieil Android chez toi marchera mieux.

## Modifier un réglage plus tard (prix, mots exclus…)

La méthode la plus simple depuis l'iPhone : supprime l'instance et recrée-la avec le script modifié.
Les réglages sont dans la partie `[recherche]`, en haut du script.

Avec une appli de terminal (Termius, ou Cloud Shell dans la console Oracle) :
```bash
sudo nano /opt/bot-ps5/config.toml        # modifier les réglages
sudo systemctl restart bot-ps5            # relancer le bot
sudo journalctl -u bot-ps5 -f             # voir ce que fait le bot en direct
```
