gitlab-ci-tools
================
Gitlab CI pipeline lint, shellcheck and format tools. Standardize your code format and prevent mistakes before you commit.

### Using gitlab-ci-tools with pre-commit
Add this to your `.pre-commit-config.yaml`

```yaml
- repo: https://github.com/c0m1c5an5/gitlab-ci-pre-commit
  rev: ''  # Use the sha / tag you want to point at
  hooks:
    - id: gitlab-ci-lint
    - id: gitlab-ci-fmt
    - id: gitlab-ci-shellcheck
```

### Hooks available

#### `gitlab-ci-lint`
Use gitlab api to lint gitlab-ci files.
- Requires [pass](https://www.passwordstore.org) to be installed on your system as a secret backend so that your api key is stored encrypted.

#### `gitlab-ci-fmt`
Ensure strict ordering of keywords in gitlab-ci configuration file.
- Requires [yq](https://github.com/mikefarah/yq) to be installed on your system.

#### `gitlab-ci-shellcheck`
Use shellcheck to check all job script sections.
- Requires [shellcheck](https://github.com/koalaman/shellcheck) to be installed on your system.
- All script sections must contain shell markers (eg. '#shellcheck shell=bash')

# Issues and proposals
Feel free to create an issue, report a bug or suggest improvements in the "Issues" section.
