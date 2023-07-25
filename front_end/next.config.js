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
