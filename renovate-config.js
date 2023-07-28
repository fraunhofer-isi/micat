module.exports = {
  username: 'renovate-release',
  gitAuthor: 'Renovate Bot <bot@renovateapp.com>',
  onboarding: false,
  enabled: true,
  platform: 'github',
  includeForks: true,
  dryRun: 'full',
  repositories: ['fraunhofer-isi/micat'],
  packageRules: [
    {
      description: 'lockFileMaintenance',
      matchUpdateTypes: [
        'pin',
        'digest',
        'patch',
        'minor',
        'major',
        'lockFileMaintenance',
      ],
      dependencyDashboardApproval: false,
      stabilityDays: 0,
    },
  ],
};