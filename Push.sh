#!/bin/bash
#Stupid way to push to git with one command.
echo "Cleaning.."
find . -name ".DS_Store" -print0 | xargs -0 rm -rf > /dev/null
find . -name "._*" -print0 | xargs -0 rm -rf > /dev/null
echo  "Pushing..";
DT=$(date "+[%m-%d-%Y][%H:%M:%S]");
git add -A;
git commit -m "Commited from Push.sh on ${DT}";
git push;
