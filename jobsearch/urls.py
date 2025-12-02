from __future__ import annotations

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from pipeline.views import CandidateSearchView


def healthcheck(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
    path("search/", CandidateSearchView.as_view(), name="candidate-search"),
]
