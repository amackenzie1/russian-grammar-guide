#!/usr/bin/env bash
# Build the guide and publish it.
#
# The live copy is one HTML file inside a site that AWS Amplify deploys from an S3 prefix, so
# publishing means: upload guide.html as <prefix>/russian/index.html, then ask Amplify to redeploy
# the prefix. Settings come from the environment (in CI) or from a local, uncommitted .deploy.env:
#
#   DEPLOY_BUCKET, DEPLOY_PREFIX, AMPLIFY_APP_ID, AMPLIFY_BRANCH, AWS_REGION
#   GUIDE_POSTHOG_KEY (optional: turns on page analytics)
#
# Locally, run it with credentials, e.g.  aws-vault exec <profile> -- tools/deploy.sh
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -f .deploy.env ]; then set -a; . ./.deploy.env; set +a; fi
: "${DEPLOY_BUCKET:?set DEPLOY_BUCKET}" "${AMPLIFY_APP_ID:?set AMPLIFY_APP_ID}"
prefix="${DEPLOY_PREFIX:-site}"
branch="${AMPLIFY_BRANCH:-main}"
region="${AWS_REGION:-us-east-1}"

uv run tools/lint.py >/dev/null || { echo "lint failed; run: uv run tools/lint.py" >&2; exit 1; }
uv run tools/build.py
aws s3 cp guide.html "s3://$DEPLOY_BUCKET/$prefix/russian/index.html" \
  --content-type "text/html; charset=utf-8" --region "$region" --only-show-errors
aws amplify start-deployment --app-id "$AMPLIFY_APP_ID" --branch-name "$branch" \
  --source-url "s3://$DEPLOY_BUCKET/$prefix/" --source-url-type BUCKET_PREFIX --region "$region" \
  --query jobSummary.jobId --output text
