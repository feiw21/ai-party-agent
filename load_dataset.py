from datasets import load_dataset

# Load the dataset
dataset = load_dataset("agents-course/unit3-invitees")

# Convert to pandas DataFrame for easier manipulation
df = dataset['train'].to_pandas()

# Now you can use the data directly
print("\nDataset Preview:")
print(df.head())

# Save to CSV for local storage (optional)
df.to_csv('invitees_data.csv', index=False)
print("\nDataset has been saved to 'invitees_data.csv'") 