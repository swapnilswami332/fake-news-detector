from pathlib import Path

import joblib
import numpy as np

from .preprocessing import normalize_text

try:
    import shap
except ImportError:
    shap = None


class NewsClassifier:
    def __init__(self) -> None:
        model_dir = Path(__file__).parent / "models"
        self.model = joblib.load(model_dir / "model.pkl")
        self.vectorizer = joblib.load(model_dir / "vectorizer.pkl")

    def analyze(self, text: str) -> dict[str, object]:
        features = self.vectorizer.transform([normalize_text(text)])
        probabilities = self.model.predict_proba(features)[0]
        label_index = int(np.argmax(probabilities))
        prediction = str(self.model.classes_[label_index])
        confidence = round(float(probabilities[label_index]) * 100)
        terms = self._important_terms(features, label_index)

        if terms:
            direction = "sensational or unsupported" if prediction == "Fake" else "reporting-style"
            reason = f"The {direction} language around “{', '.join(terms[:3])}” influenced this result."
        else:
            reason = "The model found no strongly distinctive wording in this text."

        return {
            "prediction": prediction,
            "confidence": confidence,
            "model_reason": reason,
            "important_terms": terms,
        }

    def _important_terms(self, features, label_index: int) -> list[str]:
        contributions = self._shap_values(features, label_index)
        if contributions is None:
            contributions = self._coefficient_values(features, label_index)

        feature_names = self.vectorizer.get_feature_names_out()
        active_indices = features.nonzero()[1]
        ranked_indices = sorted(
            active_indices,
            key=lambda index: abs(contributions[index]),
            reverse=True,
        )
        return [feature_names[index] for index in ranked_indices[:5]]

    def _shap_values(self, features, label_index: int) -> np.ndarray | None:
        if shap is None:
            return None
        try:
            explainer = shap.LinearExplainer(self.model, features)
            values = explainer.shap_values(features)
            if isinstance(values, list):
                return np.asarray(values[label_index][0])
            values = np.asarray(values)
            return values[0] if values.ndim == 2 else values[label_index][0]
        except Exception:
            return None

    def _coefficient_values(self, features, label_index: int) -> np.ndarray:
        coefficient = self.model.coef_[0]
        if self.model.classes_[label_index] != self.model.classes_[1]:
            coefficient = -coefficient
        return features.toarray()[0] * coefficient
