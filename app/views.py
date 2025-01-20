from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from .firebase import login_or_register, get_users_from_firebase
from django.views.decorators.csrf import csrf_exempt
from .models import Article
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import json
from django.contrib.auth.decorators import login_required

# Home view - Handles display and actions related to articles
def home(request):
    if request.method == "POST":
        # Add article
        if 'add_article' in request.POST:
            title = request.POST['title']
            description = request.POST['description']
            price = request.POST['price']
            image = request.POST['image']
            article = Article(title=title, description=description, price=price, image=image)
            article.save()
            return redirect('home')

        # Modify article
        elif 'modify_article' in request.POST:
            article_key = request.POST.get('article_key')
            if article_key:
                try:
                    article = Article.objects.get(id=article_key)
                    article.title = request.POST['title']
                    article.description = request.POST['description']
                    article.price = request.POST['price']
                    article.image = request.POST['image']
                    article.save()
                    return redirect('home')
                except Article.DoesNotExist:
                    pass

        # Delete article
        elif 'delete_article' in request.POST:
            article_key = request.POST.get('article_key')
            if article_key:
                try:
                    article = Article.objects.get(id=article_key)
                    article.delete()
                    return redirect('home')
                except Article.DoesNotExist:
                    pass

    # For GET request, render the page with articles and users from Firebase
    articles = Article.objects.all()
    users = get_users_from_firebase()
    return render(request, 'home.html', {'articles': articles, 'users': users})

# Login view - Handles user login and registration
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Validate the password using Django's validation
        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, '; '.join(e.messages))
            return render(request, 'login.html')

        try:
            # Login or register the user
            user = login_or_register(email, password)

            # Set session details
            request.session['user_id'] = user.uid
            request.session.set_expiry(300)
            return redirect('home')
        except ValueError as ve:
            messages.error(request, f"Error: {str(ve)}")
            return render(request, 'login.html')
        except Exception as e:
            messages.error(request, f"Unexpected error occurred: {str(e)}")
            return render(request, 'login.html')

    return render(request, 'login.html')

@login_required 
def logout_user(request):

    logout(request)
    return redirect('login')

# Create article view - Adds a new article via API (JSON)
@csrf_exempt
def add_article(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            title = data.get('title')
            content = data.get('content')
            # Create and save the new article
            article = Article.objects.create(title=title, content=content)
            return JsonResponse({"message": "Article added successfully!", "id": article.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": f"Error adding article: {str(e)}"}, status=400)

# Delete article view - Deletes an article by its ID
@csrf_exempt
def delete_article(request, article_id):
    try:
        # Find the article by ID and delete it
        article = Article.objects.get(id=article_id)
        article.delete()
        return JsonResponse({"message": "Article deleted successfully!"}, status=200)
    except Article.DoesNotExist:
        return JsonResponse({"error": "Article not found"}, status=404)

# Update article view - Updates an article by its ID
@csrf_exempt
def update_article(request, article_id):
    try:
        # Find the article by ID
        article = Article.objects.get(id=article_id)
        if request.method == 'PUT':
            data = json.loads(request.body)
            article.title = data.get('title', article.title)
            article.content = data.get('content', article.content)
            article.save()
            return JsonResponse({"message": "Article updated successfully!"}, status=200)
        return JsonResponse({"error": "Invalid method"}, status=405)
    except Article.DoesNotExist:
        return JsonResponse({"error": "Article not found"}, status=404)
