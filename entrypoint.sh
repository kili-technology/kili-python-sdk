if [ $# -eq 0 ]
  then
    echo "No release type argument supplied. Release type should be minor or patch."
fi
RELEASE_TYPE=$1
#create release branch
git checkout -b release/

# increment version in the kili/__init__.py file and in setup.cfg
new_version=`bump2version \
  --list \
  --commit \
  --current-version $(python -c 'from kili import __version__; print(__version__)') \
  $RELEASE_TYPE \
  kili/__init__.py \
  | grep new_version \
  | sed -r s,"^.*=",,`
git push

#release a draft version
gh release create $new_version \
    --title "Release $new_version" \
    --draft \
    --generate-notes
    --target "release/$new_version"