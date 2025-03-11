import os
import sys
import argparse  
import logging
from pydantic import BaseModel, ValidationError, Field
from openai import OpenAI, OpenAIError
from typing import List, Dict, Optional
from dotenv import load_dotenv
from config import MSG_COLOR, print_colored
from validation import clean_json, process_api_response_and_validate
from error_handlers import handle_api_errors




logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)


# Modèles Pydantic
#

# Fonction

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
    
def build_api_messages(selected_api, card_choice):
    """Construit la structure de messages pour la requête API
    
    Différencie la structure selon l'API utilisée (OpenAI vs Perplexity)
    
    Args:
        selected_api (str): "openai" ou "perplexity"
        card_choice (str): Nom de la carte bancaire choisie
        
    Returns:
        list: Structure de messages adaptée à l'API
    """

    base_content =( 
                    f"Provide structured JSON data for the {card_choice} Canadian card with these keys and specifications. "
                    "If any information is not found, return 'null' for the corresponding key.\n\n"  

                    "• cardName (string): Exact name of the card (ex: 'Amex Green Card')\n"  
                    "• issuer (string): 'American Express Canada' or 'null' if not found\n"  
                    "• annualFee (string): 'Free' or amount in $CAD (ex: '129$') or 'null'\n" 

                    "• interestRate (object):\n"
                    "   - purchaseRate (string): Interest rate in % (ex: '19.99%') or 'null'\n"
                    "   - cashAdvanceRate (string): Cash advance rate in % (ex: '23.99%') or 'null'\n"
                    "   - balanceTransferRate (string): Balance transfer rate in % (ex: '21.99%') or 'null'\n"
        
                    "• welcomeOffer (object):\n"
                    "   - bonusPoints (int)\n"
                    "   - description (string)\n"

                    "• rewardsProgram (object):\n"
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
                    "Return only JSON, no explanatory text or presentation.\n"
                    "ADD ALL FIELDS. If you don't have a response for a field, add 'null' or ['null'].\n"
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
            "content": "Provide structured JSON data with these keys and specifications. If any information is not found, return 'null' for the corresponding key."        },
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
        "perplexity": ["sonar-pro", "sonar", "sonar-reasoning-pro","sonar-deep-research"]
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

def create_api_client(selected_api,openai_key,perplexity_key):
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

def fetch_api_keys(selected_api: str) -> tuple[Optional[str], Optional[str]]:
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



    
# Implemtation de la logic    
def main():
    load_dotenv(override=True)
    
    selected_api, selected_model, card_choice =  prompt_for_api_and_model_selection()

    OPENAI_KEY, PERPLEXITY_KEY = fetch_api_keys(selected_api)

    #Client creation
    client = create_api_client(selected_api, OPENAI_KEY, PERPLEXITY_KEY)

    # Configuration de la requête
    messages= build_api_messages(selected_api, card_choice)

    print_colored(f"\nConnexion à {selected_api.upper()}", **MSG_COLOR["info"])

    api_success = False
    processing_success = False

    completion, api_success = execute_chat_completion(client, selected_api, selected_model, messages)
    
    response_text = clean_json(completion.choices[0].message.content)

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