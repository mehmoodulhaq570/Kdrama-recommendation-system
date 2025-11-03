import pandas as pd
import os
from pandas.api.types import is_datetime64_any_dtype

# File paths
dramalist_file = os.path.join(
    os.path.dirname(__file__), "dramalist_kdrama.xlsx"
)  # Now using Excel file
kdrama_file = os.path.join(os.path.dirname(__file__), "kdrama_dataset.csv")

# Read dramalist_kdrama as Excel, kdrama_dataset as CSV (all as strings)
df_dramalist = pd.read_excel(dramalist_file, dtype=str)
df_kdrama = pd.read_csv(kdrama_file, dtype=str)

# Column mapping from kdrama_dataset to dramalist format
column_mapping = {
    "Title": "title",
    "Also Known As": "alternate_names",
    "Description": "description",
    "Network": "publisher",
    "Genre": "genres",
    "Cast": "actors",
    "Release Dates": "date_published",
    "Poster": "url",  # Using Poster for url since dramalist has url field
    "Written By": "written_by",
    "Director": "director",
    "Episodes": "episodes",
    "Release Years": "release_years",
}

# Rename columns in kdrama_dataset to match dramalist format
df_kdrama = df_kdrama.rename(columns=column_mapping)

# Add missing columns with empty values to kdrama_dataset
missing_columns = [col for col in df_dramalist.columns if col not in df_kdrama.columns]
for col in missing_columns:
    df_kdrama[col] = ""

# Merge the two datasets based on the title column
combined_df = pd.merge(
    df_dramalist, df_kdrama, on="title", how="outer", suffixes=("_file1", "_file2")
)

# Fill missing values from file2 into file1 columns, only if the suffixed columns exist
for col in df_dramalist.columns:
    if col == "title":
        continue  # title is the merge key
    col_file1 = col + "_file1"
    col_file2 = col + "_file2"
    if col_file1 in combined_df.columns and col_file2 in combined_df.columns:
        combined_df[col] = combined_df[col_file1].fillna(combined_df[col_file2])
    elif col_file1 in combined_df.columns:
        combined_df[col] = combined_df[col_file1]
    elif col_file2 in combined_df.columns:
        combined_df[col] = combined_df[col_file2]

# Add extra columns from kdrama_dataset that are not in dramalist_kdrama
extra_cols = [col for col in df_kdrama.columns if col not in df_dramalist.columns]
for col in extra_cols:
    if col in combined_df.columns:
        continue
    if col in df_kdrama.columns:
        combined_df[col] = df_kdrama[col]

# Drop temporary columns created during merging
columns_to_drop = [
    col
    for col in combined_df.columns
    if col.endswith("_file1") or col.endswith("_file2")
]
combined_df.drop(columns=columns_to_drop, inplace=True)

# Reorder columns: dramalist columns first, then extra columns
final_columns = list(df_dramalist.columns) + [
    col for col in extra_cols if col in combined_df.columns
]
combined_df = combined_df[final_columns]

# Clean up date columns: remove time if present (keep only date part as string)
for col in combined_df.columns:
    if "date" in col.lower() or "published" in col.lower():
        # If column is datetime, convert to string without time
        if is_datetime64_any_dtype(combined_df[col]):
            combined_df[col] = combined_df[col].dt.strftime("%Y-%m-%d")
        # If string, remove time part if present
        else:
            combined_df[col] = (
                combined_df[col]
                .astype(str)
                .str.replace(r"\s*00:00:00(\.0+)?", "", regex=True)
            )

# Replace missing values and '-' with '_'
combined_df = combined_df.fillna("_").replace("-", "_")

# Save the combined dataset as CSV
output_combined_file = os.path.join(
    os.path.dirname(__file__), "combined_kdrama_dataset.csv"
)
combined_df.to_csv(output_combined_file, index=False, encoding="utf-8-sig")

# Save the combined dataset as Excel
output_combined_excel = os.path.join(
    os.path.dirname(__file__), "combined_kdrama_dataset.xlsx"
)
combined_df.to_excel(output_combined_excel, index=False)

print(f"Combined dataset saved to: {output_combined_file}")
print(f"Combined dataset also saved to: {output_combined_excel}")
print(f"Total rows: {len(combined_df)}")
print(f"Columns: {list(combined_df.columns)}")
