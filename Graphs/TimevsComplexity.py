import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set text size
plt.rc('font', size=24)

# Example usage
filename = "llmdata.csv"
df = pd.read_csv(filename)

# Ensure we only use the first 90 values of the dataset
df = df.head(90)

# Reassign misclassified class type 5 as class 3
df.loc[df['Type'] == 5, 'Type'] = 3

# Calculate total time for translation and configuration for each requirement
df['total_duration_time'] = df['total_duration_translation'] + df['total_duration_configuration']
df['total_len'] = df['translation_len'] + df['configuration_len']
df['eval_count_total'] = df['eval_count_translation'] + df['eval_count_configuration']
df['eval_duration_total'] = df['eval_duration_translation'] + df['eval_duration_configuration']

# Normalize translation lengths and evaluation counts
df['normalized_translation_len'] = (df['translation_len'] - df['translation_len'].min()) / (df['translation_len'].max() - df['translation_len'].min())
df['normalized_translation_eval_count'] = (df['eval_count_translation'] - df['eval_count_translation'].min()) / (df['eval_count_translation'].max() - df['eval_count_translation'].min())
df['normalized_configuration_len'] = (df['configuration_len'] - df['configuration_len'].min()) / (df['configuration_len'].max() - df['configuration_len'].min())
df['normalized_configuration_eval_count'] = (df['eval_count_configuration'] - df['eval_count_configuration'].min()) / (df['eval_count_configuration'].max() - df['eval_count_configuration'].min())
df['normalized_total_len'] = (df['total_len'] - df['total_len'].min()) / (df['total_len'].max() - df['total_len'].min())
df['normalized_total_eval_count'] = (df['eval_count_total'] - df['eval_count_total'].min()) / (df['eval_count_total'].max() - df['eval_count_total'].min())

# Calculate composite score
df['composite_translation_score'] = (df['normalized_translation_len'] + df['normalized_translation_eval_count']) / 2
df['composite_configuration_score'] = (df['normalized_configuration_len'] + df['normalized_configuration_eval_count']) / 2
df['composite_total_score'] = (df['normalized_total_len'] + df['normalized_total_eval_count']) / 2

# Sort the DataFrame based on 'total_duration_time'
df = df.sort_values(by='total_duration_time')

# Define the categories
categories = df['Type'].unique()

# Ensure we only have 4 categories (CP, RP, ACL, TN)
categories = categories[categories != 0]  # Remove category 0 if present
if len(categories) > 4:
    categories = categories[:4]  # Keep only the first 4 categories

# Create a dictionary to map category numbers to names
category_names = {1: 'CP', 2: 'RP', 3: 'ACL', 4: 'TN'}

# Define colors for each category
colors = {1: 'blue', 2: 'orange', 3: 'red', 4: 'green'}

# Create scatter plot with Seaborn
plt.figure(figsize=(10, 6))
for category in categories:
    df_category = df[df['Type'] == category]
    sns.scatterplot(data=df_category, x='composite_total_score', y='total_duration_time', color=colors[category], alpha=0.8, label=f'{category_names[category]}')

# Set labels and title
plt.xlabel('Composite Score')
plt.ylabel('Total Time (seconds)')

# Show plot
plt.legend(loc='lower right', title='Type', fontsize=18)
plt.tight_layout()
plt.show()

