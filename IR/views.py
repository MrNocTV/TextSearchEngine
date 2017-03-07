from django.shortcuts import render
from django.http import HttpResponse
import pre_processing

# Create your views here.
def home(request):
    return render(request, "IR/home.html", {})

def search(request):
    query = request.GET["query"]
    results, display, query_terms = pre_processing.retrieval(query)
    return render(request, "IR/search.html", {"query":query, "display":display, "results":results, "query_terms":query_terms})