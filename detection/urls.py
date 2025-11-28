from django.urls import path
from . import views

app_name = 'detection'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('generate-dataset/', views.GenerateDatasetPageView.as_view(), name='generate_dataset_page'),
    path('generate-download/', views.GenerateAndDownloadDatasetView.as_view(), name='generate_and_download_dataset'),
    path('upload-dataset/', views.UploadDatasetView.as_view(), name='upload_dataset'),
    path('analyze-dataset/', views.AnalyzeDatasetView.as_view(), name='analyze_dataset'),
    path('results/<uuid:analysis_id>/', views.AnalysisResultsView.as_view(), name='analysis_results'),
    path('export/<uuid:analysis_id>/', views.ExportDataView.as_view(), name='export_data'),
]