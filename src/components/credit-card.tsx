// components/CreditCardFetcher.tsx
"use client";
import { useState } from "react";

interface CreditCardData {
  cardName: string;
  issuer: string;
  annualFee: string;
  interestRate?: {
    purchaseRate: string;
  };
  rewardsProgram?: {
    program: string;
    earnRates?: {
      regularSpending: string;
    };
    redemptionOptions?: string[];
  };
  mainBenefits?: string[];
  creditScoreRecommendation?: string;
  foreignTransactionFee?: string;
  officialWebsite?: string;
}

export default function CreditCardFetcher() {
  const [cardData, setCardData] = useState<CreditCardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cardChoice, setCardChoice] = useState("");
  const [selectedApi, setSelectedApi] = useState("openai");
  const [selectedModel, setSelectedModel] = useState("gpt-3.5-turbo");

  const models = {
    openai: ["gpt-3.5-turbo", "gpt-4"],
    perplexity: ["sonar-pro", "sonar", "sonar-reasoning-pro"],
  };

  const fetchCardData = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cardChoice.trim()) {
      setError("Please enter a card name");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        process.env.NEXT_PUBLIC_API_URL + "/process",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            card_choice: cardChoice,
            selected_api: selectedApi,
            selected_model: selectedModel,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to fetch card data");
      }

      setCardData(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <form onSubmit={fetchCardData} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Credit Card Name:
            <input
              type="text"
              value={cardChoice}
              onChange={(e) => setCardChoice(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="e.g., Amex Platinum"
            />
          </label>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              API Provider:
              <select
                value={selectedApi}
                onChange={(e) => {
                  setSelectedApi(e.target.value);
                  setSelectedModel(
                    models[e.target.value as keyof typeof models][0]
                  );
                }}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="openai">OpenAI</option>
                <option value="perplexity">Perplexity</option>
              </select>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Model:
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                {models[selectedApi as keyof typeof models].map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
        >
          {loading ? "Fetching Data..." : "Get Card Details"}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
          Error: {error}
        </div>
      )}

      {cardData && (
        <div className="mt-6 space-y-4">
          <h2 className="text-2xl font-bold text-gray-900">
            {cardData.cardName}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InfoBlock title="Issuer" value={cardData.issuer} />
            <InfoBlock title="Annual Fee" value={cardData.annualFee} />
            <InfoBlock
              title="Credit Score Recommendation"
              value={cardData.creditScoreRecommendation}
            />
            <InfoBlock
              title="Foreign Transaction Fee"
              value={cardData.foreignTransactionFee}
            />
          </div>

          {cardData.interestRate?.purchaseRate && (
            <Section title="Interest Rates">
              <p>Purchase Rate: {cardData.interestRate.purchaseRate}</p>
            </Section>
          )}

          {cardData.rewardsProgram && (
            <Section title="Rewards Program">
              <InfoBlock
                title="Program"
                value={cardData.rewardsProgram.program}
              />
              {cardData.rewardsProgram.earnRates?.regularSpending && (
                <InfoBlock
                  title="Earn Rate"
                  value={cardData.rewardsProgram.earnRates.regularSpending}
                />
              )}
              {cardData.rewardsProgram.redemptionOptions && (
                <div>
                  <h4 className="text-sm font-medium text-gray-600">
                    Redemption Options:
                  </h4>
                  <ul className="list-disc pl-5">
                    {cardData.rewardsProgram.redemptionOptions.map(
                      (option, index) => (
                        <li key={index} className="text-gray-700">
                          {option}
                        </li>
                      )
                    )}
                  </ul>
                </div>
              )}
            </Section>
          )}

          {cardData.mainBenefits && (
            <Section title="Main Benefits">
              <ul className="list-disc pl-5 space-y-1">
                {cardData.mainBenefits.map((benefit, index) => (
                  <li key={index} className="text-gray-700">
                    {benefit}
                  </li>
                ))}
              </ul>
            </Section>
          )}

          {cardData.officialWebsite && (
            <div className="mt-4">
              <a
                href={cardData.officialWebsite}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                Official Website →
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const InfoBlock = ({ title, value }: { title: string; value?: string }) =>
  value ? (
    <div>
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <p className="text-gray-900">{value}</p>
    </div>
  ) : null;

const Section = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <div className="bg-gray-50 p-4 rounded-lg">
    <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
    {children}
  </div>
);
