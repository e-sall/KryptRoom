import { defineConfig } from '@playwright/test';
export default defineConfig({
 testDir:'./tests/browser',testMatch:['signal-integration.spec.ts','cinematic.review.ts','how-review.spec.ts'],
 outputDir:'../../../work/signal-test-results',workers:1,reporter:'list',timeout:60000,
 use:{baseURL:'http://127.0.0.1:3002',viewport:{width:1366,height:768}},
 projects:[{name:'chromium',use:{browserName:'chromium'}},{name:'webkit',use:{browserName:'webkit'}}],
});
