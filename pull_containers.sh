#!/bin/sh
docker pull quay.io/cdis/data-portal:master
docker pull quay.io/cdis/data-portal-prebuilt:brh.data-commons.org-feat-develop
docker pull bitnami/kubectl:latest
docker pull quay.io/cdis/awshelper:master
docker pull quay.io/cdis/workspace-token-service:feat_wts_internalfence
docker pull quay.io/cdis/fence:master
docker pull quay.io/cdis/metadata-service:master
docker pull quay.io/cdis/argo-wrapper:master
docker pull quay.io/cdis/audit-service:master
docker pull quay.io/cdis/fence:feat_dbenvvar
docker pull bitnami/postgresql:14.5.0-debian-11-r35
docker pull quay.io/cdis/hatchery:2022.10
docker pull quay.io/cdis/peregrine:2022.10
docker pull quay.io/cdis/indexd:2022.10
docker pull quay.io/cdis/pidgin:2022.10
docker pull quay.io/cdis/arborist:2022.10
docker pull quay.io/cdis/sheepdog:helm-test
docker pull quay.io/cdis/manifestservice:2022.09
docker pull quay.io/cdis/ssjdispatcher:2022.08
docker pull quay.io/datawire/ambassador:1.4.2
docker pull nginx:1.13.9-perl
echo "docker images pulled!!!"