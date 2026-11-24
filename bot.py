#!/usr/bin/env python3
"""
Bot Leboncoin -> Telegram
Surveille une recherche Leboncoin et envoie une notification Telegram
dès qu'une nouvelle annonce apparaît.

Utilisation :
    python3 bot.py              lance la surveillance
    python3 bot.py --chat-id    affiche ton chat_id Telegram (étape d'installation)
    python3 bot.py --test       envoie une notification de test + affiche les annonces actuelles
"""

import html
import json
import random
import sys
import time
import tomllib
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

try:
    import lbc
    from lbc.exceptions import DatadomeError
except ImportError:
    sys.exit("Module 'lbc' manquant. Lance d'abord :  python3 -m pip install -r requirements.txt")

DOSSIER = Path(__file__).resolve().parent
FICHIER_CONFIG = DOSSIER / "config.toml"
FICHIER_VUES = DOSSIER / "annonces_vues.json"

CATEGORIES = {
    "consoles": lbc.Category.ELECTRONIQUE_CONSOLES,
    "jeux_video": lbc.Category.ELECTRONIQUE_JEUX_VIDEO,
    "toutes": lbc.Category.TOUTES_CATEGORIES,
}


def log(msg: str) -> None:
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def normaliser(texte: str) -> str:
    """Minuscules + suppression des accents, pour comparer les mots."""
    texte = unicodedata.normalize("NFKD", texte or "")
    return "".join(c for c in texte if not unicodedata.combining(c)).lower()


def charger_config() -> dict:
    if not FICHIER_CONFIG.exists():
        sys.exit(f"Fichier de configuration introuvable : {FICHIER_CONFIG}")
    with open(FICHIER_CONFIG, "rb") as f:
        return tomllib.load(f)


# ---------------------------------------------------------------- Telegram

def telegram(cfg: dict, methode: str, **params) -> dict:
    token = cfg["telegram"]["token"]
    url = f"https://api.telegram.org/bot{token}/{methode}"
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(url, data=data, timeout=20) as r:
        return json.load(r)


def envoyer_message(cfg: dict, texte: str) -> None:
    try:
        telegram(cfg, "sendMessage", chat_id=cfg["telegram"]["chat_id"], text=texte,
                 parse_mode="HTML", disable_web_page_preview="false")
    except Exception as e:
        log(f"Erreur Telegram : {e}")


def notifier_annonce(cfg: dict, ad) -> None:
    prix = f"{ad.price:g} €" if ad.price else "prix non indiqué"
    lieu = ad.location.city_label if ad.location else ""
    texte = (
        f"🎮 <b>{html.escape(ad.subject)}</b>\n"
        f"💶 <b>{prix}</b>\n"
        f"📍 {html.escape(lieu)}\n"
        f"🕒 publiée le {ad.first_publication_date}\n\n"
        f'👉 <a href="{ad.url}">Voir l\'annonce</a>'
    )
    if ad.images:
        try:
            telegram(cfg, "sendPhoto", chat_id=cfg["telegram"]["chat_id"],
                     photo=ad.images[0], caption=texte, parse_mode="HTML")
            return
        except Exception:
            pass  # si la photo échoue, on envoie au moins le texte
    envoyer_message(cfg, texte)


def afficher_chat_id(cfg: dict) -> None:
    print("1) Ouvre Telegram et envoie un message quelconque (ex: 'salut') à TON bot.")
    input("2) Puis appuie sur Entrée ici... ")
    rep = telegram(cfg, "getUpdates")
    ids = {}
    for u in rep.get("result", []):
        chat = (u.get("message") or {}).get("chat")
        if chat:
            ids[chat["id"]] = chat.get("first_name") or chat.get("title") or ""
    if not ids:
        print("Aucun message reçu. Vérifie le token et que tu as bien écrit au bot, puis réessaie.")
        return
    for cid, nom in ids.items():
        print(f"   chat_id = {cid}   ({nom})")
    print("Copie ce numéro dans config.toml, ligne chat_id.")


# ---------------------------------------------------------------- Leboncoin

def rechercher(client: "lbc.Client", cfg: dict) -> list:
    r = cfg["recherche"]
    ville = lbc.City(lat=r["latitude"], lng=r["longitude"],
                     radius=int(r["rayon_km"]) * 1000, city=r["ville"])
    resultat = client.search(
        text=r["mots_cles"],
        category=CATEGORIES.get(r.get("categorie", "consoles"), lbc.Category.ELECTRONIQUE_CONSOLES),
        sort=lbc.Sort.NEWEST,
        locations=[ville],
        price=[int(r.get("prix_min", 0)), int(r["prix_max"])],
        ad_type=lbc.AdType.OFFER,
        limit=35,
    )
    return resultat.ads


def annonce_valide(ad, cfg: dict) -> bool:
    r = cfg["recherche"]
    titre = normaliser(ad.subject)
    tout = titre + " " + normaliser(ad.body)
    for mot in r.get("mots_exclus", []):
        if normaliser(mot) in tout:
            return False
    obligatoires = r.get("mots_obligatoires_titre", [])
    if obligatoires and not any(normaliser(m) in titre for m in obligatoires):
        return False
    if ad.price and ad.price > r["prix_max"]:
        return False
    return True


def charger_vues() -> set:
    try:
        return set(json.loads(FICHIER_VUES.read_text()))
    except Exception:
        return set()


def sauver_vues(vues: set) -> None:
    # on garde les 2000 dernières pour que le fichier ne grossisse pas indéfiniment
    FICHIER_VUES.write_text(json.dumps(sorted(vues)[-2000:]))


def nouveau_client() -> "lbc.Client":
    return lbc.Client(max_retries=2)


# ---------------------------------------------------------------- Boucle

def surveiller(cfg: dict) -> None:
    r, f = cfg["recherche"], cfg["frequence"]
    vues = charger_vues()
    premier_passage = not vues
    client = nouveau_client()
    pause_blocage = 60
    bloque_notifie = False

    log(f"Surveillance : '{r['mots_cles']}' ≤ {r['prix_max']} €, {r['rayon_km']} km autour de {r['ville']}")
    envoyer_message(cfg, f"✅ Bot démarré : <b>{html.escape(r['mots_cles'])}</b> ≤ {r['prix_max']} € "
                         f"à {r['rayon_km']} km de {html.escape(r['ville'])}")

    while True:
        try:
            annonces = rechercher(client, cfg)
            nouvelles = [a for a in annonces if a.id not in vues]

            if premier_passage:
                log(f"Premier passage : {len(annonces)} annonces existantes mémorisées (pas de notif).")
                premier_passage = False
            else:
                # de la plus ancienne à la plus récente
                for ad in reversed(nouvelles):
                    if annonce_valide(ad, cfg):
                        log(f"🔔 NOUVELLE : {ad.subject} — {ad.price} € — {ad.url}")
                        notifier_annonce(cfg, ad)
                    else:
                        log(f"Ignorée (filtre) : {ad.subject}")
                if not nouvelles:
                    log(f"Rien de nouveau ({len(annonces)} annonces).")

            vues.update(a.id for a in annonces)
            sauver_vues(vues)

            if bloque_notifie:
                envoyer_message(cfg, "✅ Le bot fonctionne à nouveau.")
            pause_blocage, bloque_notifie = 60, False
            time.sleep(random.uniform(f["attente_min"], f["attente_max"]))

        except DatadomeError:
            log(f"⚠️ Bloqué par l'anti-bot Leboncoin. Pause de {pause_blocage // 60} min.")
            if not bloque_notifie:
                envoyer_message(cfg, "⚠️ Leboncoin bloque temporairement le bot. "
                                     "Il réessaie automatiquement, rien à faire.")
                bloque_notifie = True
            time.sleep(pause_blocage)
            pause_blocage = min(pause_blocage * 2, 30 * 60)
            client = nouveau_client()

        except KeyboardInterrupt:
            log("Arrêt demandé.")
            return

        except Exception as e:
            log(f"Erreur : {e!r} — nouvel essai dans 60 s.")
            time.sleep(60)
            try:
                client = nouveau_client()
            except Exception:
                pass


def tester(cfg: dict) -> None:
    envoyer_message(cfg, "🧪 Test : si tu vois ce message, les notifications fonctionnent !")
    log("Message de test envoyé sur Telegram.")
    annonces = rechercher(nouveau_client(), cfg)
    log(f"{len(annonces)} annonces trouvées actuellement :")
    for ad in annonces[:10]:
        etat = "OK " if annonce_valide(ad, cfg) else "FILTRÉE"
        print(f"   [{etat}] {ad.price or 0:>6g} €  {ad.subject}  ({ad.location.city_label})")
    if annonces:
        notifier_annonce(cfg, annonces[0])
        log("Exemple de notification envoyé avec l'annonce la plus récente.")


if __name__ == "__main__":
    config = charger_config()
    if "COLLE_TON" in config["telegram"]["token"]:
        sys.exit("Renseigne d'abord ton token Telegram dans config.toml (voir README).")
    if "--chat-id" in sys.argv:
        afficher_chat_id(config)
    elif "COLLE_TON" in str(config["telegram"]["chat_id"]):
        sys.exit("Renseigne ton chat_id dans config.toml (lance :  python3 bot.py --chat-id).")
    elif "--test" in sys.argv:
        tester(config)
    else:
        surveiller(config)
