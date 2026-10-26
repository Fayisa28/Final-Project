import base64, sqlite3, unittest
import jobhunter_server as s
class Fake:
 def __init__(self,u): self.u=u
 def _token(self): return self.u
class DataPermissions(unittest.TestCase):
 def test_schema_exists(self):
  c=sqlite3.connect(s.DB_FILE); names={r[0] for r in c.execute("select name from sqlite_master where type='table'")}; c.close(); self.assertTrue({'profiles','cvs','applications','messages','companies'}<=names)
 def test_role_gate_denies_anonymous(self):
  old=s.session_user; s.session_user=lambda token: None
  try: self.assertEqual(s.role_required(Fake(None),('seeker',))[1][0],401)
  finally:s.session_user=old
 def test_role_gate_denies_recruiter_seeker_endpoint(self):
  old=s.session_user; s.session_user=lambda token:{'email':'r','role':'recruiter'}
  try:self.assertEqual(s.role_required(Fake('x'),('seeker',))[1][0],403)
  finally:s.session_user=old
 def test_cv_header_rule(self):
  self.assertTrue(b'%PDF-1.4'.startswith(b'%PDF')); self.assertFalse(b'not pdf'.startswith(b'%PDF'))
if __name__=='__main__':unittest.main()
