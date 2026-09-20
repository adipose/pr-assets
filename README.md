# pr-assets

Screenshots and interactive comparisons linked from pull requests, one folder per PR, served by
GitHub Pages at https://adipose.github.io/pr-assets/

GitHub renders an image in a PR body but will not give you a slider, and its own image diff viewer
only appears for an image changed in a commit, which does not work for a before and after that were
never two versions of one file.  So the comparison lives here as a page and the PR links to it.

| folder | pull request |
|---|---|
| [mpcvr-2](https://adipose.github.io/pr-assets/mpcvr-2/) | [clsid2/MPCVideoRenderer#2](https://github.com/clsid2/MPCVideoRenderer/pull/2), HDR to SDR tone mapping |

Keep a folder for as long as the PR it belongs to is open.

The slider is [img-comparison-slider](https://github.com/sneas/img-comparison-slider) by Dmytro
Snisarenko, MIT, vendored rather than loaded from a CDN so the page keeps working if the CDN does
not.  Its license is beside it in each folder that uses it.
