#!/bin/bash
set -e

if [ "$JOB_RESULT" == "success" ]; then
  HEADER_TEXT="✅ All Deployments Succeeded"
  FAILED_APPS_TEXT=""
else
  HEADER_TEXT="❌ Deployment(s) Failed"
  FAILED_APPS_TEXT="*Failed Apps:* ${FAILED_APPS}
"
fi

jq -n \
  --arg result "$JOB_RESULT" \
  --arg header "$HEADER_TEXT" \
  --arg workflow "$WORKFLOW_NAME" \
  --arg failed "$FAILED_APPS_TEXT" \
  --arg url "$RUN_URL" \
  '{
    "text": "Deployment Workflow Result: \($result)",
    "blocks": [
      {
        "type": "header",
        "text": {
          "type": "plain_text",
          "text": $header,
          "emoji": true
        }
      },
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Workflow:* \($workflow)\n*Status:* `\($result)`\n\($failed)<\($url)|Click here to view the run details.>"
        }
      }
    ]
  }' > slack-payload.json
