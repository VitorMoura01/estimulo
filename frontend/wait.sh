#!/bin/bash

service="$1"
port="$2"
shift 2
cmd="$@"

is_service_available() {
  nc -z "$service" "$port" && return 0 || return 1
}

while ! is_service_available; do
  echo "Flask is unavailable - sleeping"
  sleep 1
done

exec $cmd
