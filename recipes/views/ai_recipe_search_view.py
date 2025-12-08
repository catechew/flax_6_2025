from functools import reduce
import operator
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from dotenv import load_dotenv
import json
import openai

from recipes.models.recipe import Recipe

# Constants
SORT_OPTIONS = {
    'date_newest': '-publication_date',
    'date_oldest': 'publication_date',
    'prep_least': 'prep_time_hours',
    'prep_most': '-prep_time_hours',
    'cook_least': 'cook_time_hours',
    'cook_most': '-cook_time_hours',
    'title_az': 'title',
    'title_za': '-title',
}

# Load .env file to get API key
load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')


# Call OpenAI to extract search parameters from user context.
def get_search_params_from_ai(user_context):
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
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract recipe search params. Return only JSON."},
            {"role": "user", "content": ai_prompt}
        ],
        temperature=0.3,
        max_tokens=150,
        timeout=30
    )

    ai_response = response.choices[0].message.content.strip()
    return json.loads(ai_response)


# Apply text search across recipe fields. searches for ANY word in the query (not ALL).
def apply_search_query(recipes, search_query):
    if not search_query:
        return recipes

    search_words = search_query.split()
    recipes = recipes.annotate(
        full_name=Concat('author__first_name', Value(' '), 'author__last_name')
    )

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

    return recipes.filter(combined_q)


def apply_tag_filters(recipes, course_filters, dietary_filters, cuisine_filters, other_filters):
    """
    Apply tag-based filters to recipes.
    """
    filter_map = {
        'course_tags': course_filters,
        'dietary_tags': dietary_filters,
        'cuisine_tags': cuisine_filters,
        'other_tags': other_filters,
    }
    
    for tag_field, filter_values in filter_map.items():
        if filter_values:
            # build OR query for all values in this tag type
            tag_q = reduce(
                operator.or_,
                [Q(**{f'{tag_field}__icontains': value}) for value in filter_values]
            )
            recipes = recipes.filter(tag_q)
    
    return recipes


# Apply sorting to recipes based on sort_by parameter
def apply_sorting(recipes, sort_by):
    # Simple field sorts
    if sort_by in SORT_OPTIONS:
        return recipes.order_by(SORT_OPTIONS[sort_by])

    # Complex sorts that need annotation
    if sort_by in ['total_least', 'total_most']:
        recipes = recipes.annotate(
            total_minutes=(F('prep_time_hours') + F('cook_time_hours')) * 60 +
                          (F('prep_time_minutes') + F('cook_time_minutes'))
        )
        return recipes.order_by('total_minutes' if sort_by == 'total_least' else '-total_minutes')

    # Default sort
    return recipes.order_by('-publication_date')


# Get AI to rank top recipes based on user context
def get_ai_rankings(user_context, top_recipes):
    recipe_list = [
        {
            'id': recipe.id,
            'title': recipe.title,
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
    return json.loads(ranking_text)


def build_view_all_url(search_query, course_filters, dietary_filters, cuisine_filters, other_filters, sort_by):
    """
    build url for view all results button with all search parameters
    """
    url_params = [f'q={search_query}']
    
    filter_map = {
        'course': course_filters,
        'dietary': dietary_filters,
        'cuisine': cuisine_filters,
        'other': other_filters,
    }
    
    for param_name, filter_values in filter_map.items():
        for value in filter_values:  
            url_params.append(f'{param_name}={value}')
    
    url_params.append(f'sort={sort_by}')
    
    return '/all_recipes/?' + '&'.join(url_params)


# Use AI to find recipes based on context that users input
@login_required
def ai_recipe_search_view(request):
    if request.method != 'POST':
        return render(request, 'ai/ai_recipe_search.html')

    user_context = request.POST.get('context', '').strip()

    if not user_context:
        messages.error(request, 'Please describe your situation')
        return render(request, 'ai/ai_recipe_search.html')

    try:
        return process_ai_search(request, user_context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'ai/ai_recipe_search.html', {'user_context': user_context})

def process_ai_search(request, user_context):
    # Get search parameters from AI
    search_params = get_search_params_from_ai(user_context)

    # Filter recipes using extracted parameters
    recipes = filter_recipes(search_params)

    total_count = recipes.count()

    # handle no results
    if total_count == 0:
        context = {
            'user_context': user_context,
            'search_params': search_params,
            'no_results': True,
            'show_results': True
        }
        return render(request, 'ai/ai_recipe_search.html', context)

    # get AI to rank the results + then render them
    return render_search_results(recipes, request, user_context, search_params, total_count)

def filter_recipes(search_params):
    recipes = Recipe.objects.visible()
    recipes = apply_search_query(recipes, search_params.get('search_query', '').strip())
    recipes = apply_tag_filters(
        recipes,
        search_params.get('course_filters', []),
        search_params.get('dietary_filters', []),
        search_params.get('cuisine_filters', []),
        search_params.get('other_filters', [])
    )
    recipes = apply_sorting(recipes, search_params.get('sort_by', 'date_newest'))
    return recipes

def render_search_results(recipes, request, user_context, search_params, total_count):
    #Get AI to rank top results
    top_recipes = recipes[:10]
    ranking_data = get_ai_rankings(user_context, top_recipes)

    top_picks = ranking_data.get('top_picks', [])
    search_explanation = ranking_data.get('search_explanation', '')

    # Extract recipe IDs for "View Top Picks" button
    recipe_ids = [pick['recipe_id'] for pick in top_picks]
    top_pick_ids = ','.join(map(str, recipe_ids))

    # Build URL for "View All Results" button
    view_all_url = build_view_all_url(
        search_params.get('search_query', ''),
        search_params.get('course_filters', []),
        search_params.get('dietary_filters', []),
        search_params.get('cuisine_filters', []),
        search_params.get('other_filters', []),
        search_params.get('sort_by', '')
    )

    # Render results
    context = {
        'user_context': user_context,
        'search_params': search_params,
        'search_explanation': search_explanation,
        'top_picks': top_picks,
        'top_pick_ids': top_pick_ids,
        'total_count': total_count,
        'view_all_url': view_all_url,
        'show_results': True
    }

    return render(request, 'ai/ai_recipe_search.html', context)