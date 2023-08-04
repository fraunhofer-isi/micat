// © 2023 Fraunhofer-Gesellschaft e.V., München
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// This is the configuration ofr renovate but, referenced from
// github workflow .github/workflows/renovate.yml
// Also see
// https://github.com/renovatebot/github-action
// https://docs.renovatebot.com/self-hosted-configuration/

module.exports = {
  "username": "renovate-release",
  "gitAuthor": "Renovate Bot <bot@renovateapp.com>",
  "onboarding": false,
  "requireConfig": "optional",
  "platform": "github",
  "forkProcessing": "enabled",
  "dryRun": null, //"full",  // use full to only log messages instead of creating pull requests
  "autodiscover": true,
  "packageRules": [
    {
     "description": "lockFileMaintenance",
     "matchUpdateTypes": [
       "pin",
       "digest",
       "patch",
       "minor",
       "major",
       "lockFileMaintenance"
     ],
     "automerge": true,
     "automergeType": "branch",
     "ignoreTests": true, // set to false if you want updates only to be installed if tests pass
     "dependencyDashboardApproval": false,
     "minimumReleaseAge": null
    },

    {
      // sphinx-rtd-theme does not support Sphinx 7.0.1 yet  https://github.com/readthedocs/sphinx_rtd_theme/issues/1463
      "matchPackageNames": ["Sphinx"],
      "allowedVersions": "<7.0"
    },
    {
      // licensecheck > 2023.1.4 has bugs regarding ignoreLicense option:
      // https://github.com/FHPythonUtils/LicenseCheck/issues/48
      "matchPackageNames": ["licensecheck"],
      "allowedVersions": "<=2023.1.4"
    }



  ]
};