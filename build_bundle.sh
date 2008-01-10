#!/bin/bash

rm -rf build/*
rm -rf dist/*

python setup.py py2app
cd dist
zip -r -9 mactorii.app.zip mactorii.app
cd ../
