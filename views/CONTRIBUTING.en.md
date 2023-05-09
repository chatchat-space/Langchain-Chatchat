# Contribution Guide
Thank you for your valuable time. Your contributions will make this project better! Before submitting a contribution, please take some time to read the getting started guide below.

## Semantic Versioning
This project follows semantic versioning. We release patch versions for important bug fixes, minor versions for new features or non-important changes, and major versions for significant and incompatible changes.

Each major change will be recorded in the `changelog`.

## Submitting Pull Request
1. Fork [this repository](https://github.com/Chanzhaoyu/chatgpt-web) and create a branch from `main`. For new feature implementations, submit a pull request to the `feature` branch. For other changes, submit to the `main` branch.
2. Install the `pnpm` tool using `npm install pnpm -g`.
3. Install the `Eslint` plugin for `VSCode`, or enable `eslint` functionality for other editors such as `WebStorm`.
4. Execute `pnpm bootstrap` in the root directory.
5. Execute `pnpm install` in the `/service/` directory.
6. Make changes to the codebase. If applicable, ensure that appropriate testing has been done.
7. Execute `pnpm lint:fix` in the root directory to perform a code formatting check.
8. Execute `pnpm type-check` in the root directory to perform a type check.
9. Submit a git commit, following the [Commit Guidelines](#commit-guidelines).
10. Submit a `pull request`. If there is a corresponding `issue`, please link it using the [linking-a-pull-request-to-an-issue keyword](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword).

## Commit Guidelines

Commit messages should follow the [conventional-changelog standard](https://www.conventionalcommits.org/en/v1.0.0/):

```bash
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Commit Types

The following is a list of commit types:

- feat: New feature or functionality
- fix: Bug fix
- docs: Documentation update
- style: Code style or component style update
- refactor: Code refactoring, no new features or bug fixes introduced
- perf: Performance optimization
- test: Unit test
- chore: Other commits that do not modify src or test files


## License

[MIT](./license)