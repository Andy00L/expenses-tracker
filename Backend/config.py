from typing import List, Optional
from pydantic import BaseModel, Field
from termcolor import colored


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

class EarnRate(BaseModel):
    regular_spending: Optional[str] = Field(alias="regularSpending",default=None)

class WelcomeOffer(BaseModel):
    bonus_points: Optional[int] = Field(alias="bonusPoints",default=None)
    description: Optional[str] = Field(alias="description",default=None)

class InterestRate(BaseModel):
    purchase_rate: Optional[str] = Field(alias="purchaseRate",default=None)
    cash_advance_rate: Optional[str] = Field(alias="cashAdvanceRate", default=None)
    balance_transfer_rate: Optional[str] = Field(alias="balanceTransferRate", default=None)

class Rewards(BaseModel):
    program: Optional[str] = Field(alias="program",default=None)  # Fixed alias
    earn_rates: Optional[EarnRate] = Field(alias="earnRates",default=None)
    redemption_options: Optional[List[str]] = Field(alias="redemptionOptions",default=None)

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
