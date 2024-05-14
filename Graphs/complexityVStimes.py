import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Create subplots
fig, axs = plt.subplots(2, 4, figsize=(20, 10))

# Scatter plots
for i, category in enumerate(categories):
    df_category = df[df['Type'] == category]
    row = i // 4
    col = i % 4
    ax = axs[row, col]
    if category == 3:
        misclassified_points = df_category[df_category['Type'] == 5]
        ax.scatter(misclassified_points['composite_total_score'], misclassified_points['eval_duration_total'], color='red', alpha=0.8, label='Misclassified')
        df_category = df_category[df_category['Type'] != 5]  
    ax.scatter(df_category['composite_total_score'], df_category['total_duration_time'], color='skyblue', alpha=0.8)
    ax.set_xlabel('Complexity')
    ax.set_ylabel('Total Total Time (seconds)')
    ax.set_title(f'Total Time Distribution - {category_names[category]}')
    ax.grid()

# Violin plots
for i, category in enumerate(categories):
    df_category = df[df['Type'] == category]
    row = i // 4
    col = i % 4
    ax = axs[row + 1, col]
    sns.violinplot(y='total_duration_translation', data=df_category, palette='muted', ax=ax)
    ax.set_ylabel('Total Time (seconds)')
    ax.grid()

plt.tight_layout()
plt.show()
