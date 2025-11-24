import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
import openai


openai.api_key = os.environ.get('OPENAI_API_KEY')
print(f"=== API KEY: {os.environ.get('OPENAI_API_KEY', 'NOT SET')[:20]}...")


@login_required
def ai_recipe_finder_view(request):
    """
    AI Recipe Finder - handles both displaying the form and processing results.
    No JavaScript needed - all server-side rendering.
    """
    
    if request.method == 'POST':
        user_context = request.POST.get('context', '').strip()
        print(f"=== RECEIVED CONTEXT: {user_context}")  # Debugging print, there will be a few of these
        
        if not user_context:
            messages.error(request, 'Please describe your situation')
            return render(request, 'ai_recipe_finder.html')
        
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
        
        print(f"=== GOT RESPONSE: {response}")  # ADD THIS
        # get ai's response
        ai_response = response.choices[0].message.content.strip()
        print(f"=== API RESPONSE 1: {ai_response}")  # ADD THIS
        
        # Clean markdown formatting
        if ai_response.startswith('```'):
            ai_response = ai_response.split('```')[1]
            if ai_response.startswith('json'):
                ai_response = ai_response[4:]
            ai_response = ai_response.strip()
        
        # get search parameters from ai's response
        search_params = json.loads(ai_response)

    # GET request - just show the form
    return render(request, 'ai_recipe_finder.html')
        
