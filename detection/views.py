import json
import pandas as pd
import tempfile
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.contrib import messages
from django.db import transaction
import io

from .models import Dataset, AnalysisSession, SuspiciousComment, UserBehavior, PostAnalysis
from .ml.data_generator import DataGenerator
from .ml.detector import SuspiciousPatternDetector
from .utils.exporters import export_to_csv, export_to_excel

class DashboardView(View):
    def get(self, request):
        datasets = Dataset.objects.all().order_by('-created_at')
        analyses = AnalysisSession.objects.all().order_by('-created_at')[:10]
        
        context = {
            'datasets': datasets,
            'recent_analyses': analyses,
            'total_analyses': analyses.count(),
            'total_datasets': datasets.count(),
        }
        return render(request, 'detection/dashboard.html', context)

class GenerateDatasetView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            posts_count = data.get('posts_count', 1000)
            comments_count = data.get('comments_count', 5000)
            suspicious_ratio = data.get('suspicious_ratio', 0.05)
            
            print(f"🎯 Gerando dataset: {posts_count} posts, {comments_count} comentários, {suspicious_ratio*100}% suspeitos")
            
            # Gerar dataset
            posts_df, comments_df, actual_suspicious = DataGenerator.generate_dataset(
                posts_count, comments_count, suspicious_ratio
            )
            
            # Criar registro no banco
            dataset = Dataset.objects.create(
                name=f"Dataset_{Dataset.objects.count() + 1}",
                description=f"Dataset com {posts_count} posts e {comments_count} comentários",
                posts_count=posts_count,
                comments_count=comments_count
            )
            
            # Em produção, salvar os DataFrames em memória (não em arquivos)
            request.session['current_dataset'] = {
                'id': str(dataset.id),
                'posts_count': posts_count,
                'comments_count': comments_count,
                'actual_suspicious': actual_suspicious,
                'posts_data': posts_df.to_json(orient='records'),  # Salvar como JSON em memória
                'comments_data': comments_df.to_json(orient='records')  # Salvar como JSON em memória
            }
            
            print(f"✅ Dataset gerado: {actual_suspicious} comentários suspeitos")
            
            return JsonResponse({
                'success': True,
                'dataset': {
                    'id': str(dataset.id),
                    'name': dataset.name,
                    'posts_count': posts_count,
                    'comments_count': comments_count,
                    'actual_suspicious': actual_suspicious,
                    'suspicious_ratio': f"{(actual_suspicious/comments_count)*100:.2f}%"
                }
            })
            
        except Exception as e:
            print(f"❌ Erro ao gerar dataset: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

class AnalyzeDatasetView(View):
    def post(self, request):
        try:
            dataset_info = request.session.get('current_dataset')
            if not dataset_info:
                return JsonResponse({'success': False, 'error': 'Nenhum dataset carregado'})
            
            print("📊 Iniciando análise do dataset...")
            
            # Carregar dados da sessão (JSON em memória)
            posts_df = pd.read_json(io.StringIO(dataset_info['posts_data']))
            comments_df = pd.read_json(io.StringIO(dataset_info['comments_data']))
            
            # Criar sessão de análise
            dataset = Dataset.objects.get(id=dataset_info['id'])
            session = AnalysisSession.objects.create(
                dataset=dataset,
                total_comments=dataset_info['comments_count'],
                status='RUNNING'
            )
            
            # Treinar e executar detector
            detector = SuspiciousPatternDetector()
            
            # Criar labels baseadas nos dados reais
            labels = comments_df['is_suspicious_actual'].astype(int).values
            
            # Treinar modelo
            accuracy = detector.train(comments_df, labels)
            
            # Fazer predições
            predictions, probabilities, detected_patterns = detector.predict(comments_df)
            
            # Analisar comportamento de usuários
            user_behaviors = detector.analyze_user_behavior(comments_df, predictions, detected_patterns)
            
            # Analisar posts mais visados
            post_analyses = detector.analyze_posts_targeted(posts_df, comments_df, predictions)
            
            # Salvar resultados
            suspicious_count = int(predictions.sum())
            session.suspicious_count = suspicious_count
            session.accuracy = accuracy
            session.status = 'COMPLETED'
            session.save()
            
            # Salvar comentários suspeitos
            suspicious_comments = []
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                if pred == 1:
                    row = comments_df.iloc[i]
                    suspicious_comments.append(SuspiciousComment(
                        session=session,
                        comment_id=row['comment_id'],
                        username=row['username'],
                        comment_text=row['comment_text'],
                        probability=prob,
                        detected_patterns=detected_patterns[i]
                    ))
            
            SuspiciousComment.objects.bulk_create(suspicious_comments)
            
            # Salvar comportamentos de usuários
            user_behavior_objs = []
            for user_behavior in user_behaviors[:100]:
                user_behavior_objs.append(UserBehavior(
                    analysis_session=session,
                    username=user_behavior['username'],
                    user_id=user_behavior['user_id'],
                    suspicious_comments_count=user_behavior['suspicious_count'],
                    total_comments=user_behavior['total_count'],
                    suspicion_score=user_behavior['suspicion_score'],
                    detected_patterns=user_behavior['patterns']
                ))
            
            UserBehavior.objects.bulk_create(user_behavior_objs)
            
            # Salvar análises de posts
            post_analysis_objs = []
            for post_analysis in post_analyses[:100]:
                post_analysis_objs.append(PostAnalysis(
                    analysis_session=session,
                    post_id=post_analysis['post_id'],
                    caption=post_analysis['caption'],
                    username=post_analysis['username'],
                    suspicious_comments_count=post_analysis['suspicious_count'],
                    total_comments=post_analysis['total_count'],
                    suspicion_ratio=post_analysis['suspicion_ratio']
                ))
            
            PostAnalysis.objects.bulk_create(post_analysis_objs)
            
            # Limpar session
            if 'current_dataset' in request.session:
                del request.session['current_dataset']
            
            print(f"✅ Análise concluída: {suspicious_count} suspeitos detectados")
            
            return JsonResponse({
                'success': True,
                'analysis': {
                    'id': str(session.id),
                    'total_comments': session.total_comments,
                    'suspicious_count': session.suspicious_count,
                    'suspicious_percentage': session.suspicious_percentage(),
                    'accuracy': session.accuracy,
                    'actual_suspicious': dataset_info['actual_suspicious'],
                    'detection_accuracy': (suspicious_count / dataset_info['actual_suspicious'] * 100) if dataset_info['actual_suspicious'] > 0 else 0,
                    'top_users_count': len(user_behaviors),
                    'top_posts_count': len(post_analyses)
                }
            })
            
        except Exception as e:
            print(f"❌ Erro na análise: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

class AnalysisResultsView(View):
    def get(self, request, analysis_id):
        try:
            analysis = AnalysisSession.objects.get(id=analysis_id)
            suspicious_comments = analysis.suspicious_comments.all()[:50]
            top_users = analysis.user_behaviors.all()[:20]
            top_posts = analysis.post_analyses.all()[:20]
            
            context = {
                'analysis': analysis,
                'suspicious_comments': suspicious_comments,
                'top_users': top_users,
                'top_posts': top_posts,
                'detection_rate': analysis.suspicious_percentage(),
                'accuracy_percentage': analysis.accuracy * 100,
            }
            return render(request, 'detection/results.html', context)
        
        except AnalysisSession.DoesNotExist:
            messages.error(request, 'Análise não encontrada.')
            return redirect('detection:dashboard')

class ExportDataView(View):
    def get(self, request, analysis_id):
        try:
            analysis = AnalysisSession.objects.get(id=analysis_id)
            suspicious_comments = analysis.suspicious_comments.all()
            
            format_type = request.GET.get('format', 'csv')
            
            if format_type == 'csv':
                response = export_to_csv(suspicious_comments, analysis)
            elif format_type == 'excel':
                response = export_to_excel(suspicious_comments, analysis)
            else:
                return JsonResponse({'error': 'Formato não suportado'})
            
            return response
            
        except AnalysisSession.DoesNotExist:
            return JsonResponse({'error': 'Análise não encontrada'})

class GenerateDatasetPageView(View):
    """Página para gerar datasets"""
    def get(self, request):
        return render(request, 'detection/generate_dataset.html')

class GenerateAndDownloadDatasetView(View):
    """Gera e faz download automático dos CSVs"""
    def post(self, request):
        try:
            data = json.loads(request.body)
            posts_count = data.get('posts_count', 1000)
            comments_count = data.get('comments_count', 5000)
            suspicious_ratio = data.get('suspicious_ratio', 0.05)
            
            # Gerar dataset
            posts_df, comments_df, actual_suspicious = DataGenerator.generate_dataset(
                posts_count, comments_count, suspicious_ratio
            )
            
            # Criar resposta com ambos CSVs em JSON
            response_data = {
                'success': True,
                'posts_csv': posts_df.to_csv(index=False),
                'comments_csv': comments_df.to_csv(index=False),
                'dataset_info': {
                    'posts_count': posts_count,
                    'comments_count': comments_count,
                    'suspicious_ratio': f"{suspicious_ratio*100}%",
                    'actual_suspicious': actual_suspicious
                }
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class DownloadPostsCSVView(View):
    """Faz download do posts.csv"""
    def get(self, request):
        dataset_data = request.session.get('generated_dataset')
        if not dataset_data:
            return HttpResponse("Dados não encontrados. Gere um dataset primeiro.", status=404)
        
        response = HttpResponse(dataset_data['posts_data'], content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="posts.csv"'
        return response

class DownloadCommentsCSVView(View):
    """Faz download do comments.csv"""
    def get(self, request):
        dataset_data = request.session.get('generated_dataset')
        if not dataset_data:
            return HttpResponse("Dados não encontrados. Gere um dataset primeiro.", status=404)
        
        response = HttpResponse(dataset_data['comments_data'], content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="comments.csv"'
        return response

class UploadDatasetView(View):
    """Faz upload de dataset CSV"""
    def post(self, request):
        try:
            posts_file = request.FILES.get('posts_file')
            comments_file = request.FILES.get('comments_file')
            
            if not posts_file or not comments_file:
                return JsonResponse({'success': False, 'error': 'Ambos os arquivos são necessários'})
            
            # Ler arquivos CSV
            posts_df = pd.read_csv(posts_file)
            comments_df = pd.read_csv(comments_file)
            
            # Validar colunas básicas
            required_posts_cols = ['post_id', 'user_id', 'username', 'caption', 'post_date']
            required_comments_cols = ['comment_id', 'post_id', 'user_id', 'username', 'comment_text']
            
            if not all(col in posts_df.columns for col in required_posts_cols):
                return JsonResponse({'success': False, 'error': 'posts.csv não tem as colunas necessárias'})
            
            if not all(col in comments_df.columns for col in required_comments_cols):
                return JsonResponse({'success': False, 'error': 'comments.csv não tem as colunas necessárias'})
            
            # Criar registro no banco
            dataset = Dataset.objects.create(
                name=f"Uploaded_Dataset_{Dataset.objects.count() + 1}",
                description=f"Dataset carregado via upload - {posts_df.shape[0]} posts, {comments_df.shape[0]} comentários",
                posts_count=posts_df.shape[0],
                comments_count=comments_df.shape[0]
            )
            
            # Salvar dados na sessão
            request.session['current_dataset'] = {
                'id': str(dataset.id),
                'posts_count': posts_df.shape[0],
                'comments_count': comments_df.shape[0],
                'actual_suspicious': 0,  # Desconhecido em upload
                'posts_data': posts_df.to_json(orient='records'),
                'comments_data': comments_df.to_json(orient='records'),
                'is_uploaded': True
            }
            
            return JsonResponse({
                'success': True,
                'dataset': {
                    'id': str(dataset.id),
                    'name': dataset.name,
                    'posts_count': posts_df.shape[0],
                    'comments_count': comments_df.shape[0],
                    'actual_suspicious': 'Desconhecido (será detectado)'
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})