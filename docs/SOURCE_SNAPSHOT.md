# PySlate 0.3.0 public source snapshot

This repository imports the available `PySlate-0.3.0-source.zip` delivery archive
and preserves the existing public repository's README, MIT license, contribution
guidelines, security policy, changelog, and ignore rules.

- Original source archive SHA256:
  `3e67ad4264987730523cfa74f66c7a89a2a2e3a2d332796e89cc6476331780c3`.
- The archive's `PySlate/source/` contents live at the repository root.
- Delivery documentation and third-party notices are merged into `docs/` and
  `licenses/`. Build scripts and test defaults follow this repository layout.
- Local absolute paths in image-generation provenance are replaced with portable
  identifiers. Prompts, selected and rejected image identities, and hashes remain.
- The checked-in web bundle can be rebuilt from `package-lock.json`. The import
  rebuild matched the original `web/vendor.js` byte for byte.
- `licenses/WEB-NOTICES.md` records the supplemental Babel regenerator helper notice.

The archive's outer `SOURCE-MANIFEST.json` describes its original delivery layout;
it is not a manifest of this adapted public tree. Git records the public tree and
subsequent changes. Historic release reports document their original validation
runs and are not a new certification of this checkout.

Binary release packages, detailed historical test-report archives, and original
PNG artwork masters remain outside this source snapshot. Runtime WebP illustrations
and the other offline assets needed by the application are included. Android and
Windows installers require their documented build dependencies; this source import
does not establish real-device compatibility, clean-machine installation coverage,
code signing, or a comprehensive security audit.
