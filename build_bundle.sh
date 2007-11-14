#!/bin/bash

python setup.py py2app
cd dist
rm mactorii.app.zip
zip -r -9 mactorii.app.zip mactorii.app
cd ../
