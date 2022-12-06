# #!/bin/bash

# print cli arguments for debug
echo "cli arguments received (for debug):"
echo $@

function bump_version(){
    new_version=`bump2version \
        --list \
        --$1 \
        --current-version $(python -c 'from kili import __version__; print(__version__)') \
        $release_type \
        src/kili/__init__.py \
        | grep new_version | sed -r s,"^.*=",,`

    echo $new_version
}

function create_release_branch() {
    release_type=$2

    if [ "$release_type" != "patch" ] && [ "$release_type" != "minor" ]; then
        echo "Wrong Bump type. It should be minor or patch"
        exit 1
    fi

    commit=$3

    commit="${commit:=HEAD}"  # set commit to HEAD if commit variable is not given by the user

    git pull -q

    #get the new version
    new_version=$(bump_version dry-run)
    echo "New version: $new_version"

    #create a branch from the specified sha and commit the version bump
    git checkout -B release/$new_version $commit
    new_version=$(bump_version commit)
    if git push -f -q; then
        echo "version bump commited and pushed on the release branch"
        echo "Tests are launched on Github Actions: https://github.com/kili-technology/kili-python-sdk/actions"
    fi

}

function version_to_int { echo "$@" | awk -F. '{ printf("%d%03d%d\n", $1,$2,$3); }'; }

function get_latest_release {
    curl \
        --silent \
        "https://api.github.com/repos/kili-technology/kili-python-sdk/releases/latest" \
        | jq -r .tag_name
}

function create_draft_release {
    read -p 'Release (format: X.XX.X, default: current branch release): ' release
    if [ -z $release ]; then
        branch_name=$(git rev-parse --abbrev-ref HEAD)
        if [[ $branch_name != release/* ]]; then
            echo "You are currently not on a release branch. Please enter the release version on prompt or checkout on the release branch"
            exit 1
        fi
        release=$(echo $branch_name | cut -d/ -f2)
    else
        if ! git checkout release/$release; then
            exit 1
        fi
    fi

    latest_release=get_latest_release
    if [ $(version_to_int $latest_release) -ge $(version_to_int $release) ]; then
        echo "The release that you are trying to push is older than the latest release ($latest_release)"
        exit 1
    fi
    git tag -f -a $release -m "Release $release"
    git push origin $release

    if ! command -v gh &> /dev/null; then
        brew install gh
    fi

    gh release create $release \
        --draft \
        --title "Release $release" \
        --generate-notes

}

if [[ "$1" == 'release:branch' ]]; then
    create_release_branch
fi

if [[ "$1" == 'release:draft' ]]; then
    create_draft_release
fi
