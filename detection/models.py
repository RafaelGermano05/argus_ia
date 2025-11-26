from django.db import models
import uuid

class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posts_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class AnalysisSession(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_comments = models.IntegerField(default=0)
    suspicious_count = models.IntegerField(default=0)
    accuracy = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    def suspicious_percentage(self):
        if self.total_comments > 0:
            return (self.suspicious_count / self.total_comments) * 100
        return 0
    
    def __str__(self):
        return f"Analysis {self.id} - {self.status}"

class SuspiciousComment(models.Model):
    session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='suspicious_comments')
    comment_id = models.IntegerField()
    username = models.CharField(max_length=100)
    comment_text = models.TextField()
    probability = models.FloatField()
    detected_patterns = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-probability']

class UserBehavior(models.Model):
    analysis_session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='user_behaviors')
    username = models.CharField(max_length=100)
    user_id = models.IntegerField()
    suspicious_comments_count = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    suspicion_score = models.FloatField(default=0.0)
    detected_patterns = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-suspicion_score']

class PostAnalysis(models.Model):
    analysis_session = models.ForeignKey(AnalysisSession, on_delete=models.CASCADE, related_name='post_analyses')
    post_id = models.IntegerField()
    caption = models.TextField(blank=True)
    username = models.CharField(max_length=100)
    suspicious_comments_count = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)
    suspicion_ratio = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-suspicion_ratio']