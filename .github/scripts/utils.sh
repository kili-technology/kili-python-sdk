#!/bin/bash

get_sdk_version() {
    sdk_version=$(cat setup.cfg | grep current_version | cut -d ' ' -f 3)
    echo "$sdk_version"
}

# $1: commit or dry-run
# $2: release type (minor, patch or major)
bump_version() {
    new_version=$(bump2version \
        --list \
        --"$1" \
        --current-version "$(get_sdk_version)" \
        "$2" \
        src/kili/__init__.py \
        | grep new_version | sed -r s,"^.*=",,)

    echo "$new_version"
}

# Takes the version to convert to int
# 2.129.0 -> 21290
version_to_int() {
    echo "$@" | awk -F. '{ printf("%03d%03d%03d\n", $1,$2,$3); }';
}

get_last_release_tag_github() {
    last_tag=$(curl --silent "https://api.github.com/repos/kili-technology/kili-python-sdk/releases/latest" | jq -r .tag_name)
    echo "$last_tag"
}
