from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from apps.weblog.models import Article, Comment


@cache_page(60 * 5)
def article_inventory(request):
    articles = Article.published.all()
    return render(
        request, "weblog/article_inventory.html", {
            "articles": articles,
            "current_page": "article-inventory"
        }
    )


def article_page(request, slug):
    article = get_object_or_404(Article.published, slug=slug)
    comments = article.comments.all()

    if request.method == "POST":
        nickname = request.POST.get("nickname", "anonymous")[:64].strip()
        if not nickname:
            nickname = "anonymous"
        
        body = request.POST.get("body", "").strip()

        if body:
            Comment.objects.create(
                article=article,
                nickname=nickname,
                body=body
            )
            return redirect('weblog:article_page', slug=slug)

    return render(request, "weblog/article_page.html", {
        "article": article,
        "comments": comments
    })