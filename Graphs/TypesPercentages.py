import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set global font size
mpl.rcParams.update({'font.size': 28})

# Define the prediction counts
df_pred = pd.DataFrame({
    'Prediction': ['CP', 'RP', 'ACL', 'TN', 'All'], 
    'Correct (Percentage)': [100, 100, 65, 100, 92.2],
    'Incorrect (Percentage)': [0, 0, 35, 0, 7.8]
})

# Create the bar plot
plt.figure(figsize=(10, 6))  # Set the figure size

# Plot the blue bars for correct predictions
ax = sns.barplot(x='Prediction', y='Correct (Percentage)', data=df_pred, color='blue')

# Plot the red bars for incorrect predictions starting from the top of the blue bars
sns.barplot(x='Prediction', y='Incorrect (Percentage)', data=df_pred, color='red', ax=ax,
            bottom=df_pred['Correct (Percentage)'])


# Add incorrect percentage on top of correct percentage
for i, correct_percent in enumerate(df_pred['Correct (Percentage)']):
    if correct_percent != 100 and correct_percent != 0:  # Display percentage if different from 0 or 100
        incorrect_percent = df_pred.loc[i, 'Incorrect (Percentage)']
        ax.text(i, correct_percent/2, f"{correct_percent}%", ha='center', va='center', color='white', fontsize=16, fontweight='bold')
        ax.text(i, correct_percent + incorrect_percent/2, f"{incorrect_percent}%", ha='center', va='center', color='white', fontsize=16, fontweight='bold')

# Set tick labels in bold
plt.xticks(fontweight='bold')

# Set the axis labels
plt.xlabel('Type of requirement')
plt.ylabel('Accuracy (%)')

# Plot the graph
plt.show()

