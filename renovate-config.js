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
  "dryRun": "full", //"full",  // use full to only log messages instead of creating pull requests
  //"repositories": ["fraunhofer-isi/micat"],  // needs to be adapted to your repository
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
     "dependencyDashboardApproval": false,
     "minimumReleaseAge": null
    }
  ]
};