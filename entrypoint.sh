#!/bin/bash

# Usage:
# - To create a release branch:
# ./entrypoint.sh release:branch <bump_type> <commit_hash>
# bump_type: minor or patch.
# commit_hash: no argument will default to HEAD. Else, the commit hash provided.

# - To create a draft release:
# ./entrypoint.sh release:draft <release_number>
# release_number: release branch number. Format: X.XX.X (default: current branch)

# Requirements: gh, bump2version, git, curl

# $1: commit or dry-run
# $2: release type (minor or patch)
function bump_version() {
    new_version=`bump2version \
        --list \
        --$1 \
        --current-version $(python -c 'from kili import __version__; print(__version__)') \
        $2 \
        src/kili/__init__.py \
        | grep new_version | sed -r s,"^.*=",,`

    echo $new_version
}

function create_release_branch() {
    release_type=$1

    if [ "$release_type" != "patch" ] && [ "$release_type" != "minor" ]; then
        echo "Wrong Bump type. It should be minor or patch. Received: $release_type"
        exit 1
    fi

    commit=$2

    commit="${commit:=HEAD}"  # set commit to HEAD if commit variable is null
    echo "commit: $commit"

    git pull --quiet

    # get the new version
    new_version=$(bump_version dry-run $release_type)
    echo "New version (bump_version dry-run): $new_version"

    # create a branch from the specified sha and commit the version bump
    git checkout -B release/$new_version $commit

    # create version bump commit
    new_version=$(bump_version commit $release_type)
    echo "New version (bump_version commit): $new_version"

    if git push --quiet --set-upstream origin release/$new_version; then
        echo "version bump commited and pushed on the release branch"
        echo "Tests are launched on Github Actions: https://github.com/kili-technology/kili-python-sdk/actions"
    else
        echo "Failed to push release branch"
        exit 1
    fi

}

function version_to_int { echo "$@" | awk -F. '{ printf("%d%03d%d\n", $1,$2,$3); }'; }

function get_latest_release {
    curl \
        --silent \
        "https://api.github.com/repos/kili-technology/kili-python-sdk/releases/latest" \
        | jq -r .tag_name
}

function create_draft_release() {
    release_version=$1

    # Checkout to the release branch
    if [ -z $release_version ]; then
        branch_name=$(git rev-parse --abbrev-ref HEAD)
        if [[ $branch_name != release/* ]]; then
            echo "You are currently not on a release branch. Please enter the release version on prompt or checkout on the release branch"
            exit 1
        fi
        release_version=$(echo $branch_name | cut -d/ -f2)
    else
        if ! git checkout release/$release_version; then
            echo "Failed to checkout on branch: release/$release_version"
            exit 1
        fi
    fi

    # make sure new version is greater or equal than last release
    latest_release=get_latest_release
    if [ $(version_to_int $latest_release) -ge $(version_to_int $release_version) ]; then
        echo "The release that you are trying to push is older than the latest release ($latest_release)"
        exit 1
    fi

    # tag and push the tag
    git tag -f -a $release_version -m "Release $release_version"
    git push origin $release_version

    # install gh if needed on macOS
    if [[ $OSTYPE == 'darwin'* ]] && ! [[ -x "$(command -v gh)" ]]; then
        brew install gh
    fi

    # create draft release
    link_to_draft=$(gh release create $release_version --draft --title "Release $release_version" --generate-notes)

    echo $link_to_draft
}

if [[ "$1" == 'bump_version' ]]; then
    bump_version $2 $3 # pass (commit/dry-run) and bump type (minor/patch)
fi

if [[ "$1" == 'release:branch' ]]; then
    create_release_branch $2 $3  # pass bump type (minor or patch) and commit hash to create branch from
fi

if [[ "$1" == 'release:draft' ]]; then
    create_draft_release $2  # pass release version number
fi