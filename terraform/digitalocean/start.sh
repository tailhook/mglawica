#!/bin/sh -ex
terraform apply -var-file=key.tfvars
./tinc/start.sh
