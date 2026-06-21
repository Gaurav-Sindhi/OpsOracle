import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib
from typing import Dict, List, Tuple
from datetime import datetime
from loguru import logger
from config import Config
import os

class AnomalyDetector:
    """Detect anomalies in system metrics using ML"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        self._load_or_create_model()
        logger.info("✅ AnomalyDetector initialized")
    
    def _load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(Config.MODEL_PATH):
                self.model = joblib.load(Config.MODEL_PATH)
                self.scaler = joblib.load(Config.SCALER_PATH)
                self.is_trained = True
                logger.info("📦 Loaded existing anomaly model")
            else:
                # Create new model
                self.model = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )
                self.scaler = StandardScaler()
                logger.info("🆕 Created new anomaly model")
        except Exception as e:
            logger.warning(f"⚠️  Could not load model: {str(e)}")
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.scaler = StandardScaler()
    
    def train(self, data: pd.DataFrame) -> Dict:
        """Train anomaly detector on historical data"""
        try:
            # Prepare data
            X = data.select_dtypes(include=[np.number]).values
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled)
            
            # Save model
            os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, Config.MODEL_PATH)
            joblib.dump(self.scaler, Config.SCALER_PATH)
            
            self.is_trained = True
            
            result = {
                'status': 'success',
                'message': f'Model trained on {len(data)} samples',
                'timestamp': datetime.now().isoformat()
            }
            logger.info(f"✅ Anomaly detector trained on {len(data)} samples")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error training model: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def predict(self, metrics: Dict) -> Dict:
        """Predict if metrics indicate anomaly"""
        try:
            if not self.is_trained:
                logger.warning("⚠️  Model not trained, returning dummy prediction")
                return self._dummy_prediction(metrics)
            
            # Convert metrics to feature vector
            X = self._metrics_to_features(metrics)
            X = X.reshape(1, -1)
            
            # Scale
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            anomaly_score = -self.model.score_samples(X_scaled)[0]
            
            is_anomaly = prediction == -1
            confidence = min(max(anomaly_score / 2, 0), 1)
            
            result = {
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(anomaly_score),
                'confidence': float(confidence),
                'threshold': Config.ANOMALY_THRESHOLD,
                'timestamp': datetime.now().isoformat(),
                'metrics_used': list(metrics.keys())
            }
            
            if is_anomaly:
                logger.warning(f"🚨 Anomaly detected! Score: {anomaly_score:.3f}")
            else:
                logger.info(f"✅ No anomaly detected. Score: {anomaly_score:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in anomaly prediction: {str(e)}")
            return {'error': str(e), 'is_anomaly': False}
    
    def _metrics_to_features(self, metrics: Dict) -> np.ndarray:
        """Convert metric dict to feature vector"""
        features = []
        
        # Extract numeric values
        feature_names = [
            'cpu_utilization',
            'memory_utilization',
            'request_latency',
            'error_rate',
            'request_count'
        ]
        
        for feature in feature_names:
            if feature in metrics:
                features.append(float(metrics[feature]))
            else:
                features.append(0.0)
        
        return np.array(features)
    
    def _dummy_prediction(self, metrics: Dict) -> Dict:
        """Return dummy prediction when model not trained"""
        cpu = metrics.get('cpu_utilization', 0)
        memory = metrics.get('memory_utilization', 0)
        latency = metrics.get('request_latency', 0)
        
        # Simple threshold-based anomaly detection
        anomaly_conditions = [
            cpu > 80,
            memory > 85,
            latency > 500
        ]
        
        is_anomaly = any(anomaly_conditions)
        confidence = sum(anomaly_conditions) / len(anomaly_conditions)
        
        return {
            'is_anomaly': is_anomaly,
            'anomaly_score': confidence,
            'confidence': confidence,
            'threshold': Config.ANOMALY_THRESHOLD,
            'timestamp': datetime.now().isoformat(),
            'warning': 'Model not trained - using threshold-based detection'
        }
    
    def detect_pattern(self, history: List[Dict]) -> Dict:
        """Detect patterns that precede failures"""
        try:
            if len(history) < 5:
                return {
                    'pattern_found': False,
                    'message': 'Insufficient history for pattern detection'
                }
            
            df = pd.DataFrame(history)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            # Calculate correlations with failures
            correlations = {}
            for col in numeric_cols:
                if 'failed' in df.columns:
                    correlation = df[col].corr(df['failed'])
                    if abs(correlation) > 0.5:
                        correlations[col] = correlation
            
            result = {
                'pattern_found': len(correlations) > 0,
                'correlated_metrics': correlations,
                'timestamp': datetime.now().isoformat()
            }
            
            if result['pattern_found']:
                logger.info(f"📈 Found {len(correlations)} correlated metrics")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error detecting patterns: {str(e)}")
            return {'pattern_found': False, 'error': str(e)}

# Singleton instance
anomaly_detector = AnomalyDetector()