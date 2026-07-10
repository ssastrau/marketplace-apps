#!/bin/bash

# custom env variables from cli
if [[ -n ${INSTANCE_ENV} ]]; then
	custom_vars=(${INSTANCE_ENV})
	var_count=${#custom_vars[@]}
	count=0
	while [ ${count} -lt ${var_count} ]; do
		export ${custom_vars[count]}
		count=$(($count + 1))
	done
fi

# This app has no operator-facing UDFs (see architecture_decisions.md D1 — no user_name/domain,
# matching cpanel-almalinux/cpanel-ubuntu precedent). MODE defaults to production inside
# openlitespeed-cpanel-deploy.sh's udf() function when unset.
