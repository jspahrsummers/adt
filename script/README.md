# python-build-scripts

This project is a collection of scripts which I've found useful for new Python projects, with two goals in mind:

 1. To standardize project bootstrap after cloning
 1. To easily set up continuous integration

**The scripts' behaviors reflect how I like to set up my projects, and may not be to your tastes.** These aren't really intended for a broad audience, though please feel free to use them if you find them helpful!

## Getting Started

To add the scripts to your project, read the contents of this repository into a `script` folder:

```
$ git remote add python-build-scripts https://github.com/jspahrsummers/python-build-scripts.git
$ git fetch python-build-scripts
$ git read-tree --prefix=script/ -u python-build-scripts/master
```

Then commit the changes, to incorporate the scripts into your own repository's history. You can also freely tweak the scripts for your specific project's needs.

To merge in upstream changes later:

```
$ git fetch -p python-build-scripts
$ git merge --allow-unrelated-histories --ff --squash -Xsubtree=script python-build-scripts/master
```
