import pandas as pd

# Text columns that need whitespace cleaning
TEXT_COLUMNS = [
    "track_name",
    "artist_name",
    "genre",
    "country",
    "trend",
    "popularity_category",
    "longevity",
]

# Columns that should contain numbers
NUMERIC_COLUMNS = [
    "streams",
    "stream_change",
    "streams_7day",
    "pos",
    "days",
    "viral_score",
]

# Essential columns needed for analysis and Tableau visualisation
REQUIRED_COLUMNS = [
    "track_name",
    "artist_name",
    "streams",
    "genre",
    "country",
]


def load_data(input_path: str) -> pd.DataFrame:
    """Load the raw Spotify CSV file."""
    return pd.read_csv(input_path)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Make column names consistent and easier to use in Python/Tableau."""
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()        # remove spaces at the start/end
        .str.lower()        # make lowercase
        .str.replace(" ", "_")  # replace spaces with underscores
    )

    # Rename 7day because column names starting with numbers can be awkward
    df = df.rename(columns={"7day": "streams_7day"})

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows."""
    return df.drop_duplicates()


def clean_text_columns(df: pd.DataFrame, text_columns: list[str]) -> pd.DataFrame:
    """Clean text columns without turning missing values into the string 'nan'."""
    df = df.copy()

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].str.strip()

    return df


def coerce_numeric_columns(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    """Convert numeric columns from text/object format into real numbers."""
    df = df.copy()

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def drop_missing_required_rows(df: pd.DataFrame, required_columns: list[str]) -> pd.DataFrame:
    """Remove rows missing important values needed for analysis."""
    available_columns = [col for col in required_columns if col in df.columns]

    return df.dropna(subset=available_columns)


def remove_impossible_values(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows with values that do not make logical sense."""
    df = df.copy()

    # Streams cannot be negative
    if "streams" in df.columns:
        df = df[df["streams"] >= 0]

    # 7-day streams cannot be negative
    if "streams_7day" in df.columns:
        df = df[df["streams_7day"] >= 0]

    # Chart position should be greater than 0
    if "pos" in df.columns:
        df = df[df["pos"] > 0]

    # Number of days cannot be negative
    if "days" in df.columns:
        df = df[df["days"] >= 0]

    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Create extra columns that will make Tableau visualisations easier."""
    df = df.copy()

    # Categorise whether streams are rising, falling, or unchanged
    if "stream_change" in df.columns:
        df["stream_change_direction"] = df["stream_change"].apply(
            lambda x: "Increasing" if x > 0 else "Decreasing" if x < 0 else "No Change"
        )

    # Convert streams into millions for cleaner chart labels
    if "streams" in df.columns:
        df["streams_millions"] = df["streams"] / 1_000_000

    if "streams_7day" in df.columns:
        df["streams_7day_millions"] = df["streams_7day"] / 1_000_000

    # Create a combined artist-track label for Tableau tooltips and charts
    if "artist_name" in df.columns and "track_name" in df.columns:
        df["artist_track"] = df["artist_name"] + " - " + df["track_name"]

    return df


def sort_for_output(df: pd.DataFrame) -> pd.DataFrame:
    """Sort the final dataset so highest-streamed songs appear first."""
    if "streams" in df.columns:
        return df.sort_values(by="streams", ascending=False)

    return df


def clean_spotify_data(input_path: str, output_path: str) -> pd.DataFrame:
    """Run the complete cleaning process from raw CSV to cleaned CSV."""
    df = load_data(input_path)

    df = clean_column_names(df)
    df = remove_duplicates(df)
    df = clean_text_columns(df, TEXT_COLUMNS)
    df = coerce_numeric_columns(df, NUMERIC_COLUMNS)
    df = drop_missing_required_rows(df, REQUIRED_COLUMNS)
    df = remove_impossible_values(df)
    df = add_derived_columns(df)
    df = sort_for_output(df)

    # Save cleaned file for Tableau
    df.to_csv(output_path, index=False)

    return df


def main() -> None:
    """Main function that runs when the file is executed."""
    input_path = "spotify_global_trends.csv"
    output_path = "cleaned_spotify_global_trends.csv"

    df = clean_spotify_data(input_path, output_path)

    # Print a short summary so you know the script worked
    print("Cleaning complete.")
    print("Cleaned file saved as:", output_path)
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print(df.head())
    print(df.info())


if __name__ == "__main__":
    main()