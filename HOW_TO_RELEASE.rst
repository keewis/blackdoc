Release process
===============
1. the release happens from `master` so make sure it is up-to-date:

   .. code:: sh

      git pull origin master

2. look at `changelog.rst` and make sure it is complete and with
   references to issues and pull requests

3. run the test suite, try to call the program and make sure the
   pre-commit hook works

4. check that the documentation is building

5. Commit the release:

   .. code:: sh

      git commit -am "Release v0.X.Y"

6. Tag the release:

   .. code:: sh

      git tag -a v0.X.Y -m "v0.X.Y"

7. Build source and binary wheels:

   .. code:: sh

      git clean -xdf
      python -m pep517.build --source --binary .

8. Use `twine` to check the package build:

   .. code:: sh

      twine check dist/*

9. try installing the wheel in a new environment and run the tests /
   binary again:

   .. code:: bash

      python -m venv test
      source test/bin/activate
      python -m pip install -r requirements.txt
      python -m pip install pytest
      python -m pip install dist/*.whl
      python -m pytest
      python -m blackdoc --check .; echo $?
      python -m blackdoc .; echo $?
      git reset --hard HEAD

10. Push to master and upload to PyPI:

   .. code:: sh

      git push origin master
      git push origin --tags
      twine upload dist/*

   Be careful, this can't be undone.
              
11. Update stable:

    .. code:: sh

       git checkout stable
       git merge v0.X.Y
       git push origin stable

12. Make sure readthedocs builds both `stable` and the new tag

13. Add a new section to the changelog and push directly to master