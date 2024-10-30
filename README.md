# cs411-hw3
# Git Collaboration:
---
### When you are working
* Work on the YOUR_NAME branch
* Merge these changes into your local copy of submission `git checkout submission` followed by `git merge YOUR_NAME`
* When you are done, from the submission branch, run `git push origin submission`
* Change back to your branch to continue working `git checkout YOUR_NAME`
---
### When there are changes you want on your machine
* Pull down the changes on the submission branch `git pull origin submission`
* These changes are now in the origin/submission branch on your computer, to merge these into your local dev branch run `git checkout YOUR_NAME`to change to your branch and then `git merge origin/submission`to get these remote changes you pulled down into your copy of submission
---
### If there is a serious git error and you can no longer work on your local repo
* Make node of all of your changes (you can save them in a temporary file outside of the repo)
* Delete your local repo (if you remember your changes since you last touched origin submission you should be fine) by navigating to the parent directory of the repo `cd ..` and then deleting the repo by `rm -rf cs411-hw3`
* You can clone the remote repo again `git clone REPO_URL`
* Redo your changes and keep working