from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView

from pipeline.search_utils import (
    generate_embedding,
    search_candidates,
    hybrid_search_candidates,
    bm25_search_candidates,
)

class CandidateSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return render(request, "search.html")

    def post(self, request):
        query = request.data.get("query") or ""
        query = query.strip()
        if not query:
            return Response({"error": "Query is required."}, status=400)

        method = (request.data.get("method") or "vector").lower()

        if method == "bm25":
            matches = bm25_search_candidates(query)
        elif method == "hybrid":
            embedding = generate_embedding(query)
            matches = hybrid_search_candidates(query, embedding)
        else:
            embedding = generate_embedding(query)
            matches = search_candidates(embedding)

        return Response(
            {
                "results": matches,
                "method": method,
            }
        )
