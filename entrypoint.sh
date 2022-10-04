# #!/bin/bash

function bump_version(){
    new_version=`bump2version \
        --list \
        --$1 \
        --current-version $(python -c 'from kili import __version__; print(__version__)') \
        $release_type \
        kili/__init__.py \
        | grep new_version | sed -r s,"^.*=",,`

    echo $new_version
}

function create_release_branch() {
    read -p 'Bump type (possible values: patch or minor): ' release_type
    if [ "$release_type" != "patch" ] && [ "$release_type" != "minor" ]
        then
            echo "Wrong Bump type. It should be minor or patch"
            exit 1
    fi
    read -p 'from commit (default: HEAD): ' commit
    commit="${commit:=HEAD}"

    git pull origin master -q

    #get the new version
    new_version=$(bump_version dry-run)
    echo "New version: $new_version"

    #create a branch from the specified sha and and commit the version bump
    git checkout -B release/$new_version $commit
    new_version=$(bump_version commit)
    echo "version bump commited on the release branch"

}

if [[ "$1" == 'release:create-branch' ]]; then
    create_release_branch
fi
