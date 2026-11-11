import {defineConfig} from "@playwright/test";
import identity from "./playwright.identity.config";

// Dedicated opt-in real-service suite; preserve PR2 identity acceptance selection.
export default defineConfig({...identity,testDir:"./tests-rooms-real"});
