// © 2023 Fraunhofer-Gesellschaft e.V., München
//
// SPDX-License-Identifier: AGPL-3.0-or-later

const nextConfig = {
  // If you change the basePaths, also change path for favicon in _document.js
  basePath: '/mica-tool-wGlobal/python/front_end/out',
  reactStrictMode: true,
  images: {
    unoptimized: true // required for static export to work
  },
  webpack: (config) => {
    config.resolve.fallback = {
      'fs': false
    };
    return config;
  }

};

// eslint-disable-next-line unicorn/prefer-module
module.exports = nextConfig;
