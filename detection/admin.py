from django.contrib import admin
from .models import Dataset, AnalysisSession, SuspiciousComment, UserBehavior, PostAnalysis

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'posts_count', 'comments_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']

@admin.register(AnalysisSession)
class AnalysisSessionAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'created_at', 'total_comments', 'suspicious_count', 'accuracy', 'status']
    list_filter = ['status', 'created_at']
    readonly_fields = ['created_at']

@admin.register(SuspiciousComment)
class SuspiciousCommentAdmin(admin.ModelAdmin):
    list_display = ['username', 'comment_text', 'probability', 'session']
    list_filter = ['session']
    search_fields = ['username', 'comment_text']

@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ['username', 'suspicious_comments_count', 'total_comments', 'suspicion_score']
    list_filter = ['analysis_session']
    search_fields = ['username']

@admin.register(PostAnalysis)
class PostAnalysisAdmin(admin.ModelAdmin):
    list_display = ['post_id', 'username', 'suspicious_comments_count', 'total_comments', 'suspicion_ratio']
    list_filter = ['analysis_session']
    search_fields = ['username', 'caption']