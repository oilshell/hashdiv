#!/bin/bash
#
# Usage:
#   ./run.sh <function name>

set -o nounset
set -o pipefail
set -o errexit

# Use ~/git/dreamhost/flask/dreamhost.sh to build Python

readonly PY=Python-3.9.1

py3() {
  $HOME/opt/$PY/bin/python3.9 "$@"
}

create-venv() {
  py3 -m venv _venv
}

py-deps() {
  . _venv/bin/activate

  # Versions as of 1/2/2021
  # pip3 install 'flask==1.1.2' #'flup==1.0.3'
  #
  # 2024:
  # no flup?
  # Jinja version broke
  # I never used a lock file!  Gah
  # DId Pip have it?

  python3 -m pip install flask
  #python3 -m pip install 'flask == 1.1.2'
}

hashdiv-dirs() {
  mkdir --verbose -p upload/{tmp,paste}
}

deploy-hashdiv() {
  local dir=~/dr.shxa.org/hashdiv
  mkdir -p $dir
  cp -v .htaccess dispatch.fcgi $dir
  
  cd $dir
  hashdiv-dirs
}

deploy-soil() {
  local dir=~/builds.oilshell.org/soil-receive
  mkdir -p $dir
  cp -v soil_htaccess soil_dispatch.fcgi $dir
  cd $dir
}

"$@"
