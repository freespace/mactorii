#!/bin/bash
echo "removing old directories"
rm -rf build/*
rm -rf dist/*

echo "discovering version"
ver=$(svn info | grep Revision | cut -d ' ' -f 2);
echo ver=\"$ver\" > svn_version.py

echo "running py2app"
python setup.py py2app
cd dist

echo "producing zip"
zip -r -9 mactorii.app.zip mactorii.app
cd ../

echo "done"
