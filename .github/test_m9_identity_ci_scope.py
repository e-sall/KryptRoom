"""PR2 routing is additive; shared policy and unknown recipes stay conservative."""

import unittest

from ci_scope import classify_paths


class IdentityScopeTests(unittest.TestCase):
    def flags(self, *paths):
        return classify_paths(list(paths), lambda _: None, lambda _: None)

    def test_bff_and_shared_frontend_dependencies_require_both_consumers(self):
        for path in ["apps/web/src/server/auth/handlers.ts", "apps/web/src/app/auth/callback/route.ts",
                     "apps/web/src/app/bff/api/v1/[...path]/route.ts", "apps/web/package-lock.json",
                     "apps/web/package.json", "apps/web/next.config.ts", "apps/web/Dockerfile.identity",
                     "apps/web/playwright.identity.config.ts", "apps/web/tests-identity/new.spec.ts"]:
            self.assertEqual(self.flags(path), {"core":False,"web":True,"m9":True}, path)

    def test_m8_visual_only_stays_isolated(self):
        self.assertEqual(self.flags("apps/web/src/features/marketing/signal-v4.css"),
                         {"core":False,"web":True,"m9":False})

    def test_identity_compose_is_owned_m9_configuration(self):
        self.assertEqual(self.flags("services/control-api/compose.identity.yml"),
                         {"core":False,"web":False,"m9":True})

    def test_core_unknown_shared_and_ci_remain_conservative(self):
        for path in ["engines/zk/changed.rs", "nodes/crypto.py", "packages/manifests/room-state.schema.json",
                     "tests/state_proof/fixtures/S1_joined.json", "SECURITY.md", ".github/ci_scope.py",
                     ".github/workflows/control-api-identity.yml", "services/control-api/unknown-config"]:
            self.assertTrue(self.flags(path)["core"], path)
            self.assertTrue(self.flags(path,"apps/web/src/server/auth/handlers.ts")["core"], path)

    def test_unknown_or_shared_workflow_cannot_be_exempted_by_bff_changes(self):
        flags = self.flags("apps/web/src/server/auth/handlers.ts", ".github/workflows/private-nn.yml")
        self.assertEqual(flags,{"core":True,"web":True,"m9":True})


if __name__ == "__main__":
    unittest.main()
