import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir:'./tests/browser',testMatch:['how-review.spec.ts','marketing-v71.spec.ts'],
  outputDir:'../../../work/how-review-results',workers:1,reporter:'list',
  use:{baseURL:'http://127.0.0.1:3002',viewport:{width:1366,height:768}},
  projects:[{name:'chromium',use:{browserName:'chromium'}},{name:'webkit',use:{browserName:'webkit'}}],
});
