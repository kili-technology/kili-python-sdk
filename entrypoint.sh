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
    read -p 'Bump type (possible values are patch or minor): ' release_type
    if [ "$release_type" != "patch" ] && [ "$release_type" != "minor" ]
        then
            echo "Wrong Bump type. It should be minor or patch"
            exit 1
    fi
    read -p 'from commit (default: HEAD): ' commit
    commit="${commit:=HEAD}"

    git pull origin master -q

    #get the new version
    new_version= bump_version dry-run
    echo "New version: $new_version"

    #create a branch from the specified sha and and commit the version bump
    git checkout -B release/$new_version $commit
    new_version= bump_version commit
    echo "bump version commited : on the release branch"

}

create_release_branch


# function create-branch {
#     read -p 'Bump type: (possible options: minor or patch' uservar
# }

# if [[ "$1" == 'release:create-branch' ]]; then


# if [[ "$1" == 'release:publish' ]]; then

# if [[ "$1" == "bump:"* ]]
#   then
#     RELEASE_TYPE="$(echo $1 | cut -d: -f2)"
#     if [ "$RELEASE_TYPE" != "patch" ] && [ "$RELEASE_TYPE" != "minor" ]
#         then
#             echo "Wrong Bump type. It should be bump:minor or bump:patch"
#             exit 1
#     fi

#     if [ -z "$2" ]
#         then
#         COMMIT='HEAD'
#     else
#         COMMIT=$2
#     fi

#     #create or reset release branch
#     git checkout master
#     git pull origin master
#     git checkout -B release/bump-version-$(date +%s) $COMMIT

#     echo "Creating a new branch from master commit $COMMIT"

#     # increment version in the kili/__init__.py file and in setup.cfg
#     new_version=`bump2version \
#         --list \
#         --commit \
#         --current-version $(python -c 'from kili import __version__; print(__version__)') \
#         $RELEASE_TYPE \
#         kili/__init__.py \
#         | grep new_version | sed -r s,"^.*=",,`

#     echo "Bumping to version $new_version"
#     git push

#     gh pr create \
#         --fill \
#         --base master \
#         --reviewer theodu,PierreLeveau,mDuval1,p-desaintchamas,hugo-mailfait-kili

#     git checkout master
# fi
