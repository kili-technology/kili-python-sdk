# Testing the repo


## Pylint

- Go to the folder repository.
- `pip install pylint`
- `pylint kili`

## Recipes

```bash
# Export the right environment variables 
export KILI_API_ENDPOINT=https://staging.cloud.kili-technology.com/api/label/v2/graphql
export KILI_API_KEY=...
export KILI_USER_EMAIL=...
export KILI_USER_ID=...

# Install dependencies
pip install jupyter nbconvert nbformat pytest

# Run pytest
pytest
```

**Add a recipe to the list of tested recipes**

Add an entry to `RECIPES_TESTED` in `test_notebooks.py`.