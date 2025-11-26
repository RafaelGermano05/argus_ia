import pandas as pd
from django.http import HttpResponse
import tempfile
import os
from datetime import datetime

def export_to_csv(suspicious_comments, analysis):
    """Exporta dados para CSV com informações completas"""
    
    # Dados dos comentários suspeitos
    comments_data = []
    for comment in suspicious_comments:
        comments_data.append({
            'comment_id': comment.comment_id,
            'username': comment.username,
            'comment_text': comment.comment_text,
            'probability': f"{comment.probability:.4f}",
            'risk_level': 'ALTO' if comment.probability > 0.8 else 'MÉDIO' if comment.probability > 0.6 else 'BAIXO',
            'detected_patterns': ', '.join(comment.detected_patterns) if comment.detected_patterns else 'Nenhum padrão específico',
            'analysis_date': analysis.created_at.strftime("%d/%m/%Y %H:%M")
        })
    
    # Criar DataFrame
    df_comments = pd.DataFrame(comments_data)
    
    # Criar resposta HTTP
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="argus_analysis_{analysis.id}_suspicious_comments.csv"'
    
    # Escrever CSV
    df_comments.to_csv(response, index=False, encoding='utf-8')
    
    return response

def export_to_excel(suspicious_comments, analysis):
    """Exporta dados para Excel com múltiplas abas"""
    
    # Dados dos comentários suspeitos
    comments_data = []
    for comment in suspicious_comments:
        comments_data.append({
            'ID do Comentário': comment.comment_id,
            'Usuário': comment.username,
            'Texto do Comentário': comment.comment_text,
            'Probabilidade': comment.probability,
            'Nível de Risco': 'ALTO' if comment.probability > 0.8 else 'MÉDIO' if comment.probability > 0.6 else 'BAIXO',
            'Padrões Detectados': ', '.join(comment.detected_patterns) if comment.detected_patterns else 'Nenhum padrão específico',
            'Data da Análise': analysis.created_at
        })
    
    # Dados de estatísticas
    stats_data = [{
        'Total de Comentários Analisados': analysis.total_comments,
        'Comentários Suspeitos Detectados': analysis.suspicious_count,
        'Taxa de Detecção (%)': analysis.suspicious_percentage(),
        'Acurácia do Modelo': analysis.accuracy,
        'ID da Análise': str(analysis.id),
        'Dataset': analysis.dataset.name,
        'Data da Análise': analysis.created_at,
        'Posts no Dataset': analysis.dataset.posts_count,
        'Comentários no Dataset': analysis.dataset.comments_count
    }]
    
    # Dados dos usuários mais suspeitos
    user_data = []
    for user in analysis.user_behaviors.all()[:50]:
        user_data.append({
            'Usuário': user.username,
            'ID do Usuário': user.user_id,
            'Comentários Suspeitos': user.suspicious_comments_count,
            'Total de Comentários': user.total_comments,
            'Taxa de Suspeição (%)': user.suspicion_score,
            'Padrões Detectados': ', '.join(user.detected_patterns) if user.detected_patterns else 'Nenhum'
        })
    
    # Dados dos posts mais visados
    post_data = []
    for post in analysis.post_analyses.all()[:50]:
        post_data.append({
            'ID do Post': post.post_id,
            'Autor': post.username,
            'Legenda': post.caption,
            'Comentários Suspeitos': post.suspicious_comments_count,
            'Total de Comentários': post.total_comments,
            'Taxa de Visitação Suspeita (%)': post.suspicion_ratio
        })
    
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        with pd.ExcelWriter(tmp.name, engine='openpyxl') as writer:
            # Aba de comentários suspeitos
            if comments_data:
                df_comments = pd.DataFrame(comments_data)
                df_comments.to_excel(writer, sheet_name='Comentários Suspeitos', index=False)
            
            # Aba de estatísticas
            df_stats = pd.DataFrame(stats_data)
            df_stats.to_excel(writer, sheet_name='Estatísticas', index=False)
            
            # Aba de usuários suspeitos
            if user_data:
                df_users = pd.DataFrame(user_data)
                df_users.to_excel(writer, sheet_name='Usuários Suspeitos', index=False)
            
            # Aba de posts visados
            if post_data:
                df_posts = pd.DataFrame(post_data)
                df_posts.to_excel(writer, sheet_name='Posts Visados', index=False)
            
            # Aba de informações do modelo
            model_info = [{
                'Sistema': 'ARGUS IA - Detecção de Perfis Suspeitos',
                'Versão': '1.0',
                'Data de Exportação': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'Padrões Monitorados': 'Emojis suspeitos (corações, espirais) e textos inadequados',
                'Finalidade': 'Uso acadêmico - Projeto de detecção de comportamentos suspeitos'
            }]
            df_info = pd.DataFrame(model_info)
            df_info.to_excel(writer, sheet_name='Informações', index=False)
        
        tmp.seek(0)
        excel_data = tmp.read()
    
    os.unlink(tmp.name)
    
    response = HttpResponse(
        excel_data,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="argus_analysis_{analysis.id}_full_report.xlsx"'
    return response