#!/bin/bash

if [[ "$1" == "bump:"* ]]
  then
    RELEASE_TYPE="$(echo $1 | cut -d: -f2)"
    if [ "$RELEASE_TYPE" != "patch" ] && [ "$RELEASE_TYPE" != "minor" ]
        then
            echo "Wrong Bump type. It should be bump:minor or bump:patch"
            exit 1
    fi

    #create or reset release branch
    git checkout master
    git pull
    git checkout -B release/bump-version

    # increment version in the kili/__init__.py file and in setup.cfg
    new_version=`bump2version \
        --list \
        --commit \
        --current-version $(python -c 'from kili import __version__; print(__version__)') \
        $RELEASE_TYPE \
        kili/__init__.py \
        | grep new_version | sed -r s,"^.*=",,`

    echo "Bumping to version $new_version"
    git push

    gh pr create \
        --fill \
        --base master \
        --reviewer theodu,PierreLeveau,mDuval1,p-desaintchamas,hugo-mailfait-kili

    git checkout master
fi
