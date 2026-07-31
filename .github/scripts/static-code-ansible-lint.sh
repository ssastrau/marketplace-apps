#!/usr/bin/env bash

set -e

if [ -n "$CONFIGS" ]; then
	LINT_PATHS=$(echo "$CONFIGS" | jq -r '.[] | "apps/" + .' | tr '\n' ' ')
	echo "Linting updated apps: $LINT_PATHS"
else
	LINT_PATHS=""
	echo "Linting all apps"
fi

pip install ansible-lint
ansible-galaxy collection install community.general community.docker community.postgresql community.crypto community.mysql community.mongodb community.rabbitmq
export ANSIBLE_CONFIG="tests/static_code_analysis/ansible_playbooks/ansible.cfg"
ansible-lint -c tests/static_code_analysis/ansible_playbooks/.ansible-lint.yaml $LINT_PATHS
echo "✅ ansible-lint passed: no errors found."
