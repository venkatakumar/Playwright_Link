import pandas as pd

# Read the CSV
df = pd.read_csv('output/linkedin_posts_with_urls_fixed.csv')

print(f"Columns: {list(df.columns)}")
print()
print("Data analysis:")
print(f"Total rows: {len(df)}")
print()

for col in df.columns:
    if len(df) > 0:
        value = df[col].iloc[0]
        print(f"{col}: '{value}'")
    else:
        print(f"{col}: N/A")

print()
print("Issues found:")
print(f"- Empty author names: {df['author_name'].isna().sum()}")
print(f"- Empty author titles: {df['author_title'].isna().sum()}")  
print(f"- Empty post dates: {df['post_date'].isna().sum()}")
print(f"- Image files column present: {'image_files' in df.columns}")
