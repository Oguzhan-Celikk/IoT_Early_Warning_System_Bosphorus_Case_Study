# IoT Early Warning System: Bosphorus Case Study

This project implements a Water Level Prediction System using Machine Learning and IoT sensor data. It includes a training pipeline, a FastAPI backend, and a web interface.

## Project Structure

```
├── app/                        # --- WEB / API SIDE ---
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api.py                  # API Endpoints
│   ├── schemas.py              # Pydantic models
│   └── templates/              # Static files (HTML, CSS, JS)
│       ├── index.html
│       ├── style.css
│       └── script.js
│
├── ml_core/                    # --- MODEL TRAINING SIDE ---
│   ├── __init__.py
│   ├── train.py                # Script to train models
│   ├── preprocessing.py        # Data cleaning and preparation functions
│   └── inference.py            # Model loading and prediction logic
│
├── saved_models/               # --- SAVED MODELS ---
│   ├── model.pkl               # Trained regression model
│   ├── turbidity_classifier.pkl# Trained classification model
│   └── scaler.pkl              # Data scaler
│
├── data/                       # --- DATASETS ---
│   ├── water-level_turbidity-high.csv
│   ├── water-level_turbidity-medium.csv
│   └── water-level_turbidity-low.csv
│
├── requirements.txt            # Dependencies
└── README.md
```

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Train Models (Optional):**
    If you need to retrain the models:
    ```bash
    python ml_core/train.py
    ```
    This will save the trained models to `saved_models/`.

3.  **Run the Application:**
    ```bash
    python -m app.main
    ```
    *Note: If you are on Windows and `python` doesn't work, try using `py` instead:*
    ```bash
    py -m app.main
    ```

    Or directly with uvicorn:
    ```bash
    uvicorn app.main:app --reload
    ```

4.  **Access the Interface:**
    Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API Endpoints

*   `POST /predict`: Predict water level and turbidity status.
*   `GET /datasets/{type}`: Get sample data (high, medium, low).
*   `GET /`: Serve the web interface.

## Models

*   **Turbidity Classifier:** Random Forest Classifier to detect turbidity status (Low, Medium, High).
*   **Water Level Regressor:** Random Forest Regressor (by default) to predict water level.
