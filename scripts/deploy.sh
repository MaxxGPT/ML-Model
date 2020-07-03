#!/bin/bash

# Exit upon encountering an error
set -euo pipefail

# Set the base route
ROOT_DIR=$(pwd)

# Run the script to set up the env variables and other custom functions
source $ROOT_DIR/scripts/utilis.sh

checkcommitmessage() {
  info "Checking commit message"
  COMMIT_MESSAGE=`git log --format=%B -n 1 $BITBUCKET_COMMIT`
  messagecheck=`echo $COMMIT_MESSAGE | grep -w "#manualrun"`
  if [ -z "$messagecheck" ]
  then
    error "Your commit message not contains #manualrun"
  else
    info "Initializing jenkins to start"
  fi
}
checkcommitmessage
