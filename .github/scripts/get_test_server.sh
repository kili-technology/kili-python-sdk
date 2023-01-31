#!/bin/bash

# Script that determines the test server to run the tests against.

current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "current_branch: $current_branch"

if [[ $current_branch = release/* ]]; then
    sdk_version=$(cat setup.cfg | grep current_version | cut -d ' ' -f 3)
    echo "sdk_version: $sdk_version"
    IFS=. read -r major minor patch <<< "$sdk_version"
    sdk_version_major_minor="$major.$minor"

    prod_version=$(curl --silent "https://cloud.kili-technology.com/api/label/v2/version" | jq -r .version)
    echo "prod_version: $prod_version"
    IFS=. read -r major minor patch <<< "$prod_version"
    prod_version_major_minor="$major.$minor"

    preprod_version=$(curl --silent "https://preproduction.cloud.kili-technology.com/api/label/v2/version" | jq -r .version)
    echo "preprod_version: $preprod_version"
    IFS=. read -r major minor patch <<< "$preprod_version"
    preprod_version_major_minor="$major.$minor"

    if [[ $sdk_version_major_minor = $preprod_version_major_minor ]]; then
        echo "TEST_AGAINST=PREPROD"
        echo "KILI_API_ENDPOINT=https://preproduction.cloud.kili-technology.com/api/label/v2/graphql"
    elif [[ $sdk_version_major_minor = $prod_version_major_minor ]]; then
        echo "TEST_AGAINST=PROD"
        echo "KILI_API_ENDPOINT=https://cloud.kili-technology.com/api/label/v2/graphql"
    else
        echo "ERROR: SDK version $sdk_version_major_minor does not match neither preprod version $preprod_version nor prod version $prod_version"
    fi
else
    echo "TEST_AGAINST=STAGING"
    echo "KILI_API_ENDPOINT=https://staging.cloud.kili-technology.com/api/label/v2/graphql"
fi
