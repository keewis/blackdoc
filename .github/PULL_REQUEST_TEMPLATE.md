- [ ] Closes #xxxx
- [ ] Tests added
- [ ] Passes `pre-commit run --all-files`
- [ ] User visible changes (including notable bug fixes) are documented in `changelog.rst`
- [ ] New features are documented in the docs

<!--
By default, the upstream-dev CI is only run when triggered by the github website (`workflow_dispatch`)
or if it was run on schedule. To run it on a commit of a pull request (`pull_request`), include
the `[test-upstream]` tag in the summary line of the commit message.

For changes that are not covered by the CI please use the `[skip-ci]` tag to avoid running the
normal CI.
-->
