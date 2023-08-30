retry_command() {
  local cmd="$1"
  local max_retries="${2:-15}"
  local retry_delay="${3:-60}"

  for ((i=1; i<=max_retries; i++)); do
    eval "$cmd"

    if [[ $? -eq 0 ]]; then
        echo "Command executed successfully!"
        return 0
    else
        echo "Attempt $i of $max_retries failed. Retrying in $retry_delay seconds..."
        sleep "$retry_delay"
    fi
  done

  echo "Failed to execute command after $max_retries attempts."
  exit 1
}
