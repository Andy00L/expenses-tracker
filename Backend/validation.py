import json

from jsonschema import ValidationError

from config import MSG_COLOR, CreditCard, print_colored
from error_handlers import handle_api_errors


def save_data(filename: str, data: dict) -> None:
    formatted_json = json.dumps([data], indent=2, ensure_ascii=False)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted_json)

def validate_dict(response_text: dict)-> dict:

    # Conversion manuelle si nécessaire
    if "annualFee" in response_text and isinstance(response_text["annualFee"], int):
        response_text["annualFee"] = str(response_text["annualFee"])
    try:
        credit_card = CreditCard(**response_text)
        return credit_card.model_dump(by_alias=True)
    except ValidationError as e:
        handle_api_errors(e)
        raise

def clean_json(response_text: str) -> dict:
    try:
        # Clean response text to extract only JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == 0:
            raise ValueError("Aucun JSON détecté dans la réponse")

        data = response_text[json_start:json_end]

        # Remove markdown code blocks if present
        data_str = data.replace('```json', '').replace('```', '').strip()
        data_dict = json.loads(data_str)
        return data_dict
    except Exception as e:
        handle_api_errors(e)

def process_api_response_and_validate(
    completion: object, 
    selected_api: str, 
    response_text: dict
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
        save_data("previus.json", response_text)
        print_colored("💾 Données brutes sauvegardées", **MSG_COLOR["success"])
        # Add check for empty response
        if not response_text:
            raise ValueError("Réponse API vide")
        
        validated_reponse=validate_dict(response_text)
        print_colored("✅ Données validées", **MSG_COLOR["success"])
        # Sauvegarde finale
        save_data("result.json",validated_reponse)
        return True
    except Exception as e:
        handle_api_errors(e, selected_api, response_text)
        return False  # Return tuple
