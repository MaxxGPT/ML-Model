#!/bin/bash

# Exit upon encountering an error
set -euo pipefail

# Set the base route
ROOT_DIR=$(pwd)

# Run the script to set up the env variables and other custom functions
source $ROOT_DIR/scripts/utilis.sh

sendsqsrequest(){
  info "sending sqs request"
  is_success_or_fail $(aws sqs send-message --queue-url $QUEUEURL --message-body "bitbukcet manualrun trigger" --region=$AWS_REGION)
}
main () {
    sendsqsrequest
}

main