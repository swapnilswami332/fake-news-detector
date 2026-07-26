export type Source = {
  title: string;
  url: string;
};

export type Prediction = {
  prediction: "Fake" | "Real";
  confidence: number;
  trust_score: number;
  model_reason: string;
  ai_fact_check: string;
  sources: Source[];
  processing_time_ms: number;
};
