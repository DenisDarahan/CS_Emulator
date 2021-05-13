#!/bin/bash

touch cs_emulator.prog

for file in $(find ./ -name '*.py' -or -name '*.kv');
do
    # cat "$file";
    cat "$file" | base64 >> cs_emulator.prog
done
