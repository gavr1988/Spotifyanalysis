import tempfile
import unittest
from pathlib import Path

import pandas as pd

import run


class TestSpotifyCleaningPipeline(unittest.TestCase):
    def test_clean_column_names_normalizes_labels(self):
        df = pd.DataFrame(columns=[" Track Name ", "7day", "Stream Change"])

        cleaned = run.clean_column_names(df)

        self.assertEqual(list(cleaned.columns), ["track_name", "streams_7day", "stream_change"])

    def test_clean_text_columns_strips_whitespace(self):
        df = pd.DataFrame(
            {
                "track_name": ["  SWIM  "],
                "artist_name": [" BTS "],
            }
        )

        cleaned = run.clean_text_columns(df, ["track_name", "artist_name"])

        self.assertEqual(cleaned.loc[0, "track_name"], "SWIM")
        self.assertEqual(cleaned.loc[0, "artist_name"], "BTS")

    def test_coerce_numeric_columns_converts_invalid_values(self):
        df = pd.DataFrame(
            {
                "streams": ["1000", "bad"],
                "pos": ["1", "2"],
            }
        )

        cleaned = run.coerce_numeric_columns(df, ["streams", "pos"])

        self.assertEqual(cleaned["streams"].dtype.kind, "f")
        self.assertTrue(pd.isna(cleaned.loc[1, "streams"]))
        self.assertEqual(cleaned.loc[0, "pos"], 1)

    def test_add_derived_columns_creates_helper_fields(self):
        df = pd.DataFrame(
            {
                "artist_name": ["BTS"],
                "track_name": ["SWIM"],
                "stream_change": [12],
                "streams": [2_000_000],
                "streams_7day": [1_500_000],
            }
        )

        cleaned = run.add_derived_columns(df)

        self.assertEqual(cleaned.loc[0, "stream_change_direction"], "Increasing")
        self.assertEqual(cleaned.loc[0, "streams_millions"], 2.0)
        self.assertEqual(cleaned.loc[0, "streams_7day_millions"], 1.5)
        self.assertEqual(cleaned.loc[0, "artist_track"], "BTS - SWIM")

    def test_clean_spotify_data_writes_expected_output(self):
        raw_csv = """ Track Name , Artist Name , Streams , Stream Change , 7day , Genre , Country , Pos , Days , Viral Score , Trend , Popularity Category , Longevity
        SWIM , BTS , 1000000 , 25 , 500000 , Pop , US , 1 , 10 , 90 , Rising , High , Long
        SWIM , BTS , 1000000 , 25 , 500000 , Pop , US , 1 , 10 , 90 , Rising , High , Long
        Bad Row , Unknown , -5 , -1 , -2 , Pop , US , 0 , -1 , 10 , Falling , Low , Short
        """

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            input_path = temp_dir_path / "input.csv"
            output_path = temp_dir_path / "output.csv"
            input_path.write_text(raw_csv)

            cleaned = run.clean_spotify_data(str(input_path), str(output_path))

            self.assertTrue(output_path.exists())
            self.assertEqual(len(cleaned), 1)
            self.assertEqual(cleaned.loc[0, "track_name"], "SWIM")
            self.assertEqual(cleaned.loc[0, "artist_track"], "BTS - SWIM")
            self.assertEqual(cleaned.loc[0, "stream_change_direction"], "Increasing")
            self.assertAlmostEqual(cleaned.loc[0, "streams_millions"], 1.0)

            written = pd.read_csv(output_path)
            self.assertEqual(len(written), 1)
            self.assertEqual(written.loc[0, "artist_track"], "BTS - SWIM")


if __name__ == "__main__":
    unittest.main()
