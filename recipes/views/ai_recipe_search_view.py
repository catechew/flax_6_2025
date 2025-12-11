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
from openai import error

from recipes.models.recipe import Recipe

SORT_OPTIONS = {
    "date_newest": "-publication_date",
    "date_oldest": "publication_date",
    "prep_least": "prep_time_hours",
    "prep_most": "-prep_time_hours",
    "cook_least": "cook_time_hours",
    "cook_most": "-cook_time_hours",
    "title_az": "title",
    "title_za": "-title",
}

ERROR_MESSAGES = {
    json.JSONDecodeError: "Unable to process AI response. Please try again.",
    error.AuthenticationError: "AI service configuration error. Apologies for the inconvenience.",
    error.RateLimitError: "AI service is busy. Please wait a moment and try again.",
    error.APIConnectionError: "Unable to connect to AI service. Please check your connection.",
}
DEFAULT_ERROR = "Something went wrong. Please try again."

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")


def _build_search_prompt(user_context):
    """Build prompt for extracting search parameters."""
    return f"""Context: "{user_context}"
Extract: {{"search_query":"keywords","dietary_filters":[],"cuisine_filters":[],"other_filters":[],"sort_by":"date_newest"}}
Only relevant filters."""


def get_search_params_from_ai(user_context):
    """Call OpenAI to extract search parameters."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract recipe search params. Return only JSON.",
            },
            {"role": "user", "content": _build_search_prompt(user_context)},
        ],
        temperature=0.3,
        max_tokens=150,
        timeout=30,
    )
    return json.loads(response.choices[0].message.content.strip())


def _build_word_queries(word):
    """Build Q objects for a single search word."""
    return (
        Q(title__icontains=word)
        | Q(adjectives__icontains=word)
        | Q(ingredients__icontains=word)
        | Q(steps__icontains=word)
        | Q(author__username__icontains=word)
        | Q(author__first_name__icontains=word)
        | Q(author__last_name__icontains=word)
        | Q(full_name__icontains=word)
    )


def apply_search_query(recipes, search_query):
    """Apply text search across recipe fields."""
    if not search_query:
        return recipes

    recipes = recipes.annotate(
        full_name=Concat("author__first_name", Value(" "), "author__last_name")
    )

    combined_q = Q()
    for word in search_query.split():
        combined_q |= _build_word_queries(word)

    return recipes.filter(combined_q)


def apply_tag_filters(
    recipes, course_filters, dietary_filters, cuisine_filters, other_filters
):
    """Apply tag-based filters to recipes."""
    if course_filters:
        recipes = build_or_query(recipes, "course_tags", course_filters)
    if dietary_filters:
        recipes = build_or_query(recipes, "dietary_tags", dietary_filters)
    if cuisine_filters:
        recipes = build_or_query(recipes, "cuisine_tags", cuisine_filters)
    if other_filters:
        recipes = build_or_query(recipes, "other_tags", other_filters)
    return recipes


def build_or_query(recipes, tag_field, filter_values):
    """Build and apply OR query for a tag field."""
    tag_q = reduce(
        operator.or_,
        [Q(**{f"{tag_field}__icontains": value}) for value in filter_values],
    )
    return recipes.filter(tag_q)


def apply_sorting(recipes, sort_by):
    """Apply sorting to recipes."""
    if sort_by in SORT_OPTIONS:
        return recipes.order_by(SORT_OPTIONS[sort_by])

    if sort_by in ["total_least", "total_most"]:
        recipes = recipes.annotate(
            total_minutes=(F("prep_time_hours") + F("cook_time_hours")) * 60
            + (F("prep_time_minutes") + F("cook_time_minutes"))
        )
        return recipes.order_by(
            "total_minutes" if sort_by == "total_least" else "-total_minutes"
        )

    return recipes.order_by("-publication_date")


def _build_recipe_list(top_recipes):
    """Build recipe list for AI ranking."""
    return [
        {
            "id": recipe.id,
            "title": recipe.title,
            "tags": f"{getattr(recipe, 'course_tags', '')} {getattr(recipe, 'dietary_tags', '')}".strip(),
        }
        for recipe in top_recipes
    ]


def _build_ranking_prompt(user_context, recipe_list):
    """Build prompt for AI ranking."""
    return f"""Context: "{user_context}"
Recipes: {json.dumps(recipe_list, indent=2)}
Rank top 3. Return: {{"top_picks":[{{"recipe_id":123,"title":"Name","reason":"Why"}}],"search_explanation":"Strategy"}}"""


def get_ai_rankings(user_context, top_recipes):
    """Get AI to rank top recipes."""
    recipe_list = _build_recipe_list(top_recipes)
    ranking_response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Rank recipes. Return only JSON."},
            {
                "role": "user",
                "content": _build_ranking_prompt(user_context, recipe_list),
            },
        ],
        temperature=0.5,
        max_tokens=300,
    )
    return json.loads(ranking_response.choices[0].message.content.strip())


def build_view_all_url(
    search_query,
    course_filters,
    dietary_filters,
    cuisine_filters,
    other_filters,
    sort_by,
):
    """Build URL for view all results button."""
    url_params = []

    filter_map = {
        "course": course_filters,
        "dietary": dietary_filters,
        "cuisine": cuisine_filters,
        "other": other_filters,
    }
    for param_name, filter_values in filter_map.items():
        url_params = add_params_to_url(param_name, filter_values, url_params)

    url_params.append(f"sort={sort_by}")
    return "/all_recipes/?" + "&".join(url_params)


def add_params_to_url(param_name, filter_values, url_params):
    """Add filter parameters to url params list."""
    for value in filter_values:
        url_params.append(f"{param_name}={value}")
    return url_params


@login_required
def ai_recipe_search_view(request):
    """AI recipe search view."""
    if request.method != "POST":
        return render(request, "ai/ai_recipe_search.html")
    user_context = request.POST.get("context", "").strip()

    if not user_context:
        messages.error(request, "Please describe your situation")
        return render(request, "ai/ai_recipe_search.html")
    try:
        return process_ai_search(request, user_context)
    except Exception as e:
        message = ERROR_MESSAGES.get(type(e), DEFAULT_ERROR)
        messages.error(request, message)
        return render(
            request, "ai/ai_recipe_search.html", {"user_context": user_context}
        )


def process_ai_search(request, user_context):
    """Process AI search request."""
    search_params = get_search_params_from_ai(user_context)
    recipes = filter_recipes(search_params)

    if recipes.count() == 0:
        return render(
            request,
            "ai/ai_recipe_search.html",
            {
                "user_context": user_context,
                "search_params": search_params,
                "no_results": True,
                "show_results": True,
            },
        )
    return render_search_results(recipes, request, user_context, search_params)


def filter_recipes(search_params):
    """Filter recipes using search parameters."""
    recipes = Recipe.objects.visible()
    recipes = apply_search_query(recipes, search_params.get("search_query", "").strip())
    recipes = apply_tag_filters(
        recipes,
        search_params.get("course_filters", []),
        search_params.get("dietary_filters", []),
        search_params.get("cuisine_filters", []),
        search_params.get("other_filters", []),
    )
    return apply_sorting(recipes, search_params.get("sort_by", "date_newest"))


def build_result_context(
    user_context, search_params, ranking_data, total_count, view_all_url
):
    """Build context for search results."""
    top_picks = ranking_data.get("top_picks", [])
    recipe_ids = [pick["recipe_id"] for pick in top_picks]

    return {
        "user_context": user_context,
        "search_params": search_params,
        "search_explanation": ranking_data.get("search_explanation", ""),
        "top_picks": top_picks,
        "top_pick_ids": ",".join(map(str, recipe_ids)),
        "total_count": total_count,
        "view_all_url": view_all_url,
        "show_results": True,
    }


def render_search_results(recipes, request, user_context, search_params):
    """Render search results with AI rankings."""
    ranking_data = get_ai_rankings(user_context, recipes[:10])
    view_all_url = build_view_all_url(
        search_params.get("search_query", ""),
        search_params.get("course_filters", []),
        search_params.get("dietary_filters", []),
        search_params.get("cuisine_filters", []),
        search_params.get("other_filters", []),
        search_params.get("sort_by", ""),
    )
    context = build_result_context(
        user_context, search_params, ranking_data, recipes.count(), view_all_url
    )
    return render(request, "ai/ai_recipe_search.html", context)
