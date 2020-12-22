from dagster import (
    AssetMaterialization,
    EventMetadataEntry,
    execute_pipeline,
    pipeline,
    solid,
    InputDefinition,
    OutputDefinition,
    Output,
    failure_hook,
    success_hook,
)
import dagster_pandas
import pandas as pd 
import time
DataFrame = dagster_pandas.create_dagster_pandas_dataframe_type(name="DataFrame")


@solid(
    description=("Extracts a csv file from url and saves it as a dataframe"),
    input_defs=[
        InputDefinition(
            name="url",
            description="URL to the csv file to be downloaded",
            dagster_type=str
        )
    ],
    output_defs=[
        OutputDefinition(
            name="dataframe",
            dagster_type=DataFrame
        )
    ]
)
def fetchCsv(context, url: str) -> DataFrame:
    df = pd.read_csv(url)
    context.log.info("Executing time delay...")
    time.sleep(10)

    yield Output(value=df, output_name="dataframe")


@solid(
    description=("Transform name column by replacing space with comma"),
    input_defs=[
        InputDefinition(
            name="df",
            description="cereal dataframe",
            dagster_type=DataFrame
        )
    ],
    output_defs=[
        OutputDefinition(
            name="dataframe",
            dagster_type=DataFrame
        )
    ]
)
def transformName(context, df: DataFrame) -> DataFrame:
    df['name'] = df['name'].str.replace(" ", ",")

    context.log.info("Executing time delay...")
    time.sleep(3)

    # https://docs.dagster.io/overview/asset-materializations
    # https://github.com/dagster-io/dagster/issues/3234
    yield AssetMaterialization(
        asset_key="my_dataset",
        description="transformed dataframe",
        metadata_entries=[
            EventMetadataEntry.text(str(len(df)), "n_rows", "Number of rows seen in the dataframe"),
            EventMetadataEntry.text(str(df.shape), "shape", "The shape of the DataFrame."),
            EventMetadataEntry.md(df.dtypes.to_markdown(), "dtypes", "The dtypes within the DataFrame."),
            EventMetadataEntry.md(df.head().to_markdown(), "head", "A markdown preview of the first 5 rows."),
            EventMetadataEntry.md(df.tail().to_markdown(), "tail", "A markdown preview of the last 5 rows."),
        ],
    )
    yield Output(value=df, output_name="dataframe")


@pipeline
def main_pipeline():
    df = fetchCsv()
    transformName(df)


if __name__ == "__main__":
    run_config = {
        "solids": {
            "fetchCsv": {"inputs": {"url": {"value": "https://raw.githubusercontent.com/dagster-io/dagster/master/examples/docs_snippets/docs_snippets/intro_tutorial/cereal.csv"}}}
        }
    }
    results = execute_pipeline(main_pipeline, run_config=run_config)

    # https://docs.dagster.io/tutorial/testable
    df = results.result_for_solid("transformName").output_value("dataframe")

    print(df.head())

