from django.urls import path

from .views import RetrieveSeriesAPIView, RetrieveStudyAPIView

urlpatterns = [
    path(
        "<str:pacs>/wadors/studies/<str:study_uid>/",
        RetrieveStudyAPIView.as_view(),
        name="wado_rs-studies_with_study_uid",
    ),
    path(
        "<str:pacs>/wadors/studies/<str:study_uid>/<str:mode>/",
        RetrieveStudyAPIView.as_view(),
        name="wado_rs-studies_with_study_uid_and_mode",
    ),
    path(
        "<str:pacs>/wadors/studies/<str:study_uid>/series/<str:series_uid>/",
        RetrieveSeriesAPIView.as_view(),
        name="wado_rs-series_with_study_uid_and_series_uid",
    ),
    path(
        "<str:pacs>/wadors/studies/<str:study_uid>/series/<str:series_uid>/<str:mode>/",
        RetrieveSeriesAPIView.as_view(),
        name="wado_rs-series_with_study_uid_and_series_uid_and_mode",
    ),
]
