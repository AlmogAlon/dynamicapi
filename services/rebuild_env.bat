:; # BASH ONLY CODE:

if [ -z ${LINK_ONLY} ]; then
  python3.10 -m venv ./venv --upgrade-deps
  source ./venv/bin/activate
  pip install wheel
  pip install --use-deprecated=legacy-resolver -r requirements.txt
fi

set +e

if [ -z ${BUILD_ONLY} ]; then

  for SERVICE in "api" ; do
    pushd $SERVICE
    ln -s -n ../common common
    ln -s -n ../requirements.txt requirements.txt
    popd
  done

fi

exit
:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%
