#!/bin/bash
echo "removing old directories"
rm -rf build/*
rm -rf dist/*

echo "running svn up"
svn up

echo "running py2app"
python setup.py py2app
cd dist

echo "producing zip"
zip -r -9 mactorii.app.zip mactorii.app
cd ../

echo "done"
