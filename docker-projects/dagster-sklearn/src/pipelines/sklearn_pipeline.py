from dagster import pipeline
from solids.sklearn_solids import (
    fetch_titanic_dataset,
    feature_selection,
    split_into_train_test,
    get_features_columns,
    get_target_column,
    encode_features,
    logregression,
    fit_model,
    predict,
    get_accuracy_score,
)


# NOTE: When the same solid is being invoked multiple times, the solid
# names after the first invocation, will be suffixed (ex. "_2", "_3", etc)
# The 2nd invocation of get_features_columns will be shown in dagit as
# "get_features_columns_2" and the 2nd invocation of get_target_column
# will be shown in dagit as "get_target_column_2"
# With .alias(), we can give them a better name or alias, instead of
# the "_2" suffix naming convention.
# Documentation:
# https://docs.dagster.io/concepts/solids-pipelines/pipelines#aliases-and-tags


@pipeline
def sklearn_pipeline():
    raw_data = fetch_titanic_dataset()
    final_features = feature_selection(raw_data)
    df_train, df_test = split_into_train_test(final_features)
    X_train = get_features_columns.alias("get_features_from_train")(df_train)
    X_test = get_features_columns.alias("get_features_from_test")(df_test)
    y_train = get_target_column.alias("get_target_from_train")(df_train)
    y_test = get_target_column.alias("get_target_from_test")(df_test)
    ct = encode_features()
    logreg = logregression()
    model = fit_model(X_train, y_train, ct, logreg)
    y_pred = predict(X_test, model)
    get_accuracy_score(y_test, y_pred)
