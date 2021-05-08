from dagster import solid, Output, OutputDefinition
from pathlib import Path
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

# Relative to this .py file, move up 2 folder levels to
# fetch the local csv file located in the "data" folder
# of this repo
data_dir = Path(__file__).resolve().parents[2] / "data"


@solid(
    description="Retrieves the Titanic data set",
)
def fetch_titanic_dataset(context) -> pd.DataFrame:
    # For now, hard-code the path/filename
    df = pd.read_csv(data_dir / "titanic.csv")

    context.log.info(f"Number of rows: {df.shape[0]}")
    context.log.info(f"Number of columns: {df.shape[1]}")
    context.log.info(f"Columns: {df.columns}")

    return df


@solid(
    description="Limits data set to features we want to use",
)
def feature_selection(context, df: pd.DataFrame) -> pd.DataFrame:
    keep_columns = ["Parch", "Fare", "Embarked", "Sex", "Name", "Age", "Survived"]
    df_final = df[keep_columns]

    context.log.info(f"Number of rows: {df_final.shape[0]}")
    context.log.info(f"Number of columns: {df_final.shape[1]}")
    context.log.info(f"Columns: {df_final.columns}")
    context.log.info(f"5 random rows: \n {df_final.sample(n=5).transpose()}")

    return df_final


@solid(
    description="Split the data set into training (75%) and testing (25%)",
    output_defs=[
        OutputDefinition(name="training_set", dagster_type=pd.DataFrame),
        OutputDefinition(name="testing_set", dagster_type=pd.DataFrame),
    ],
)
def split_into_train_test(context, df: pd.DataFrame):

    df_train, df_test = train_test_split(df, train_size=0.75, random_state=42)

    context.log.info(f"Number of rows in train: {df_train.shape[0]}")
    context.log.info(f"Number of columns in train: {df_train.shape[1]}")

    context.log.info(f"Number of rows in test: {df_test.shape[0]}")
    context.log.info(f"Number of columns in test: {df_test.shape[1]}")

    yield Output(df_train, output_name="training_set")
    yield Output(df_test, output_name="testing_set")


@solid(description="Define required encoding and return column transformer")
def encode_features(context):

    imp_constant = SimpleImputer(strategy="constant", fill_value="missing")
    ohe = OneHotEncoder()

    imp_ohe = make_pipeline(imp_constant, ohe)
    vect = CountVectorizer()
    imp = SimpleImputer()

    ct = make_column_transformer(
        (imp_ohe, ["Embarked", "Sex"]),
        (vect, "Name"),
        (imp, ["Age", "Fare"]),
        remainder="passthrough",
    )

    return ct


@solid(description="Return logistic regression model")
def logregression(context):

    return LogisticRegression(solver="liblinear", random_state=1)


@solid(description="Get features columns from dataframe")
def get_features_columns(context, df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Parch", "Fare", "Embarked", "Sex", "Name", "Age"]

    return df[cols]


@solid(description="Get target column from dataframe")
def get_target_column(context, df: pd.DataFrame) -> pd.Series:

    return df["Survived"]


@solid(description="Fit the model")
def fit_model(context, X: pd.DataFrame, y: pd.Series, ct, model):
    pipe = make_pipeline(ct, model)
    pipe.fit(X, y)

    return pipe


@solid(description="Predict on new data")
def predict(context, X_new: pd.DataFrame, pipe):

    context.log.info(f"Prediction: \n{pipe.predict(X_new)}")

    return pipe.predict(X_new)


@solid(description="Get accuracy score")
def get_accuracy_score(context, y_true: pd.Series, y_pred: np.ndarray):

    context.log.info(f"Accuracy score: {accuracy_score(y_true, y_pred)}")
