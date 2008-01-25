#!/bin/bash
echo "removing old directories"
rm -rf build/*
rm -rf dist/*

echo "running py2ap"

python setup.py py2app
cd dist

echo "producing zip"
zip -r -9 mactorii.app.zip mactorii.app
cd ../

echo "done"
