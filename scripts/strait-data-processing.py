import os
import re
import pandas as pd


PROJECTS_DIR =  "/u/23/chrens1/unix/Ja/Aalto/papers/SRGM-maturity/EASE2026/Data/STRAIT"

def create_strait_summaries(PROJECTS_DIR):

    pattern = re.compile(r"batchAnalysisReport-(\d+)-(.+)\.csv$")

    for project in os.listdir(PROJECTS_DIR):
        print(f"Processing STRAIT results for project: {project}")
        project_path = os.path.join(PROJECTS_DIR, project)
        if not os.path.isdir(project_path):
            continue

        merged_rows = []

        for fname in os.listdir(project_path):
            match = pattern.match(fname)
            if not match:
                continue

            # number = match.group(1)
            version = match.group(2)

            csv_path = os.path.join(project_path, fname)
            try:
                df = pd.read_csv(csv_path)
            except Exception:
                continue

            # # Remove old project name column if it exists
            # for col in df.columns:
            #     if col.lower().replace(" ", "") in ("projectsname", "projectname"):
            #         df = df.drop(columns=[col])
            #         break


            df.insert(0, "Project", f"{project}-{version}")

            merged_rows.append(df)


        if not merged_rows:
            continue


        final_df = pd.concat(merged_rows, ignore_index=True)

        final_df.sort_values(by="Project", inplace=True)


        output_path = os.path.join(PROJECTS_DIR, f"STRAIT-{project}-Summary.csv")
        final_df.to_csv(output_path, index=False)

        print(f"Created: {output_path}")

if __name__ == '__main__':
    create_strait_summaries(PROJECTS_DIR)