# Usage
Usage in `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/c0m1c5an5/gitlab-ci-pre-commit
  rev: ''  # Use the sha / tag you want to point at
  hooks:
    - id: gitlab-ci-lint
    - id: gitlab-ci-fmt
    - id: gitlab-ci-shellcheck
```

# Issues and proposals

Feel free to create an issue, report a bug or suggest improvements in the "Issues" section.


# Hooks

## gitlab-ci-lint
Use gitlab api to lint gitlab-ci files.

Requirements (installed manually):
- [pass](https://www.passwordstore.org)

Requirements (installed automatically):
- [python-gitlab](https://python-gitlab.readthedocs.io/en/stable)
- [GitPython](https://github.com/gitpython-developers/GitPython)
- [giturlparse](https://github.com/nephila/giturlparse)

## gitlab-ci-fmt
Ensure strict ordering of keywords in gitlab-ci configuration file.

Requirements (installed manually):
- [yq](https://github.com/mikefarah/yq)

## gitlab-ci-shellcheck
Use shellcheck to check job script sections.

Requirements (installed manually):
- [shellcheck](https://github.com/koalaman/shellcheck)
