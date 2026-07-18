#!/usr/bin/env bash

# Hacky script to determine which of the Green-Blue deployments is active.
#
# Input: none
# Output: 'green', 'blue', or 'none', depending which deployment appears to be active
#
# It works by interrogating route53 for which load balancer the production URL is pointing to. It assumes that the
# load balancer name contains the word "green" or "blue" as appropriate.
#
#
# Note: it guesses. Not 100% reliable and brittle to changes in AWS.

ZONE_ID='Z1KPE8ISFGCJNT'
PROD_URL='v1.esp.evolution.ml.'

aws route53 list-resource-record-sets \
    --hosted-zone-id ${ZONE_ID} \
    --query "ResourceRecordSets[?Name=='$PROD_URL']" \
    | jq '.[]| .ResourceRecords[].Value' \
    | grep --extended-regexp --only-matching '(green|blue)' || echo 'none'

