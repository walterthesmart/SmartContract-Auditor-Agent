# Deployment Guide

## Vercel Deployment Fix

The deployment error you encountered was due to Husky (Git hooks tool) trying to install in Vercel's build environment where `.git` directory is not available.

### What was fixed:

1. **Husky Installation Issue**: Modified `frontend/package.json` to skip Husky installation in CI environments:
   ```json
   "prepare": "node -e \"if (process.env.CI !== 'true') { try { require('husky').install() } catch (e) {} }\""
   ```

2. **Vercel Configuration**: Added `vercel.json` to properly handle the frontend subdirectory structure.

### Environment Variables

For production deployment, you'll need to set these environment variables in Vercel:

- `NEXT_PUBLIC_API_URL`: URL of your backend API server
- `NEXT_PUBLIC_HEDERA_NETWORK`: Either "testnet" or "mainnet"

### Deployment Steps

1. **Push your changes** to GitHub
2. **In Vercel Dashboard**:
   - Go to your project settings
   - Add environment variables:
     - `NEXT_PUBLIC_API_URL` = `https://your-backend-url.com`
     - `NEXT_PUBLIC_HEDERA_NETWORK` = `testnet`
3. **Redeploy** the project

### Backend Deployment

The frontend expects a backend API. You'll need to deploy the Python backend separately:

1. **Deploy backend** to a service like Railway, Render, or Heroku
2. **Update** `NEXT_PUBLIC_API_URL` in Vercel to point to your backend URL
3. **Ensure** your backend has CORS configured to allow requests from your Vercel domain

### Local Development

For local development:
1. Copy `frontend/.env.example` to `frontend/.env.local`
2. Update the values as needed
3. Run `npm run dev` in the frontend directory

### Troubleshooting

If you still encounter issues:
- Check Vercel build logs for specific errors
- Ensure all dependencies are properly listed in `package.json`
- Verify environment variables are set correctly in Vercel dashboard
