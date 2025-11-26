import pandas as pd
import random
from datetime import datetime, timedelta
from django.utils import timezone
import numpy as np

class DataGenerator:
    @staticmethod
    def generate_dataset(posts_count=1000, comments_count=5000, suspicious_ratio=0.05):
        """Gera dataset completo para teste com taxa de suspeitos precisa e natural"""
        
        # Garantir que os valores são inteiros
        posts_count = int(posts_count)
        comments_count = int(comments_count)
        
        # Calcular número exato de comentários suspeitos com variação natural
        expected_suspicious = int(comments_count * suspicious_ratio)
        # Adicionar variação de ±20% para ser mais natural
        variation = int(expected_suspicious * 0.2)
        actual_suspicious = expected_suspicious + random.randint(-variation, variation)
        # Garantir mínimo de 1 se a taxa for > 0
        if suspicious_ratio > 0 and actual_suspicious < 1:
            actual_suspicious = 1
        
        print(f"🎯 Gerando dataset:")
        print(f"   📊 Posts: {posts_count}")
        print(f"   💬 Comentários: {comments_count}")
        print(f"   🚨 Taxa suspeita: {suspicious_ratio*100}%")
        print(f"   🎯 Esperados: {expected_suspicious} comentários suspeitos")
        print(f"   📈 Com variação: {actual_suspicious} comentários suspeitos")

        # Gerar posts
        posts_data = []
        for i in range(1, posts_count + 1):
            user_id = random.randint(100, 999)
            username = f"user_{user_id}"
            caption = DataGenerator._generate_caption()
            post_date = DataGenerator._generate_random_date()
            likes_count = random.randint(0, 200)
            
            posts_data.append({
                'post_id': i,
                'user_id': user_id,
                'username': username,
                'caption': caption,
                'post_date': post_date,
                'likes_count': likes_count
            })
        
        # Gerar comentários
        comments_data = []
        suspicious_comments_generated = 0
        
        # Criar usuários com comportamentos variados
        suspicious_users = ['predator_1', 'danger_acc', 'suspect_usr', 'bad_actor', 'risk_user']
        normal_users = [f'normal_user_{i}' for i in range(1, 201)]
        
        # Definir probabilidades de comportamento para cada usuário
        user_behavior_probs = {}
        
        # Usuários suspeitos têm alta probabilidade (70-90%)
        for user in suspicious_users:
            user_behavior_probs[user] = random.uniform(0.7, 0.9)
        
        # Usuários normais têm baixa probabilidade (1-10%)
        for user in normal_users:
            user_behavior_probs[user] = random.uniform(0.01, 0.1)
        
        # Garantir número aproximado de comentários suspeitos
        for i in range(1, comments_count + 1):
            post_id = random.randint(1, posts_count)
            
            # Escolher usuário aleatoriamente
            if random.random() < 0.15:  # 15% de chance de ser usuário suspeito
                username = random.choice(suspicious_users)
            else:
                username = random.choice(normal_users)
            
            user_id = hash(username) % 1000
            
            # Decidir se este comentário será suspeito baseado no comportamento do usuário
            user_suspicion_prob = user_behavior_probs.get(username, 0.05)
            
            # Ajustar probabilidade para atingir o número desejado
            remaining_suspicious = actual_suspicious - suspicious_comments_generated
            remaining_comments = comments_count - i
            
            if remaining_suspicious > 0 and remaining_suspicious == remaining_comments:
                # Forçar suspeito se for o último necessário
                comment_text, is_suspicious = DataGenerator._generate_suspicious_comment()
                suspicious_comments_generated += 1
            elif suspicious_comments_generated < actual_suspicious and random.random() < user_suspicion_prob:
                # Comentário suspeito baseado no comportamento do usuário
                comment_text, is_suspicious = DataGenerator._generate_suspicious_comment()
                suspicious_comments_generated += 1
            else:
                # Comentário normal
                comment_text, is_suspicious = DataGenerator._generate_normal_comment()
            
            comment_date = DataGenerator._generate_random_date()
            
            comments_data.append({
                'comment_id': i,
                'post_id': post_id,
                'user_id': user_id,
                'username': username,
                'comment_text': comment_text,
                'comment_date': comment_date,
                'is_suspicious_actual': is_suspicious
            })
        
        # Verificação final
        actual_ratio = suspicious_comments_generated / comments_count
        print(f"✅ Dataset gerado:")
        print(f"   🎯 Esperados: {expected_suspicious} suspeitos")
        print(f"   📈 Gerados: {suspicious_comments_generated} suspeitos")
        print(f"   📊 Taxa real: {actual_ratio*100:.2f}%")
        
        posts_df = pd.DataFrame(posts_data)
        comments_df = pd.DataFrame(comments_data)
        
        return posts_df, comments_df, suspicious_comments_generated
    
    @staticmethod
    def _generate_caption():
        normal_captions = [
            "Dia lindo no parque! 🌳",
            "Momento em família ❤️",
            "Novo hobby! 📚",
            "Passeio incrível! ✈️",
            "Almoço delicioso! 🍕",
            "Treino do dia 💪",
            "Pôr do sol maravilhoso 🌅",
            "Final de semana perfeito! 😊",
            "Novas conquistas! 🏆",
            "Momento de paz ✨",
            "Com os amigos! 👫",
            "Viagem dos sonhos! 🌍",
            "Novo livro! 📖",
            "Dia de festa! 🎉",
            "Natureza é vida! 🌿"
        ]
        return random.choice(normal_captions)
    
    @staticmethod
    def _generate_normal_comment():
        """Gera comentários normais (nunca suspeitos)"""
        normal_comments = [
            "Que legal! 😊", "Adorei! ❤️", "Incrível! 🌟",
            "Belo momento! 📸", "Maravilhoso! ✨", "Top! 🔥",
            "Muito bom! 👍", "Fantástico! 💫", "Show! 🎉",
            "Parabéns! 👏", "Que foto incrível! 📷", "Amei! 💖",
            "Sensacional! 😍", "Perfeito! 💯", "Incrível! 🤩",
            "Que máximo! 🚀", "Adorável! 🥰", "Fantástico! 🌈",
            "Impressionante! 😲", "Excelente! ⭐"
        ]
        return random.choice(normal_comments), False
    
    @staticmethod
    def _generate_suspicious_comment():
        """Gera comentários suspeitos com variação"""
        suspicious_patterns = [
            ("👧💕 Que fofa!", "emoji_hearts_girls"),
            ("💜💜 linda demais", "emoji_hearts_girls"), 
            ("👧🏻💖 maravilhosa", "emoji_hearts_girls"),
            ("🌀👦 garoto bonito", "emoji_spiral_boys"),
            ("👦🌀 que menino lindo", "emoji_spiral_boys"),
            ("que menina linda", "suspicious_text_girls"),
            ("garotinha fofa demais", "suspicious_text_girls"),
            ("menino bonito esse", "suspicious_text_boys"),
            ("👧💕💕 linda menina", "emoji_hearts_girls"),
            ("🌀👦🌀 que garoto", "emoji_spiral_boys"),
            ("💕👧🏻 tão fofa", "emoji_hearts_girls"),
            ("👦💙 lindo menino", "emoji_spiral_boys"),
            ("menina encantadora", "suspicious_text_girls"),
            ("garoto especial", "suspicious_text_boys"),
            ("👧💖 que princesa", "emoji_hearts_girls"),
            ("🌀👦💙 menino lindo", "emoji_spiral_boys")
        ]
        
        # Escolher padrão aleatório
        comment, pattern_type = random.choice(suspicious_patterns)
        
        # Adicionar variação ocasional no texto
        if random.random() < 0.3:
            variations = ["", "!", "!!", " 💕", " 😊"]
            comment += random.choice(variations)
        
        return comment, True
    
    @staticmethod
    def _generate_random_date():
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()
        random_date = start_date + timedelta(
            seconds=random.randint(0, int((end_date - start_date).total_seconds()))
        )
        return random_date.strftime("%Y-%m-%d")