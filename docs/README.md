# KILI SDK docs

## HTML Preview

Automatically reloads when you edit a file.

```
cd docs
make serve
```

## Build website

Builds to webiste. has to be done before to publish it.

```
make mkdocs build
```

## Publish

```
make mkdocs gh-deploy --force
```

Pushes to the `gh-deploy` branch and republishes as github pages.
