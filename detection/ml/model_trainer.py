import pandas as pd
from .detector import SuspiciousPatternDetector
import joblib

def create_training_data(comments_df):
    """Cria dados de treinamento rotulados baseados nos padrões suspeitos"""
    labels = []
    
    for _, row in comments_df.iterrows():
        comment = str(row['comment_text']).lower()
        
        # Marcar como suspeito se contiver padrões conhecidos
        suspicious = any(pattern in comment for pattern in [
            '👧💕', '💜💜', '👧🏻💖', '💕👧', '💖💖',
            '🌀👦', '👦🌀', '💙🌀', '🌀💙', '👦💙',
            'menina linda', 'garotinha fofa', 'menino bonito'
        ])
        
        labels.append(1 if suspicious else 0)
    
    return labels

def train_and_save_model(comments_df, model_path='suspicious_pattern_detector.pkl'):
    """Treina e salva o modelo"""
    print("Criando dados de treinamento...")
    labels = create_training_data(comments_df)
    
    print("Treinando modelo...")
    detector = SuspiciousPatternDetector()
    accuracy = detector.train(comments_df, labels)
    
    print("Salvando modelo...")
    detector.save_model(model_path)
    
    print(f"Modelo salvo em {model_path} com acurácia: {accuracy:.4f}")
    return detector, accuracy

def load_trained_model(model_path='suspicious_pattern_detector.pkl'):
    """Carrega um modelo treinado"""
    detector = SuspiciousPatternDetector()
    detector.load_model(model_path)
    return detector