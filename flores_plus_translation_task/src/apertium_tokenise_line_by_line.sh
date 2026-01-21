#!/bin/bash

# 1. Configuration (Check these paths!)
automorf=/usr/share/apertium/apertium-eng-spa/spa-eng.automorf.bin
tagger=/usr/share/apertium/apertium-eng-spa/spa-eng.prob

# 2. Initialize counter
count=1

# 3. Process Line by Line
while IFS= read -r line; do
    echo "Processing line $count..."

    echo "$line" \
    | apertium-destxt \
    | lt-proc "$automorf" \
    | apertium-tagger -g "$tagger" \
    | sed 's/\[[^]]*\]/ /g'         `# 1. Replace artifacts with a space` \
    | sed 's/<[^>]*>//g'            `# 2. Remove tags (<n>, <adj>)` \
    | sed 's/\^[^/]*\///g'          `# 3. Remove surface form (^word/)` \
    | tr -d '^'                     `# 4. Clean stray start markers` \
    | sed 's/\$[[:space:]]*/$/g'    `# 5. Remove spaces after the $ marker` \
    | tr '$' '\n'                   `# 6. Convert $ markers to Newlines` \
    | tr -d '^' \
    | tr -d '[' \
    | tr -d ']' \
    | tr -d '*' \
    | tr -d '.' \
    | tr -d ',' \
    | grep -v '^$'                  `# 7. Remove empty lines` \
    > "../data/tokens/$2/${count}.txt"

    ((count++))
done < "$1"
