import pandas as pd
import sys
import os

STRAIT_FOLDER = ""
SOURCEMETER_FOLDER = ""
SONAR_FOLDER = ""


def remove_prefix_from_project(csv_path, prefix_to_remove):

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    df["Project"] = df["Project"].apply(
        lambda x: x[len(prefix_to_remove):] if isinstance(x, str) and x.startswith(prefix_to_remove) else x
    )

    df.to_csv(csv_path, index=False)
    print(f"Updated CSV saved: {csv_path}")


def merge_strait_sonar_sourcemeter(output_dir, strait_csv, sonar_csv, sourcemeter_csv, duration_csv):

    df_strait = pd.read_csv(strait_csv)
    df_sonar = pd.read_csv(sonar_csv)
    df_sourcemeter = pd.read_csv(sourcemeter_csv)
    df_duration = pd.read_csv(duration_csv)

    df_sonar = df_sonar.rename(columns={"project_key": "Project"})

    merged = (df_strait.merge(df_duration, on="Project", how="inner")
                       .merge(df_sourcemeter, on="Project", how="inner")
                       .merge(df_sonar, on="Project", how="inner"))


    merged.sort_values(by="Project", inplace=True)

    output_dir = os.path.dirname(os.path.abspath(output_dir))
    output_file = os.path.join(output_dir, "merged_strait_sonar_sourcemeter.csv")

    merged.to_csv(output_file, index=False)

    print(f"Merged CSV created:\n{output_file}")
    return output_file


# if __name__ == "__main__":
#     # strait_csv = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/STRAIT/STRAIT-httpie-cli-Summary.csv"
#     # sonar_csv ="/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/Sonarqube/sonarqube_metrics.csv"
#     # sourcemeter_csv = "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/Results/FilteredResults/Python/cli-Summary.csv"
#     # duration_csv="/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/cli-duration.csv"
#
#     # merge_strait_sonar_sourcemeter(output_dir, strait_csv, sonar_csv, sourcemeter_csv, duration_csv)