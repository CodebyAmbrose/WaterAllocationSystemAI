import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization, Bidirectional
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from datetime import datetime

# Create models directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

def add_engineered_features(df):
    """Add engineered features to improve model performance"""
    # Time-based features
    df['hour'] = df['date'].dt.hour
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_year']/365)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_year']/365)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
    df['week_sin'] = np.sin(2 * np.pi * df['week_of_year']/52)
    df['week_cos'] = np.cos(2 * np.pi * df['week_of_year']/52)
    
    # Rolling statistics by borough
    for window in [7, 14, 30]:
        df[f'rolling_mean_{window}d'] = df.groupby('borough')['consumption_(hcf)'].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean())
        df[f'rolling_std_{window}d'] = df.groupby('borough')['consumption_(hcf)'].transform(
            lambda x: x.rolling(window=window, min_periods=1).std())
        df[f'rolling_max_{window}d'] = df.groupby('borough')['consumption_(hcf)'].transform(
            lambda x: x.rolling(window=window, min_periods=1).max())
        df[f'rolling_min_{window}d'] = df.groupby('borough')['consumption_(hcf)'].transform(
            lambda x: x.rolling(window=window, min_periods=1).min())

    # Lag features
    for lag in [1, 7, 14]:
        df[f'consumption_lag_{lag}'] = df.groupby('borough')['consumption_(hcf)'].shift(lag)
    
    # Fill NaN values with appropriate statistics
    for col in df.columns:
        if df[col].isnull().any():
            if 'lag' in col or 'rolling' in col:
                df[col].fillna(df[col].mean(), inplace=True)
    
    return df

def load_and_preprocess_data(file_path):
    """Load and preprocess the data"""
    print("Loading and preprocessing data...")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Encode borough
    le = LabelEncoder()
    df['borough_encoded'] = le.fit_transform(df['borough'])
    
    # Add engineered features
    df = add_engineered_features(df)
    
    # Save the label encoder for future use
    joblib.dump(le, 'models/borough_encoder.joblib')
    
    print(f"\nDataset shape: {df.shape}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Number of boroughs: {len(df['borough'].unique())}")
    
    # Analyze feature correlations
    plt.figure(figsize=(12, 10))
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    sns.heatmap(df[numeric_cols].corr(), annot=False, cmap='coolwarm')
    plt.title('Feature Correlations')
    plt.tight_layout()
    plt.savefig('models/feature_correlations.png')
    plt.close()
    
    return df

def create_sequences(data, seq_length):
    """Create sequences for LSTM with overlap"""
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length), :-1])
        y.append(data[i + seq_length, -1])
    return np.array(X), np.array(y)

def build_model(sequence_length, n_features):
    """Build an optimized LSTM model"""
    model = Sequential([
        # First LSTM layer with more units and bidirectional
        Bidirectional(LSTM(128, activation='tanh', return_sequences=True, 
                     input_shape=(sequence_length, n_features))),
        BatchNormalization(),
        Dropout(0.3),
        
        # Second LSTM layer
        LSTM(64, activation='tanh'),
        BatchNormalization(),
        Dropout(0.3),
        
        # Dense layers
        Dense(32, activation='relu'),
        BatchNormalization(),
        Dense(1)
    ])
    
    # Use Adam optimizer with lower learning rate
    optimizer = Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='huber')  # Huber loss for robustness
    
    return model

def evaluate_model(model, X_test, y_test, scaler, features):
    """Evaluate model performance"""
    # Make predictions
    y_pred = model.predict(X_test, verbose=0)
    
    # Inverse transform predictions and actual values
    y_test_reshaped = np.zeros((len(y_test), len(features)))
    y_test_reshaped[:, -1] = y_test
    y_pred_reshaped = np.zeros((len(y_pred), len(features)))
    y_pred_reshaped[:, -1] = y_pred.flatten()
    
    y_test_actual = scaler.inverse_transform(y_test_reshaped)[:, -1]
    y_pred_actual = scaler.inverse_transform(y_pred_reshaped)[:, -1]
    
    # Calculate metrics
    mse = mean_squared_error(y_test_actual, y_pred_actual)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test_actual, y_pred_actual)
    r2 = r2_score(y_test_actual, y_pred_actual)
    mape = np.mean(np.abs((y_test_actual - y_pred_actual) / y_test_actual)) * 100
    
    print("\nModel Performance Metrics:")
    print(f"Root Mean Squared Error: {rmse:.2f} HCF")
    print(f"Mean Absolute Error: {mae:.2f} HCF")
    print(f"R² Score: {r2:.4f}")
    print(f"Mean Absolute Percentage Error: {mape:.2f}%")
    
    # Plot actual vs predicted values with confidence intervals
    plt.figure(figsize=(12, 8))
    
    # Scatter plot
    plt.scatter(y_test_actual, y_pred_actual, alpha=0.5, label='Predictions')
    
    # Perfect prediction line
    plt.plot([y_test_actual.min(), y_test_actual.max()],
             [y_test_actual.min(), y_test_actual.max()],
             'r--', lw=2, label='Perfect Prediction')
    
    # Add confidence intervals
    z = np.polyfit(y_test_actual, y_pred_actual, 1)
    p = np.poly1d(z)
    plt.plot(y_test_actual, p(y_test_actual), "b-", alpha=0.5, label='Trend')
    
    plt.xlabel('Actual Consumption (HCF)')
    plt.ylabel('Predicted Consumption (HCF)')
    plt.title('Test Set: Actual vs Predicted Water Consumption')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('models/prediction_performance.png')
    plt.close()
    
    # Save sample predictions with more detail
    sample_size = min(20, len(y_test_actual))
    sample_indices = np.random.choice(len(y_test_actual), sample_size, replace=False)
    sample_predictions = pd.DataFrame({
        'Actual': y_test_actual[sample_indices],
        'Predicted': y_pred_actual[sample_indices],
        'Absolute_Error': np.abs(y_test_actual[sample_indices] - y_pred_actual[sample_indices]),
        'Percentage_Error': np.abs((y_test_actual[sample_indices] - y_pred_actual[sample_indices]) / y_test_actual[sample_indices]) * 100
    })
    
    print("\nSample Predictions:")
    print(sample_predictions.round(2))
    
    # Save detailed metrics to file
    with open('models/model_metrics.txt', 'w') as f:
        f.write("Model Performance Metrics:\n")
        f.write(f"Root Mean Squared Error: {rmse:.2f} HCF\n")
        f.write(f"Mean Absolute Error: {mae:.2f} HCF\n")
        f.write(f"R² Score: {r2:.4f}\n")
        f.write(f"Mean Absolute Percentage Error: {mape:.2f}%\n\n")
        f.write("Distribution of Errors:\n")
        f.write(f"90th percentile error: {np.percentile(np.abs(y_test_actual - y_pred_actual), 90):.2f} HCF\n")
        f.write(f"95th percentile error: {np.percentile(np.abs(y_test_actual - y_pred_actual), 95):.2f} HCF\n")
        f.write("\nSample Predictions:\n")
        f.write(sample_predictions.round(2).to_string())
    
    return rmse, mae, r2, mape

def train_model():
    """Train the LSTM model"""
    # Load and preprocess data
    df = load_and_preprocess_data('high_quality_water_consumption.csv')
    
    # Add time-based features
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day_of_month'] = df['date'].dt.day
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_year'] = df['date'].dt.dayofyear
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    # Prepare feature columns in the correct order
    feature_columns = [
        'year', 'month', 'day_of_month', 'day_of_week', 'day_of_year', 'week_of_year',
        'borough_encoded', 'hour', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'week_sin', 'week_cos'
    ]
    
    # Add rolling statistics and lag features to columns list
    for window in [7, 14, 30]:
        feature_columns.extend([
            f'rolling_mean_{window}d', f'rolling_std_{window}d',
            f'rolling_max_{window}d', f'rolling_min_{window}d'
        ])
    
    for lag in [1, 7, 14]:
        feature_columns.append(f'consumption_lag_{lag}')
    
    # Add target variable as the last column
    feature_columns.append('consumption_(hcf)')
    
    # Select features and target
    data = df[feature_columns].values
    
    # Scale the features
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Save the scaler for future use
    joblib.dump(scaler, 'models/feature_scaler.joblib')
    
    # Create sequences
    sequence_length = 14
    X, y = create_sequences(scaled_data, sequence_length)
    print(f"\nTotal sequences created: {len(X)}")
    print(f"Sequence shape: {X.shape}")
    
    # Split into training and test sets (80-20 split)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Build and compile the model
    n_features = X.shape[2]
    model = build_model(sequence_length, n_features)
    
    # Build the model by passing a dummy batch
    dummy_batch = np.zeros((1, sequence_length, n_features))
    model(dummy_batch)
    
    print("\nModel Architecture:")
    model.summary()
    
    # Save model summary to file
    with open('models/model_summary.txt', 'w') as f:
        model.summary(print_fn=lambda x: f.write(x + '\n'))
    
    # Define callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.0001),
        ModelCheckpoint('models/best_model.h5', monitor='val_loss', save_best_only=True)
    ]
    
    # Train the model
    print("\nTraining the model...")
    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.2,
        callbacks=callbacks,
        verbose=1
    )
    
    # Plot training history
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Training History')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig('models/training_history.png')
    plt.close()
    
    # Evaluate the model
    print("\nEvaluating model performance...")
    evaluate_model(model, X_test, y_test, scaler, feature_columns)
    
    # Save the final model
    model.save('models/water_consumption_model.h5')
    print("\nTraining completed. Model and artifacts saved in 'models' directory.")

if __name__ == "__main__":
    train_model() 