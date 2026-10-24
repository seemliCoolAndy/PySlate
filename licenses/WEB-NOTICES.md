# Bundled web dependency notices

`npm-dependencies.json` records installed dependency versions and their license texts.
The built `web/vendor.js` also preserves upstream legal comments.

DOMPurify's distributed JavaScript includes Babel's MIT-licensed regenerator helper.
Its embedded notice names Facebook and links to the Babel helper license. The full
text is retained in [babel-helpers/LICENSE](babel-helpers/LICENSE), in addition to
DOMPurify's Apache 2.0 / MPL 2.0 texts.

Source of the helper notice (checked 2026-10-24):
[Babel helpers license](https://github.com/babel/babel/blob/main/packages/babel-helpers/LICENSE).
This supplemental file is retained when `tools/collect_licenses.py` refreshes the
installed npm package notices.
