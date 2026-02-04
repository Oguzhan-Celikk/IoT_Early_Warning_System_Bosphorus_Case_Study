import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.svm import SVR
from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import os
import sys

# Add the project root to sys.path to allow imports from ml_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml_core.preprocessing import load_data, clean_and_tag_data, prepare_master_dataset

# Visualization Functions
def plot_correlation_heatmap(master_df):
    print("Generating Correlation Heatmap...")
    plt.figure(figsize=(10, 8))
    numeric_df = master_df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.show()

def plot_class_balance(counts_data):
    print("Generating Class Balance Chart...")
    plt.figure(figsize=(8, 6))
    labels = list(counts_data.keys())
    before_counts = [x['before'] for x in counts_data.values()]
    after_counts = [x['after'] for x in counts_data.values()]
    x = np.arange(len(labels))
    width = 0.35
    plt.bar(x - width/2, before_counts, width, label='Before Balancing', color='skyblue')
    plt.bar(x + width/2, after_counts, width, label='After Balancing', color='salmon')
    plt.ylabel('Number of Samples')
    plt.title('Class Balance: Before vs After Sampling')
    plt.xticks(x, labels)
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_feature_distribution(master_df, X_scaled, features_list):
    print("Generating Feature Distribution Histogram...")
    
    # Prepare the data
    raw_ir = master_df['ir_value']
    ir_index = features_list.index('ir_value')
    scaled_ir = X_scaled[:, ir_index]

    # Create side-by-side plot areas (1 row, 2 columns)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 1st Chart: Raw Data
    sns.histplot(raw_ir, bins=30, kde=True, color='#1f77b4', ax=axes[0])
    axes[0].set_title('BEFORE: Raw IR Value Distribution', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Raw Value (0 - 4095)', fontsize=10)
    axes[0].set_ylabel('Frequency', fontsize=10)
    axes[0].grid(True, linestyle='--', alpha=0.5)

    # 2nd Chart: Scaled Data
    sns.histplot(scaled_ir, bins=30, kde=True, color='#2ca02c', ax=axes[1])
    axes[1].set_title('AFTER: MinMax Scaled IR Value', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Scaled Value (0.0 - 1.0)', fontsize=10)
    axes[1].set_ylabel('Frequency', fontsize=10)
    axes[1].grid(True, linestyle='--', alpha=0.5)

    # Title and Layout
    plt.suptitle('Effect of Normalization on LiDAR Sensor Data', fontsize=16)
    plt.tight_layout()
    
    # Save and Show
    plt.savefig('distribution_comparison.png', dpi=300)
    plt.show()
    print("Graph saved as 'distribution_comparison.png'")

# Model Development
def train_models(X_train, X_test, y_train, y_test, X_class_train, X_class_test, y_class_train, y_class_test):
    """Trains and evaluates models with requested visualizations."""
    
    # Ensure saved_models directory exists
    if not os.path.exists('saved_models'):
        os.makedirs('saved_models')

    # A. Auxiliary Water Turbidity Classifier
    print("\nTraining Turbidity Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_class_train, y_class_train)
    
    y_pred_class = clf.predict(X_class_test)
    acc = accuracy_score(y_class_test, y_pred_class)
    print(f"Turbidity Classifier Accuracy: {acc:.4f}")
    
    # Confusion Matrix Chart
    print("Displaying Confusion Matrix...")
    cm = confusion_matrix(y_class_test, y_pred_class, labels=clf.classes_)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=clf.classes_)
    disp.plot(cmap='Blues')
    plt.title(f'Confusion Matrix (Accuracy: {acc:.2f})')
    plt.show()
    
    joblib.dump(clf, 'saved_models/turbidity_classifier.pkl')
    print("Saved saved_models/turbidity_classifier.pkl")

    # B. Water Level Regressors
    print("\nTraining Water Level Regressors...")
    regressors = {
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=20, random_state=42),
        "SVR": SVR(),
        "XGBoost": XGBRegressor(objective='reg:squarederror', random_state=42),
        "MLP Regressor": MLPRegressor(random_state=42, max_iter=2000)
    }
    
    results = {}
    best_model_name = ""
    best_score = -float('inf') 
    best_model = None
    
    for name, model in regressors.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {"MSE": mse, "RMSE": rmse, "R2": r2}
        print(f"  MSE: {mse:.4f}, RMSE: {rmse:.4f}, R2: {r2:.4f}")

        # Scatter Plot (Only for Random Forest) Chart
        if name == "Random Forest":
            print("Displaying Random Forest Scatter Plot...")
            plt.figure(figsize=(8, 6))
            plt.scatter(y_test, y_pred, alpha=0.6, color='b')
            # Plot the perfect prediction line (y=x)
            min_val = min(y_test.min(), y_pred.min())
            max_val = max(y_test.max(), y_pred.max())
            plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
            plt.xlabel('Actual Water Level')
            plt.ylabel('Predicted Water Level')
            plt.title('Random Forest: Predicted vs Actual')
            plt.legend()
            plt.grid(True)
            plt.show()
        
        if r2 > best_score:
            best_score = r2
            best_model_name = name
            best_model = model

    # Bar Chart Comparing R2 Scores
    print("Displaying Model Comparison Chart...")
    model_names = list(results.keys())
    r2_values = [results[m]['R2'] for m in model_names]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(model_names, r2_values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.xlabel('Models')
    plt.ylabel('R2 Score')
    plt.title('Model Performance Comparison (R2 Score)')
    plt.ylim(0, 1.1) # Assuming R2 is positive, cap slightly above 1
    
    # Add text labels on bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, round(yval, 3), ha='center', va='bottom')
        
    plt.show()
            
    print(f"\nBest Regressor: {best_model_name} with R2: {best_score:.4f}")
    joblib.dump(best_model, 'saved_models/model.pkl') # Renamed to model.pkl as per structure
    print("Saved saved_models/model.pkl")
    
    return results

def main():
    # 1. Load Data
    df_high, df_medium, df_low = load_data(data_dir='data')
    if df_high is None: return

    # Capture "Before" Counts
    counts_data = {
        'High': {'before': len(df_high)},
        'Medium': {'before': len(df_medium)},
        'Low': {'before': len(df_low)}
    }

    # 2. Process
    df_high = clean_and_tag_data(df_high, 'High')
    df_medium = clean_and_tag_data(df_medium, 'Medium')
    df_low = clean_and_tag_data(df_low, 'Low')

    # 3. Prepare Master (Balancing & Merge)
    master_df = prepare_master_dataset(df_high, df_medium, df_low)
    
    # Capture "After" Counts
    after_counts = master_df['turbidity_category'].value_counts()
    counts_data['High']['after'] = after_counts.get('High', 0)
    counts_data['Medium']['after'] = after_counts.get('Medium', 0)
    counts_data['Low']['after'] = after_counts.get('Low', 0)

    # Visualizations
    plot_class_balance(counts_data)
    plot_correlation_heatmap(master_df)
    
    # 4. Feature Selection & Scaling
    features_all = ['ir_value', 'us_value', 'acc_x', 'acc_y', 'acc_z', 'gyr_x', 'gyr_y', 'gyr_z']
    target = 'water_level'
    
    X = master_df[features_all]
    y = master_df[target]
    y_class = master_df['turbidity_category']
    
    # Scaling
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)
    
    plot_feature_distribution(master_df, X_scaled, features_all)
    
    # Save scaler
    if not os.path.exists('saved_models'):
        os.makedirs('saved_models')
    joblib.dump(scaler, 'saved_models/scaler.pkl')
    print("Saved saved_models/scaler.pkl")
    
    # Create separate datasets
    X_class = X_scaled 
    X_reg = X_scaled[:, 1:] 
    
    # Train/Test Split
    X_reg_train, X_reg_test, X_class_train, X_class_test, y_train, y_test, y_class_train, y_class_test = train_test_split(
        X_reg, X_class, y, y_class, test_size=0.2, random_state=42
    )
    
    # Train
    train_models(X_reg_train, X_reg_test, y_train, y_test, X_class_train, X_class_test, y_class_train, y_class_test)

if __name__ == "__main__":
    main()
