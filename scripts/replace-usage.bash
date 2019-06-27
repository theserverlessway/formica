#!/bin/bash

set -euo pipefail

command_files=$(ls docs/commands/*.md | grep -v 'index')

for file in $command_files
do
  echo "Updating Usage in $file"
  command=$(echo $file | sed 's/.*\/.*\/\(.*\).md/\1/g' | sed 's/_/ /g')
  sed -i '/^## Usage/Q' $file
  echo -e '## Usage\n\n```' >> ./$file
  formica $command --help >> ./$file
  echo '```' >> ./$file
done