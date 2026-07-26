from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .preprocessing import normalize_text


TRAINING_EXAMPLES = [
    ("Scientists publish peer reviewed study on coastal erosion trends", "Real"),
    ("City council approves funding for a new public library", "Real"),
    ("Health department releases weekly influenza surveillance report", "Real"),
    ("Election commission publishes official turnout figures", "Real"),
    ("University researchers describe results in a medical journal", "Real"),
    ("National weather service issues flood warning for the region", "Real"),
    ("Company files quarterly earnings report with market regulator", "Real"),
    ("Museum opens exhibition featuring local artists", "Real"),
    ("Government agency announces updated road safety guidance", "Real"),
    ("Hospital expands its emergency care facility next spring", "Real"),
    ("Independent audit finds school district followed procurement rules", "Real"),
    ("Public transport authority adds late night bus service", "Real"),
    ("Researchers measure declining bee populations over ten years", "Real"),
    ("Court releases written ruling in consumer protection case", "Real"),
    ("Census bureau reports population estimates for the county", "Real"),
    ("Water utility repairs broken pipe after neighborhood outage", "Real"),
    ("Space agency shares images from its latest satellite mission", "Real"),
    ("Local newspaper reports dates for the annual arts festival", "Real"),
    ("Medical association recommends updated childhood vaccination schedule", "Real"),
    ("Fire department contains warehouse fire with no reported injuries", "Real"),
    ("SHOCKING secret cure doctors do not want you to know", "Fake"),
    ("You will not believe what this politician did yesterday", "Fake"),
    ("Miracle drink melts fat overnight with no exercise", "Fake"),
    ("Government hides proof that all banks will close tomorrow", "Fake"),
    ("Breaking: celebrity confirms alien invasion is already underway", "Fake"),
    ("One strange trick makes you rich instantly guaranteed", "Fake"),
    ("Share this before authorities delete it from the internet", "Fake"),
    ("Scientists stunned by proof that the moon is made of cheese", "Fake"),
    ("Urgent warning: household spice cures every disease", "Fake"),
    ("Secret report proves schools are replacing history books tonight", "Fake"),
    ("Doctors hate this simple method that reverses aging", "Fake"),
    ("Exclusive: hidden device controls the weather over cities", "Fake"),
    ("This unbelievable video proves a giant creature lives downtown", "Fake"),
    ("Media refuses to report shocking truth about free energy", "Fake"),
    ("New law bans all pets nationwide starting next week", "Fake"),
    ("Ancient prophecy predicts exact date of worldwide blackout", "Fake"),
    ("Click now to see the miracle vaccine nobody discusses", "Fake"),
    ("Experts panic after mysterious signal predicts disaster", "Fake"),
    ("Billionaire gives everyone free money through this secret link", "Fake"),
    ("Officials admit water supply changes color because of conspiracy", "Fake"),
]


def train_model() -> None:
    texts, labels = zip(*TRAINING_EXAMPLES)
    vectorizer = TfidfVectorizer(
        preprocessor=normalize_text,
        ngram_range=(1, 2),
        min_df=1,
        max_features=4_000,
        sublinear_tf=True,
    )
    features = vectorizer.fit_transform(texts)
    model = LogisticRegression(max_iter=1_000, class_weight="balanced", random_state=42)
    model.fit(features, labels)

    model_dir = Path(__file__).parent / "models"
    model_dir.mkdir(exist_ok=True)
    joblib.dump(model, model_dir / "model.pkl")
    joblib.dump(vectorizer, model_dir / "vectorizer.pkl")
    print(f"Saved model artifacts to {model_dir}")


if __name__ == "__main__":
    train_model()
