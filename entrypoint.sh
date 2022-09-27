#!/bin/bash

if [[ "$1" == "bump:"* ]]
  then
    RELEASE_TYPE="$(echo $1 | cut -d: -f2)"
    if [ "$RELEASE_TYPE" != "patch" ] && [ "$RELEASE_TYPE" != "minor" ]
        then
            echo "Wrong Bump type. It should be bump:minor or bump:patch"
            exit 1
    fi

    if [ -z "$2" ]
        then
        COMMIT='HEAD'
    else
        COMMIT=$2
    fi

    #create or reset release branch
    git checkout master
    git pull origin master --tags
    git checkout -B release/bump-version-$(date +%s) $COMMIT

    echo "Creating a new branch from master commit $COMMIT"

    # increment version in the kili/__init__.py file and in setup.cfg
    new_version=`bump2version \
        --list \
        --commit \
        --current-version $(python -c 'from kili import __version__; print(__version__)') \
        $RELEASE_TYPE \
        kili/__init__.py \
        | grep new_version | sed -r s,"^.*=",,`

    echo "Bumping to version $new_version"
    git tag -a $new_version -m "Release $new_version"
    git push origin master --tags

    gh pr create \
        --fill \
        --base master \
        --reviewer theodu,PierreLeveau,mDuval1,p-desaintchamas,hugo-mailfait-kili

    git checkout master
fi
