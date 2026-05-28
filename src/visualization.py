import matplotlib.pyplot as plt
import seaborn as sns

def plot_regimes(df, output_path):
    plt.figure(figsize=(12,5))
    
    sns.scatterplot(
        x=df['date'],      # lowercase
        y=df['close'],     # lowercase
        hue=df['Regime'],  # from your ML model
        palette='tab10',
        s=12
    )
    
    plt.title("Market Regime Classification")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend(title="Regime")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()