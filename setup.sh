#!/usr/bin/bash

# Install requirements
pip install docker gitpython

for d in ./*; do
    if [ ! -d "$d" ]; then
        continue
    fi;
    if [ -f "${d}"/build.py ]; then
        echo "Find no build.py for ${d}"
        continue
    fi;
    # Generate Dockerfile if needed
    if grep -q generate .stages; then
        echo "Generating ${d}"
        python setup.py --mode=generate
    fi;
    # Build docker image
    if grep -q build .stages; then
        echo "Building ${d}"
        python setup.py --mode=build --path=/tmp/"${d}"
    fi;
done;