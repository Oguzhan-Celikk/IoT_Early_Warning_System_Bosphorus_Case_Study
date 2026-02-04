import joblib
import numpy as np
import os

class Predictor:
    def __init__(self, model_dir='saved_models'):
        self.model_dir = model_dir
        self.model = None
        self.turbidity_classifier = None
        self.scaler = None
        self.load_models()

    def load_models(self):
        print("Loading models...")
        try:
            # Load the main regression model (renamed to model.pkl)
            self.model = joblib.load(os.path.join(self.model_dir, 'model.pkl'))
            self.turbidity_classifier = joblib.load(os.path.join(self.model_dir, 'turbidity_classifier.pkl'))
            self.scaler = joblib.load(os.path.join(self.model_dir, 'scaler.pkl'))
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Error loading models: {e}")
            # We don't raise here to allow app to start, but predict will fail
            
    def predict(self, features):
        """
        Args:
            features: list or np.array of shape (8,) -> [ir, us, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z]
        Returns:
            dict: {water_level, turbidity_status}
        """
        if not self.scaler or not self.model or not self.turbidity_classifier:
            raise ValueError("Models not loaded")

        input_array = np.array(features).reshape(1, -1)
        scaled_input = self.scaler.transform(input_array)
        
        # Predict Turbidity
        turbidity_pred = self.turbidity_classifier.predict(scaled_input)[0]
        
        # Predict Water Level (exclude IR)
        # Note: The regressor was trained on the same scaled features but EXCLUDING the first one (IR value)
        water_level_input = scaled_input[:, 1:]
        water_level_pred = self.model.predict(water_level_input)[0]
        
        return {
            "predicted_water_level": float(water_level_pred),
            "detected_turbidity_status": str(turbidity_pred)
        }
