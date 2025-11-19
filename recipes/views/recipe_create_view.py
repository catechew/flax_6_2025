from recipes.forms.recipe_form import RecipeForm, RecipeIngredientFormSet, RecipeStepFormSet
from django.views.generic.edit import CreateView
from django.urls import reverse
from recipes.models import Recipe, IngredientPrice
from django.db import transaction


class CreateRecipeView(CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'create_recipe.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredient_formset'] = RecipeIngredientFormSet(
                self.request.POST, 
                self.request.FILES,
                instance=self.object
            )
            context['step_formset'] = RecipeStepFormSet(
                self.request.POST, 
                self.request.FILES,
                instance=self.object
            )
        else:
            context['ingredient_formset'] = RecipeIngredientFormSet()
            context['step_formset'] = RecipeStepFormSet()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        step_formset = context['step_formset']
        # Debug: Print formset errors
        print("=== INGREDIENT FORMSET VALIDATION ===")
        print(f"Is valid: {ingredient_formset.is_valid()}")
        if not ingredient_formset.is_valid():
            print(f"Formset errors: {ingredient_formset.errors}")
            print(f"Non-form errors: {ingredient_formset.non_form_errors()}")

        print("=== STEP FORMSET VALIDATION ===")
        print(f"Is valid: {step_formset.is_valid()}")
        if not step_formset.is_valid():
            print(f"Formset errors: {step_formset.errors}")
            print(f"Non-form errors: {step_formset.non_form_errors()}")



        with transaction.atomic():
            # Save the recipe first
            self.object = form.save()

            # Save ingredients
            if ingredient_formset.is_valid():
                ingredient_formset.instance = self.object
                ingredients = ingredient_formset.save(commit=False)

                # Only save ingredients that have a name
                saved_count = 0
                for ingredient in ingredients:
                    if ingredient.name and ingredient.name.strip():  # Check for non-empty name
                        ingredient.order = saved_count
                        ingredient.save()
                        saved_count += 1

                        # Save price for future auto-fill
                        if ingredient.store and ingredient.price:
                            IngredientPrice.objects.update_or_create(ingredient_name=ingredient.name.lower().strip(),
                                store=ingredient.store,
                                defaults={'price': ingredient.price}
                            )
            else:
                # Rollback and show errors
                transaction.set_rollback(True)
                return self.form_invalid(form)

            # Save steps
            if step_formset.is_valid():
                step_formset.instance = self.object
                steps = step_formset.save(commit=False)

                # Only save steps that have instructions
                step_number = 1
                for step in steps:
                    if step.instruction and step.instruction.strip():  # Check for non-empty instruction
                        step.step_number = step_number
                        step.save()
                        step_number += 1
            else:
                # Rollback and show errors
                transaction.set_rollback(True)
                return self.form_invalid(form)
        print("=== SUCCESS - REDIRECTING ===")
        return super().form_valid(form)


    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_success_url(self):
        return reverse('all_recipes')