#!/bin/bash

tenantId=$1

services=" activityIngress mitui-video-playback antivirus mitui-videos baas-s3-broker mitui-videos-aws cloudnotification office365 content-translation phrase-substitution contentTranslation realtime-discovery core-phrasesubstitution rebuildSearchIndex core-translation recoactivity csm-aws recoactivity-aws dealroom recofollows digestrecommender recofollows-aws digestrecommender-aws recommendations directory recommendations-aws gala-app-service reconotify identity reconotify-aws if-crm-sfdc recorealtime jive-auth-cloud-analytics-aws recorealtime-aws jive-cloud-analytics rewards jive-cloud-analytics-aws rewards-recognition jive-cmr-cloud-analytics search jive-id-auth search.moreLikeThis jive-id-batphone search.query jive-id-profile searchIndexManage jive-id-public spam-prevention jive-id-ui spamprevention jive-im-cloud-analytics streamonce jive-im-cloud-analytics-aws unified-admin-aws jivewadmin vid-authorization-perceptive mitui-cloudalytics vid-delete-perceptive mitui-cloudalytics-aws vid-download-perceptive mitui-cloudalytics-export vid-embed mitui-cloudalytics-insights vid-registration-perceptive mitui-cloudalytics-insights-aws vid-status-perceptive mitui-comments vid-upload-perceptive mitui-people video-authorization-perceptive mitui-people-aws video-authorize-perceptive mitui-phrases video-delete-perceptive mitui-phrases-aws video-download-perceptive mitui-places video-embed mitui-places-aws video-regauth-perceptive mitui-profile video-register-perceptive mitui-profile-aws video-registration-perceptive mitui-userpanel video-status-perceptive mitui-userpanel-aws video-upload-perceptive mitui-video-browse zenx mitui-video-create"

for service in $services; do

  printf "\n==> Resetting secrets for tenantID [${tenantId}] service [${service}]\n"

  for i in {1..3}; do

  curl -s \
   -H 'Content-Type: application/json' \
   -d '{"customerSecretRequest":{"serviceName":"'${service}'", "systemId":"'${tenantId}'"},"instanceType":""}' \
     'http://tenancy-prod-app'${i}'.s1phx1.jivehosted.com:20000/purge/secret/services/tenantSecret/purge'

  done

done
printf "\n"
