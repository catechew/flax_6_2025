import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
import json
import openai

from recipes.models.recipe import Recipe


openai.api_key = os.environ.get('OPENAI_API_KEY')
print(f"=== API KEY: {os.environ.get('OPENAI_API_KEY', 'NOT SET')[:20]}...")

"""
AI Recipe Finder - handles both displaying the form and processing results.
"""
@login_required
def ai_recipe_finder_view(request):
    
    if request.method == 'POST':
        user_context = request.POST.get('context', '').strip()
        print(f"=== RECEIVED CONTEXT: {user_context}")  # Debugging print, there will be a few of these
        
        if not user_context:
            messages.error(request, 'Please describe your situation')
            return render(request, 'ai_recipe_finder.html')
        
        try:
            print("=== STARTING API CALL 1")
            # pass in context to chatGPT, which outputs a json of search parameters
            # right now we have to hardcode the list of params which I think is not easily avoidable
            ai_prompt = f"""Context: "{user_context}"

            Extract search params as JSON:
            {{
            "search_query": "keywords",
            "dietary_filters": ["vegetarian"/"vegan"/"halal"/"kosher"/"gluten-free"/"dairy-free"],
            "cuisine_filters": ["Japanese"/"Italian"/"Chinese"/"Asian"/"Persian"/"Jamaican"/"Western"/"British"/"Lebanese"/"Middle-Eastern"],
            "other_filters": ["high protein"/"low calorie"/"low carb"/"quick"/"budget"],
            "sort_by": "total_least"/"total_most"/"date_newest"
            }}
            Only relevant filters. Empty arrays if none apply."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract recipe search params. Return only JSON."},
                    {"role": "user", "content": ai_prompt}
                ],
                temperature=0.3, # slightly random and creative responses
                max_tokens=150,
                timeout=30  # added this one because it was taking too long before
            )
            
            print(f"=== GOT RESPONSE: {response}")  
            # get ai's response
            ai_response = response.choices[0].message.content.strip()
            print(f"=== API RESPONSE 1: {ai_response}")  
            
            # get search parameters from ai's response
            search_params = json.loads(ai_response)

            # start with all recipes and whittle it down based on search params
            recipes = Recipe.objects.all()
                
            # apply search query - search each word separately and combine results
            search_query = search_params.get('search_query', '').strip()
            if search_query:
                search_words = search_query.split()
                recipes = recipes.annotate(
                    full_name=Concat('author__first_name', Value(' '), 'author__last_name')
                )
                
                # combine all searches with one word each at a time
                combined_q = Q()
                for word in search_words:
                    combined_q |= (
                        Q(title__icontains=word) |
                        Q(adjectives__icontains=word) |
                        Q(ingredients__icontains=word) |
                        Q(steps__icontains=word) |
                        Q(author__username__icontains=word) |
                        Q(author__first_name__icontains=word) |
                        Q(author__last_name__icontains=word) |
                        Q(full_name__icontains=word)
                    )
                
                recipes = recipes.filter(combined_q)
            
            # Apply filters
            course_filters = search_params.get('course_filters', [])
            if course_filters:
                course_q = Q()
                for course in course_filters:
                    course_q |= Q(course_tags__icontains=course)
                recipes = recipes.filter(course_q)
            
            dietary_filters = search_params.get('dietary_filters', [])
            if dietary_filters:
                dietary_q = Q()
                for dietary in dietary_filters:
                    dietary_q |= Q(dietary_tags__icontains=dietary)
                recipes = recipes.filter(dietary_q)
            
            cuisine_filters = search_params.get('cuisine_filters', [])
            if cuisine_filters:
                cuisine_q = Q()
                for cuisine in cuisine_filters:
                    cuisine_q |= Q(cuisine_tags__icontains=cuisine)
                recipes = recipes.filter(cuisine_q)
            
            other_filters = search_params.get('other_filters', [])
            if other_filters:
                other_q = Q()
                for other in other_filters:
                    other_q |= Q(other_tags__icontains=other)
                recipes = recipes.filter(other_q)
            
            # Apply sorting, so AI recommendations can be top
            sort_by = search_params.get('sort_by', 'date_newest')
            if sort_by == 'date_newest':
                order_field = '-publication_date'
            elif sort_by == 'date_oldest':
                order_field = 'publication_date'
            elif sort_by == 'prep_least':
                order_field = 'prep_time_hours'
            elif sort_by == 'prep_most':
                order_field = '-prep_time_hours'
            elif sort_by == 'cook_least':
                order_field = 'cook_time_hours'
            elif sort_by == 'cook_most':
                order_field = '-cook_time_hours'
            elif sort_by == 'total_least':
                recipes = recipes.annotate(
                    total_minutes=(F('prep_time_hours') + F('cook_time_hours')) * 60 +
                                    (F('prep_time_minutes') + F('cook_time_minutes'))
                )
                order_field = 'total_minutes'
            elif sort_by == 'total_most':
                recipes = recipes.annotate(
                    total_minutes=(F('prep_time_hours') + F('cook_time_hours')) * 60 +
                                    (F('prep_time_minutes') + F('cook_time_minutes'))
                )
                order_field = '-total_minutes'
            elif sort_by == 'title_az':
                order_field = 'title'
            elif sort_by == 'title_za':
                order_field = '-title'
            else:
                order_field = '-publication_date'
            
            recipes = recipes.order_by(order_field)

            print(f"=== FOUND {recipes.count()} RECIPES")

            # Get top 10 results for ranking
            top_recipes = recipes[:10]
            print(f"=== TOP RECIPES: {list(top_recipes.values_list('id', 'title'))}")

            total_count = recipes.count()

            if total_count == 0:
                # No recipes found - show friendly message
                context = {
                    'user_context': user_context,
                    'search_params': search_params,
                    'no_results': True,
                    'show_results': True
                }
                return render(request, 'ai_recipe_finder.html', context)
            
            # if there are recipes to rank, get the AI to rank them
            if top_recipes.exists():
                print("=== STARTING API CALL 2")
                recipe_list = [
                    {
                        'id': recipe.id,
                        'title': recipe.title,
                        # get tags and trim off whitespace
                        'tags': f"{getattr(recipe, 'course_tags', '')} {getattr(recipe, 'dietary_tags', '')}".strip()
                    }
                    for recipe in top_recipes
                ]
                
                ranking_prompt = f"""Context: "{user_context}"

                    Recipes:
                    {json.dumps(recipe_list, indent=2)}

                    Rank top 3 recipes. Return JSON:
                    {{
                    "top_picks": [{{"recipe_id": 123, "title": "Name", "reason": "Why it fits (1 sentence)"}}],
                    "search_explanation": "Search strategy (1 sentence)"
                    }}"""
                
                ranking_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Rank recipes. Return only JSON."},
                        {"role": "user", "content": ranking_prompt}
                    ],
                    temperature=0.5,
                    max_tokens=300
                )

                ranking_text = ranking_response.choices[0].message.content.strip()

                # remove whitespace from start/end
                ranking_data = json.loads(ranking_text)

                top_picks = ranking_data.get('top_picks', [])
                search_explanation = ranking_data.get('search_explanation', '')

                # Build URL for when you click "View All Results" button
                # append each parameter to the url
                url_params = []
                if search_query:
                    url_params.append(f'q={search_query}')
                for course in course_filters:
                    url_params.append(f'course={course}')
                for dietary in dietary_filters:
                    url_params.append(f'dietary={dietary}')
                for cuisine in cuisine_filters:
                    url_params.append(f'cuisine={cuisine}')
                for other in other_filters:
                    url_params.append(f'other={other}')
                if sort_by:
                    url_params.append(f'sort={sort_by}')
                
                view_all_url = '/all_recipes/?' + '&'.join(url_params)

                # supply context to html file
                context = {
                    'user_context': user_context,
                    'search_params': search_params,
                    'search_explanation': search_explanation,
                    'top_picks': top_picks,
                    'total_count': total_count,
                    'view_all_url': view_all_url,
                    'show_results': True
                }

                print(f"AI RESPONSE 1: {ai_response[:100]}")
                print(f"AI RESPONSE 2: {ranking_text[:100]}")
                
                return render(request, 'ai_recipe_finder.html', context)
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'ai_recipe_finder.html', {'user_context': user_context})


    # this is for if a GET request was made. no context needed
    return render(request, 'ai_recipe_finder.html')
    
