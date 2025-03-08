import os
import sys
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



def get_api_client(api_type: str, openai_key: str, perplexity_key: str):
    if api_type == "openai":
        return OpenAI(api_key=openai_key)
    elif api_type == "perplexity":
        return OpenAI(
            api_key=perplexity_key,
            base_url="https://api.perplexity.ai"
        )
    else:
        raise ValueError("API non supportée")
    
def handle_api_errors(e: Exception, api_type: str):
    if isinstance(e, AuthenticationError):
        print_colored(f"🔒 ERREUR {api_type.upper()}: Clé API invalide", **MSG_COLOR["error"])
    elif isinstance(e, RateLimitError):
        print_colored(f"⏳ ERREUR {api_type.upper()}: Limite de débit atteinte", **MSG_COLOR["warning"])
    elif isinstance(e, APIConnectionError):
        print_colored(f"🔴 ERREUR {api_type.upper()}: Connexion impossible", **MSG_COLOR["error"])
    else:
        print_colored(f"❗ ERREUR INCONNUE {api_type.upper()}: {str(e)}", **MSG_COLOR["error"])

    

def main():
    load_dotenv()


    
    if not api_key:
        print_colored("❌ ERREUR CRITIQUE : Clé API manquante", **MSG_COLOR["error"])
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    api_success = False
    processing_success = False

    print_colored("▸ Connexion à l'API OpenAI...", **MSG_COLOR["info"])

    try:
        completion = client.chat.completions.create(
            model="o1",
            messages=[
                {
    "role": "system",
    "content": 
    "Fournissez des données structurées en JSON sur la carte Amex COBALT canadienne avec ces clés et spécifications. Si une information n'est pas trouvée, retournez 'null' pour la clé correspondante.\n\n"
    "• cardName (string): Nom exact de la carte (ex: 'Amex Green Card')\n"
    "• issuer (string): 'American Express Canada' ou 'null' si non trouvé\n"
    "• annualFee (string): 'Gratuite' ou montant en $CAD (ex: '129$') ou 'null'\n"
    "• interestRate (object):\n"
    "   - purchaseRate (string): Taux d'intérêt en % (ex: '19.99%') ou 'null'\n"
    "• welcomeOffer (object):"
    "• rewardsProgram (object):\n"
    "   - bonusPoints (int): 30 000"
    "   - description (string):Obtenez jusqu’à 30 000 points la première année en accumulant 2 500 points"
    "   - program (string): Nom du programme ou 'null'\n"
    "   - earnRates (object):\n"
    "       - regularSpending (string): Points par $1 ou 'null'\n"
    "   - redemptionOptions (array): 2-3 options ou ['null']\n"
    "• mainBenefits (array): 3-5 avantages ou ['null']\n"
    "• creditScoreRecommendation (string): Tranche de score (ex: 'Bon ou excellent') ou 'null'\n"
    "• foreignTransactionFee (string): 'Aucun' ou montant (ex: '0%') ou 'null'\n"
    "• officialWebsite (string): Lien officiel canadien ou 'null'\n\n"
    "Formats : \n"
    "- Les valeurs numériques restent des strings (ex: '129$')\n"
    "- Les objets vides doivent contenir 'null' pour les sous-champs\n"
    "- Les tableaux vides doivent être ['null']\n"
}
            ],
            response_format={"type": "json_object"}
        )
        api_success = True
        print_colored("✅ Connexion réussie", **MSG_COLOR["success"])

    except AuthenticationError:
        print_colored("🔒 ERREUR : Clé API invalide", **MSG_COLOR["error"])

    except Exception as e:
        print_colored(f"❗ ERREUR INCONNUE : {str(e)}", **MSG_COLOR["error"])

    if api_success:
        try:
            response_text = completion.choices[0].message.content
            with open("previu.json", "w", encoding="utf-8") as f:
                f.write(response_text)
            print_colored("💾 Données brutes sauvegardées", **MSG_COLOR["success"])

            card_data = json.loads(response_text)
            
            # Conversion manuelle si nécessaire
            if "annualFee" in card_data and isinstance(card_data["annualFee"], int):
                card_data["annualFee"] = str(card_data["annualFee"])

            # Validation
            credit_card = CreditCard(**card_data)
            processing_success = True
            print_colored("✅ Données validées", **MSG_COLOR["success"])

            # Sauvegarde finale
            with open("result.json", "w", encoding="utf-8") as f:
                json.dump([credit_card.model_dump(by_alias=True)], f, indent=2, ensure_ascii=False)

        except json.JSONDecodeError as e:
            print_colored("❌ ERREUR JSON : Format incorrect", **MSG_COLOR["error"])
            print_colored(f"Détails : {str(e)}", "yellow")

        except ValidationError as e:
            print_colored("⚠️ ERREUR DE VALIDATION", **MSG_COLOR["warning"])
            print_colored("Problèmes détectés :", **MSG_COLOR["error"])
            for error in e.errors():
                loc = " → ".join(map(str, error['loc']))
                print_colored(f"  • {loc} : {error['msg']}", color="red")

        except TypeError as e:
            print_colored("❗ ERREUR DE TYPE : Données non sérialisables", **MSG_COLOR["error"])
            print_colored(f"Détails : {str(e)}", "yellow")

    if not api_success:
        print_colored("❌ ÉCHEC DE LA CONNEXION", **MSG_COLOR["error"])
    elif processing_success:
        print_colored("✅ OPÉRATION COMPLÉTÉE", **MSG_COLOR["success"])
    else:
        print_colored("⚠️ TRAITEMENT ÉCHEC", **MSG_COLOR["warning"])

if __name__ == "__main__":
    main()