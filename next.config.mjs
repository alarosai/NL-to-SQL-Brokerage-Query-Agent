/** @type {import('next').NextConfig} */
const nextConfig = {
    serverExternalPackages: ["better-sqlite3"],
    outputFileTracingIncludes: {
        '/api/query': ['./data/**/*'],
    },
};

export default nextConfig;
