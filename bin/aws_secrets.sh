if [[ $1 == "AWS_ACCESS_KEY_ID" ]]; then
  if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    value="$(awk -F' = ' ' $1 == "aws_access_key_id" {print $2; exit}' "$HOME"/.aws/credentials)"
  else
    value="$AWS_ACCESS_KEY_ID"
  fi
else
  if [[ -z "$AWS_SECRET_ACCESS_KEY" ]]; then
    value="$(awk -F' = ' '$1 == "aws_secret_access_key" {print $2; exit}' "$HOME"/.aws/credentials)"
  else
    value="$AWS_SECRET_ACCESS_KEY"
  fi
fi

echo "$value"
