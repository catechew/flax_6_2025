import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dotenv import load_dotenv
import json
import openai
import re

# Load .env file to get API key
load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')


def generate_recipe_with_ai(user_prompt):
    """
    Generate a complete recipe based on user's description/request.
    Returns structured recipe data.
    """
    ai_prompt = f"""Based on this request: "{user_prompt}"

Create a complete recipe. Return ONLY valid JSON with no markdown formatting:
{{
    "title": "Recipe Name",
    "description": "Brief 1-2 sentence description",
    "prep_time": "15 minutes",
    "cook_time": "30 minutes",
    "servings": 4,
    "difficulty": "Easy/Medium/Hard",
    "ingredients": [
        "ingredient 1 with measurement",
        "ingredient 2 with measurement"
    ],
    "steps": [
        "Step 1 detailed instruction",
        "Step 2 detailed instruction"
    ],
    "tips": ["Optional cooking tip 1", "Optional tip 2"],
    "dietary_info": ["vegetarian", "gluten-free"] or []
}}

IMPORTANT: Return ONLY the JSON object, no markdown code blocks, no extra text."""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a professional chef. Generate complete, practical recipes with precise measurements and clear instructions. Return ONLY valid JSON with no markdown formatting or code blocks."
            },
            {
                "role": "user",
                "content": ai_prompt
            }
        ],
        response_format={"type": "json_object"},  # Force JSON mode
        temperature=0.7,
        max_tokens=1000,
        timeout=30
    )

    ai_response = response.choices[0].message.content.strip()

    # Remove markdown code blocks if present (just in case)
    ai_response = re.sub(r'^```json\s*', '', ai_response)
    ai_response = re.sub(r'\s*```$', '', ai_response)
    ai_response = ai_response.strip()

    return json.loads(ai_response)


@login_required
def ai_recipe_generator_view(request):
    """
    AI Recipe Generator - creates new recipes from user prompts
    """
    if request.method != 'POST':
        return render(request, 'ai_recipe_generator.html')

    user_prompt = request.POST.get('prompt', '').strip()

    if not user_prompt:
        messages.error(request, 'Please describe what you want to cook')
        return render(request, 'ai_recipe_generator.html')

    try:
        # Generate recipe using AI
        recipe_data = generate_recipe_with_ai(user_prompt)

        context = {
            'user_prompt': user_prompt,
            'recipe': recipe_data,
            'show_results': True
        }

        return render(request, 'ai_recipe_generator.html', context)

    except json.JSONDecodeError as e:
        messages.error(request, 'AI returned invalid format. Please try again.')
        return render(request, 'ai_recipe_generator.html', {'user_prompt': user_prompt})

    except openai.error.Timeout:
        messages.error(request, 'Request timed out. Please try again.')
        return render(request, 'ai_recipe_generator.html', {'user_prompt': user_prompt})

    except openai.error.APIError as e:
        messages.error(request, f'OpenAI API error: {str(e)}')
        return render(request, 'ai_recipe_generator.html', {'user_prompt': user_prompt})

    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'ai_recipe_generator.html', {'user_prompt': user_prompt})