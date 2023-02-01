#!/bin/bash

# Script that determines the test server to run the tests against.
# The test server is echoed in stdout
# To get test server, parse: TEST_AGAINST=<value>;
# To get endpoint, parse: KILI_API_ENDPOINT=<value>;

current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "current_branch: $current_branch"

if [[ $current_branch = release/* ]]; then
    # we are on a release branch, test against preprod or prod
    sdk_version=$(cat setup.cfg | grep current_version | cut -d ' ' -f 3)
    echo "sdk_version: $sdk_version"
    IFS=. read -r sdk_major sdk_minor sdk_patch <<< "$sdk_version"

    if [[ "$sdk_patch" == "0" ]]; then
        # minor release, we test against preprod
        echo "TEST_AGAINST=PREPROD;"
        echo "KILI_API_ENDPOINT=https://preproduction.cloud.kili-technology.com/api/label/v2/graphql;"
    else
        # patch release, we test against prod
        echo "TEST_AGAINST=PROD;"
        echo "KILI_API_ENDPOINT=https://cloud.kili-technology.com/api/label/v2/graphql;"
    fi

else
    # master or dev branch, we test against staging
    echo "TEST_AGAINST=STAGING;"
    echo "KILI_API_ENDPOINT=https://staging.cloud.kili-technology.com/api/label/v2/graphql;"
fi
