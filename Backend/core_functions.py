import os
import sys
import argparse
import argparse  
from termcolor import colored
from pydantic import BaseModel, ValidationError, Field
from openai import OpenAI, APIConnectionError, APIError, AuthenticationError, RateLimitError, OpenAIError
from typing import List, Dict, Optional
import json
from dotenv import load_dotenv

MSG_COLOR = {
    "success": {"color": "green", "attrs": ["bold"]},
    "warning": {"color": "yellow", "attrs": ["bold"]},
    "error": {"color": "red", "attrs": ["bold"]},
    "info": {"color": "blue", "attrs": ["bold"]},
}

def print_colored(text, **kwargs):
    color = kwargs.get("color", "white")
    attrs = kwargs.get("attrs", None)
    print(colored(text, color, attrs=attrs))

# Modèles Pydantic
#
class EarnRate(BaseModel):
    regular_spending: Optional[str] = Field(alias="regularSpending")

class WelcomeOffer(BaseModel):
    bonus_points: Optional[int] = Field(alias="bonusPoints")
    description: Optional[str] = Field(alias="description")

class InterestRate(BaseModel):
    purchase_rate: Optional[str] = Field(alias="purchaseRate")

class Rewards(BaseModel):
    program: Optional[str] = Field(alias="program")  # Fixed alias
    earn_rates: Optional[EarnRate] = Field(alias="earnRates")
    redemption_options: Optional[List[str]] = Field(alias="redemptionOptions")

class CreditCard(BaseModel):
    card_name: Optional[str] = Field(alias="cardName")
    issuer: Optional[str] = Field(alias="issuer")
    annual_fee: Optional[str] = Field(alias="annualFee")
    interest_rate: Optional[InterestRate] = Field(alias="interestRate")
    rewards: Optional[Rewards] = Field(alias="rewardsProgram")  # Top-level key is "rewardsProgram"
    perks: Optional[List[str]] = Field(alias="mainBenefits")
    credit_score: Optional[str] = Field(alias="creditScoreRecommendation")
    introductory_offer: Optional[WelcomeOffer] = Field(
        alias="welcomeOffer", default=None
    )  # Now optional with default
    foreign_fee: Optional[str] = Field(alias="foreignTransactionFee")
    source: Optional[str] = Field(alias="officialWebsite")

# Fonction
#
def get_api_client(api_type: str, openai_key: str, perplexity_key: str):
    """Initialise le client API approprié en fonction du type spécifié
    
    Args:
        api_type (str): "openai" ou "perplexity"
        openai_key (str): Clé d'API OpenAI
        perplexity_key (str): Clé d'API Perplexity
        
    Returns:
        Client API configuré avec les paramètres appropriés
    
    Raises:
        ValueError: Si le type d'API n'est pas supporté
    """
    if api_type == "openai":
        return OpenAI(api_key=openai_key)
    elif api_type == "perplexity":
        # Configuration spécifique pour Perplexity avec URL de base différente
        return OpenAI(
            api_key=perplexity_key,
            base_url="https://api.perplexity.ai"
        )
    else:
        raise ValueError("API non supportée")
    
def handle_api_errors(e: Exception, api_type: str, response_text=""):
    """Gère les erreurs d'API de manière centralisée avec messages colorés
    
    Args:
        e (Exception): Exception capturée
        api_type (str): Type d'API concerné ("openai" ou "perplexity")
    """

    error_message = str(e)

    # Authentification invalide (clés incorrectes ou expirées)
    if isinstance(e, AuthenticationError):
        print_colored(f"🔒 {api_type.upper()}: Clé API invalide", **MSG_COLOR["error"])
    # Limite de requêtes atteinte (API saturée)
    elif isinstance(e, RateLimitError):
        print_colored(f"⏳ {api_type.upper()}: Limite de débit atteinte", **MSG_COLOR["warning"])
    # Erreur de connexion réseau ou API hors ligne
    elif isinstance(e, APIConnectionError):
        print_colored(f"🔴 {api_type.upper()}: Connexion impossible", **MSG_COLOR["error"])
    # Réponse non conforme au format JSON attendu
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
    # Structure des messages incorrecte pour l'API
    elif "Last message must have role `user`" in error_message:
        print_colored(f"⚠️ {api_type.upper()}: Dernier message doit être un message utilisateur (role `user`)", **MSG_COLOR["warning"])
    # Erreur générique non catégorisée
    else:
        print_colored(f"❗ {api_type.upper()}: {error_message}", **MSG_COLOR["error"])

def build_messages(selected_api, card_choice):
    """Construit la structure de messages pour la requête API
    
    Différencie la structure selon l'API utilisée (OpenAI vs Perplexity)
    
    Args:
        selected_api (str): "openai" ou "perplexity"
        card_choice (str): Nom de la carte bancaire choisie
        
    Returns:
        list: Structure de messages adaptée à l'API
    """

    base_content =( 
                    f"Provide structured JSON data for the {card_choice} Canadian card with these keys and specifications. If any information is not found, return 'null' for the corresponding key.\n\n"  
                    "• cardName (string): Exact name of the card (ex: 'Amex Green Card')\n"  
                    "• issuer (string): 'American Express Canada' or 'null' if not found\n"  
                    "• annualFee (string): 'Free' or amount in $CAD (ex: '129$') or 'null'\n"  
                    "• interestRate (object):\n"  
                    "   - purchaseRate (string): Interest rate in % (ex: '19.99%') or 'null'\n"  
                    "• welcomeOffer (object):\n"  
                    "• rewardsProgram (object):\n"  
                    "   - bonusPoints (int): 30,000\n"  
                    "   - description (string): Get up to 30,000 points in the first year by earning 2,500 points\n"  
                    "   - program (string): Name of the program or 'null'\n"  
                    "   - earnRates (object):\n"  
                    "       - regularSpending (string): Points per $1 or 'null'\n"  
                    "   - redemptionOptions (array): 2-3 options or ['null']\n"  
                    "• mainBenefits (array): 3-5 benefits or ['null']\n"  
                    "• creditScoreRecommendation (string): Score range (ex: 'Good or Excellent') or 'null'\n"  
                    "• foreignTransactionFee (string): 'None' or amount (ex: '0%') or 'null'\n"  
                    "• officialWebsite (string): Official Canadian link or 'null'\n\n"  
                    "Formats:\n"  
                    "- Numeric values remain as strings (ex: '129$')\n"  
                    "- Empty objects must contain 'null' for sub-fields\n"  
                    "- Empty arrays must be ['null']\n"  
                    "Return only JSON, no explanatory text or presentation"      
                )
    if selected_api == "openai":
        messages=[
                {
                    "role": "system",
                    "content": base_content
                }
            ]
    else:  # Perplexity
        messages = [
        # Message système (configuration)
        {
            "role": "system",
            "content": "Provide structured JSON data with these keys and specifications. If any information is not found, return 'null' for the corresponding key"        },
        # Message utilisateur (requete finale)
        {
            "role": "user",
            "content": (base_content)
        }
    ]   
        
    return messages
    
def prompt_for_api_and_model_selection():
    """Affiche l'interface interactive de sélection des paramètres
    
    Renvoie les choix de l'utilisateur après validation
    """
    # Écran d'accueil interactif
    print_colored("Bienvenue dans l'assistant de carte de crédit", **MSG_COLOR["info"])
    # Sélection de l'API par menu
    api_options = ["OpenAI", "Perplexity"]
    while True:
        print("\nChoisissez l'API :")
        for idx, option in enumerate(api_options, 1):
            print(f"{idx}. {option}")
        try:
            api_choice = int(input("Entrez le numéro : "))
            selected_api = api_options[api_choice-1].lower()
            break
        except (ValueError, IndexError):
            print_colored("Numéro invalide", **MSG_COLOR["warning"])
 
    # Sélection du modèle par menu
    models = {
        "openai": ["o1", "gpt-3.5-turbo"],
        "perplexity": ["sonar-pro", "sonar", "sonar-reasoning-pro"]
    }
    model_list = models[selected_api]
    while True:
        print("\nModèles disponibles :")
        for idx, model in enumerate(model_list, 1):
            print(f"{idx}. {model}")
        try:
            model_choice = int(input("Entrez le numéro du modèle : "))
            selected_model = model_list[model_choice-1]
            break
        except (ValueError, IndexError):
            print_colored("Numéro invalide", **MSG_COLOR["warning"])


    print("\nChoisissez la carte :")
    card_choice = str(input("Entrez le nom de la carte : "))

    return selected_api, selected_model, card_choice

def client_creation(selected_api,openai_key,perplexity_key):
    # Création du client
    try:
        client = get_api_client(
            api_type=selected_api,
            openai_key=openai_key or os.getenv("OPENAI_API_KEY"),
            perplexity_key=perplexity_key or os.getenv("PERPLEXITY_API_KEY")
        )
        return client
    except Exception as e:
        print_colored(f"Impossible de créer le client : {str(e)}", **MSG_COLOR["error"])
        raise  
    
def execute_chat_completion(client, selected_api: str, selected_model: str, messages: list) -> tuple[bool, Optional[object]]:
    """Exécute une requête de complétion chat en fonction de l'API choisie et gère les erreurs
    
    Args:
        client: Client API configuré (OpenAI ou Perplexity)
        selected_api (str): Type d'API ("openai" ou "perplexity")
        selected_model (str): Nom du modèle à utiliser
        messages (list): Structure de messages pour la requête
        
    Returns:
        tuple: 
            - bool: Succès de la requête API
            - object: Réponse de l'API ou None en cas d'échec
    """

    try:
            print(selected_api, selected_model)
            if selected_api == "openai":
                # OpenAI requires response_format
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    response_format={"type": "json_object"}
                )
            else:
                # Perplexity doesn't support response_format
                completion = client.chat.completions.create(
                    model=selected_model,
                    messages=messages
                )
            print_colored("✅ Connexion réussie", **MSG_COLOR["success"])
            return (completion,True)
    except OpenAIError as e:
        handle_api_errors(e, selected_api )
        return (False, None)
    except Exception as e:
        print_colored(f"❗ ERREUR INCONNUE : {str(e)}", **MSG_COLOR["error"])
        return (False, None)

def retrieve_api_keys_based_on_api_selection(selected_api: str) -> tuple[Optional[str], Optional[str]]:
    """Récupère les clés d'API depuis les variables d'environnement ou saisie manuelle selon l'API choisie
    
    Args:
        selected_api (str): Type d'API ("openai" ou "perplexity")
        
    Returns:
        tuple:
            - str: Clé OpenAI ou None
            - str: Clé Perplexity ou None
            
    Raises:
        SystemExit: Si aucune clé valide n'est fournie
    """
    openai_key = os.getenv('OPENAI_KEY')
    perplexity_key = os.getenv('PERPLEXITY_KEY')

    # Demande manuelle de la clé si manquante, selon l'API choisie
    if selected_api == "openai":
        # Vérification de la clé OpenAI
        if not openai_key:
            # Demande interactive si la clé n'est pas présente dans .env
            openai_key = input("Clé OpenAI (laisser vide pour utiliser .env) : ").strip()
    else:
        if not perplexity_key:
            perplexity_key = input("Clé Perplexity (laisser vide pour utiliser .env) : ").strip()

    if not (openai_key or perplexity_key):
        print_colored("❌ Clés d'API manquantes", **MSG_COLOR["error"])
        sys.exit(1)

    return openai_key, perplexity_key 

def process_api_response_and_validate(
    completion: object, 
    selected_api: str, 
    response_text: str
)  -> bool:
    """Traite la réponse API, valide les données et sauvegarde les résultats
    
    Args:
        completion (object): Objet de réponse de l'API
        selected_api (str): Type d'API utilisé ("openai" ou "perplexity")
        response_text (str): Contenu brut de la réponse API
        
    Returns:
        bool: Vrai si le traitement est réussi, Faux sinon
    """
    try: 
        with open("previu.json", "w", encoding="utf-8") as f:
            f.write(response_text)
        print_colored("💾 Données brutes sauvegardées", **MSG_COLOR["success"])
        # Add check for empty response
        if not response_text.strip():
            raise ValueError("Réponse API vide")
        card_data = json.loads(response_text)
        
        # Conversion manuelle si nécessaire
        if "annualFee" in card_data and isinstance(card_data["annualFee"], int):
            card_data["annualFee"] = str(card_data["annualFee"])
        # Validation
        credit_card = CreditCard(**card_data)
        
        print_colored("✅ Données validées", **MSG_COLOR["success"])
        # Sauvegarde finale
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump([credit_card.model_dump(by_alias=True)], f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        handle_api_errors(e, selected_api, response_text)
        return False  # Return tuple


# Implemtation de la logic    
def main():
    load_dotenv(override=True)
    
    selected_api, selected_model, card_choice =  prompt_for_api_and_model_selection()

    OPENAI_KEY, PERPLEXITY_KEY = retrieve_api_keys_based_on_api_selection(selected_api)

    #Client creation
    client = client_creation(selected_api, OPENAI_KEY, PERPLEXITY_KEY)

    # Configuration de la requête
    messages= build_messages(selected_api, card_choice)

    print_colored(f"\nConnexion à {selected_api.upper()}", **MSG_COLOR["info"])

    api_success = False
    processing_success = False

    completion, api_success = execute_chat_completion(client, selected_api, selected_model, messages)
    
    response_text = completion.choices[0].message.content

    if api_success:
        processing_success = process_api_response_and_validate(completion,selected_api, response_text)
    if not api_success:
        print_colored("❌ ÉCHEC DE LA CONNEXION", **MSG_COLOR["error"])
    elif processing_success:
        print_colored("✅ OPÉRATION COMPLÉTÉE", **MSG_COLOR["success"])
    else:
        print_colored("⚠️ TRAITEMENT ÉCHEC", **MSG_COLOR["warning"])

if __name__ == "__main__":
    main()