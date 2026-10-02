# Contributing

Start with the README and reproduce the problem using the current version. Open an issue with your operating system, relevant tool versions, what you expected, and what happened. Remove credentials and personal information from examples and logs.

Make a focused change on a branch. Explain the problem and the resulting behavior in the pull request, then run the checks below. GitHub also runs these checks before a pull request can merge.

```sh
python3 -B .github/scripts/check_repository.py
python3 -B -m unittest discover -s .github/scripts -p 'test_*.py'
```

Keep examples generic. Do not contribute personal configuration, account IDs, subscriber lists, private style recipes, or files from a working video project. Dependencies and GitHub Actions updates go through a pull request and the same checks as other changes.

The editing library also requires Node.js and FFmpeg:

```sh
node validate-library.mjs
cd '09 Visual Storytelling and Motion System/starter'
npm ci --ignore-scripts
npm test
```

Add new public files to `manifest.json`. Rebuild and test the standalone ZIP when its contents change.
