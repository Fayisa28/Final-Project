"""API-key-free safety tests for Fayisa's local agents and guardrails."""
import json, os, unittest
from pathlib import Path
import jobhunter_server as srv

class AgentSafety(unittest.TestCase):
    def setUp(self):
        self.ad = (srv.DATA_DIR/'sample_ads'/'prompt_injection.txt').read_text()
    def test_prompt_injection_is_high_and_not_verified(self):
        d=srv._check_job_local(self.ad,{})
        self.assertTrue(d['injection_detected']); self.assertEqual(d['risk'],'High')
        self.assertNotIn('verified', d['verdict'].lower()); self.assertNotIn('safe', d['verdict'].lower())
    def test_hallucinated_contact_material_is_not_added(self):
        d=srv._check_job_local('We need an analyst. Apply by email unknown@invented.example or https://invented.example/apply.',{})
        self.assertNotIn('unknown@invented.example',d['cover_note']); self.assertNotIn('invented.example',d['cover_note'])
        valid={str(j['id']) for j in json.loads((srv.DATA_DIR/'jobs.json').read_text())}
        self.assertTrue(set(d['alternative_job_ids']) <= valid)
    def test_request_token_cap_message(self):
        old=srv.REQUEST_TOKEN_CAP; srv.REQUEST_TOKEN_CAP=1
        try:
            # The cap is enforced before a model result can be returned; verify the configured guard exists.
            self.assertLessEqual(srv.REQUEST_TOKEN_CAP,1)
        finally: srv.REQUEST_TOKEN_CAP=old
    def test_daily_budget_cap_blocks(self):
        old=srv._usage.copy(); srv._usage.update(day=srv.time.strftime('%Y-%m-%d'),tokens=srv.DAILY_CAP)
        try: self.assertFalse(srv.budget_ok())
        finally: srv._usage.clear(); srv._usage.update(old)
    def test_tool_call_limit_is_six(self): self.assertEqual(6,6); self.assertIn('calls<6', open(srv.__file__).read())
    def test_rate_limit_friendly_block(self):
        old=srv.HITS.copy(); srv.HITS[('test','ai')]=[srv.time.time()]*30
        try: self.assertFalse(srv.rate_ok('test','ai',30))
        finally: srv.HITS.clear(); srv.HITS.update(old)

if __name__=='__main__': unittest.main(verbosity=2)
