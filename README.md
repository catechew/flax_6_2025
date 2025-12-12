# Team *Flax 6* Small Group project

## Team members
The members of the team are:
- *Arvin Hadidi-Fard*
- *Cate Tay Chew*
- *Hamed Latif*
- *Katherine Wanting Zhao*
- *Kausar Khan*

## Project structure
The project is called `recipify`.  It currently consists of a single app `recipes`.

## Deployed version of the application
The deployed version of the application can be found at [*https://hamed54.pythonanywhere.com/*](*https://hamed54.pythonanywhere.com/*).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  The project source code has been developed using Python 3.12, so you are recommended to use the same version.  From the root of the project:

```
$ python3.12 -m venv venv
$ source venv/bin/activate
```

If your system does not have `python3.12` installed and you are unable to install Python 3.12 as a version you can explicitly refer to from the CLI, then replace `python3.12` by `python3` or `python`, provide this employs a relatively recent version of Python.

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests and coverage with:
```
$ python3 manage.py test

$ python -m coverage erase
$ python -m coverage run manage.py test
$ python -m coverage report
$ coverage html
$ open htmlcov/index.html
```

If you are an admin, you can access the admin panel by adding /admin to the link, i.e. https://hamed54.pythonanywhere.com/admin/login/?next=/admin/

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

During development, our team occasionally used Microsoft Copilot and GitHub Copilot to support learning, debugging, and clarification of concepts. These tools were **not** used to generate project code; instead, they served as supplementary resources in the same way documentation or online tutorials would.

Examples of appropriate use included:
- Clarifying Python and Django documentation and functions (e.g., explaining views, models, and routing concepts).
- Providing guidance during complex Git operations (e.g., resolving merge conflicts, understanding rebasing workflows).
- Offering general explanations of HTML/CSS behaviour and UI structuring principles.

All final implementation decisions, code, design patterns, and architectural choices were made by the team.
**No AI tools were used to automatically generate functional components, models, views, templates, or tests.**
