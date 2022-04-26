# KILI SDK docs

The Kili SDK doc is created with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), a theme for MkDocs which is a static site generator geared towards technical project documentation.
The webiste is hosted in Github Pages [here](https://kili-technology.github.io/kili-playground/)

## install dependencies:

```
pip install -r requirements.txt
```

## HTML Preview

Automatically reloads when you edit a file.

```
mike serve
```

## List all versions

```
mike list
```

## create a new version

```
mike deploy [version: X.XX] [alias]...
```

The version with the tag `latest` will always be opened by default when asking for the root url of the doc
If you push the last version, please put `lastest` as alias and overwrite the previous version alias with:

```
mike deploy --update-aliases [version: X.XX] latest
```

## Publish the doc to the website

The documentation website is hosted on Github Pages based in the files on the branch `gh-pages` of Kili SDK.
To push a new documentation to the website, just deploy the new version on the branch `gh-pages` by adding the `--push` argument to the deploy command:

```
git fetch origin gh-pages --depth=1
mike deploy --push [version: X.XX] [alias]...
```

or by updating the alias:

```
git fetch origin gh-pages --depth=1
mike deploy --push --update-aliases [version: X.XX] latest
```

## Delete a version:

```
mike delete [version-or-alias]...
```

## Troubleshooting

Read the Mike docs here: https://github.com/jimporter/mike
Read the Material for MK docs here: https://squidfunk.github.io/mkdocs-material/getting-started/
