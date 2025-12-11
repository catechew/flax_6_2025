import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dotenv import load_dotenv
import json
import openai
import re

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")


def _build_recipe_prompt(user_prompt):
    """Build AI prompt for recipe generation."""
    template = '{"title":"Name","description":"Brief","prep_time":"15 min","cook_time":"30 min","servings":4,"difficulty":"Easy","ingredients":["item"],"steps":["step"],"tips":[],"dietary_info":[]}'
    return f'Request: "{user_prompt}"\n\nCreate recipe as JSON (no markdown):\n{template}\n\nReturn ONLY JSON.'


def _get_openai_config():
    """Get OpenAI API configuration."""
    return {
        "model": "gpt-4o-mini",
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
        "max_tokens": 1000,
        "timeout": 30,
    }


def _call_openai_for_recipe(user_prompt):
    """Call OpenAI API to generate recipe."""
    config = _get_openai_config()
    response = openai.ChatCompletion.create(
        messages=[
            {
                "role": "system",
                "content": "Professional chef. Generate recipes as JSON only. No markdown.",
            },
            {"role": "user", "content": _build_recipe_prompt(user_prompt)},
        ],
        **config,
    )
    return response.choices[0].message.content.strip()


def generate_recipe_with_ai(user_prompt):
    """Generate a complete recipe based on user's description."""
    ai_response = _call_openai_for_recipe(user_prompt)
    ai_response = _clean_json_response(ai_response)
    return json.loads(ai_response)


def _clean_json_response(response):
    """Remove markdown code blocks from AI response."""
    response = re.sub(r"^```json\s*", "", response)
    response = re.sub(r"\s*```$", "", response)
    return response.strip()


def _get_error_message(exception):
    """Map exception types to user-friendly error messages."""
    if isinstance(exception, json.JSONDecodeError):
        return "AI returned invalid format. Please try again."
    if isinstance(exception, openai.error.Timeout):
        return "Request timed out. Please try again."
    if isinstance(exception, openai.error.APIError):
        return f"OpenAI API error: {str(exception)}"
    return f"An error occurred: {str(exception)}"


def _handle_recipe_generation(user_prompt, request):
    """Handle recipe generation and return context."""
    recipe_data = generate_recipe_with_ai(user_prompt)
    request.session["last_ai_recipe"] = recipe_data
    return {"user_prompt": user_prompt, "recipe": recipe_data, "show_results": True}


@login_required
def ai_recipe_generator_view(request):
    """AI Recipe Generator - creates new recipes from user prompts."""
    if request.method != "POST":
        return render(request, "ai/ai_recipe_generator.html")

    user_prompt = request.POST.get("prompt", "").strip()
    if not user_prompt:
        messages.error(request, "Please describe what you want to cook")
        return render(request, "ai/ai_recipe_generator.html")
    try:
        context = _handle_recipe_generation(user_prompt, request)
        return render(request, "ai/ai_recipe_generator.html", context)
    except Exception as e:
        messages.error(request, _get_error_message(e))
        return render(
            request, "ai/ai_recipe_generator.html", {"user_prompt": user_prompt}
        )
