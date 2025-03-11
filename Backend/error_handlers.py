
import json
from flask import logging
from jsonschema import ValidationError
from openai import APIConnectionError, AuthenticationError, OpenAIError, RateLimitError
from core_functions import MSG_COLOR, print_colored


def handle_api_errors(e: Exception, api_type: str="", response_text=""):
    """Gère les erreurs d'API de manière centralisée avec messages colorés
    
    Args:
        e (Exception): Exception capturée
        api_type (str): Type d'API concerné ("openai" ou "perplexity")
    """

    error_message = str(e)

    # Authentification invalide (clés incorrectes ou expirées)
    if isinstance(e, AuthenticationError):
        msg = f"🔒 {api_type.upper()}: Clé API invalide"
        print_colored(msg, **MSG_COLOR["error"])
        logging.error(msg)    # Limite de requêtes atteinte (API saturée)
    elif isinstance(e, RateLimitError):
        msg = f"⏳ {api_type.upper()}: Limite de débit atteinte"
        print_colored(msg, **MSG_COLOR["warning"])
        logging.warning(msg)    # Erreur de connexion réseau ou API hors ligne
    elif isinstance(e, APIConnectionError):
        msg = f"🔴 {api_type.upper()}: Connexion impossible"
        print_colored(msg, **MSG_COLOR["error"])
        logging.error(msg)    # Réponse non conforme au format JSON attendu
    elif isinstance(e,json.JSONDecodeError):
        print_colored("❌ ERREUR JSON : Format incorrect", **MSG_COLOR["error"])
        print_colored(f"Détails : {str(e)}", color="yellow")  # Use keyword argument
        print_colored(f"Contenu reçu : '{response_text[:50]}...'", color="magenta")
        print_colored("Vérifiez la structure de la réponse API", **MSG_COLOR["warning"])
    # Données non conformes au modèle Pydantic
    elif isinstance(e, ValidationError):
        print_colored("⚠️ ERREUR DE VALIDATION", **MSG_COLOR["warning"])
        for error in e.errors():
            loc = " → ".join(map(str, error['loc']))
            print_colored(f"  • {loc} : {error['msg']}", **MSG_COLOR["error"])
    # Incohérence de type (ex: str au lieu de int)
    elif isinstance(e, TypeError):
        print_colored("❗ ERREUR DE TYPE : Données non sérialisables", **MSG_COLOR["error"])
        print_colored(f"Détails : {str(e)}", color="yellow")
    # Valeur invalide (ex: champ requis manquant)
    elif isinstance(e, ValueError):
        print_colored(f"❗ ERREUR DE TYPE/VALEUR : {str(e)}", **MSG_COLOR["error"])
    elif isinstance(e, OpenAIError):
        msg = f"❗ {api_type.upper()}: Erreur OpenAI - {error_message}"
        print_colored(msg, **MSG_COLOR["error"])
        logging.error(msg)
    # Structure des messages incorrecte pour l'API
    elif "Last message must have role `user`" in error_message:
        print_colored(f"⚠️ {api_type.upper()}: Dernier message doit être un message utilisateur (role `user`)", **MSG_COLOR["warning"])
    # Erreur générique non catégorisée
    else:
        print_colored(f"❗ {api_type.upper()}: {error_message}", **MSG_COLOR["error"])
