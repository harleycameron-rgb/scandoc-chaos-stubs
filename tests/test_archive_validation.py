import copy,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from stub_factory import make_sentinel
from verify_silhouette import verify_one,verify_path
from verify_moire import verify_path as verify_moire
class ArchiveValidation(unittest.TestCase):
 def test_current_inventory(self):
  self.assertTrue(verify_path(ROOT/'silhouette/instances')['all_upheld'])
  self.assertTrue(verify_moire(ROOT/'moire-fields')['all_upheld'])
 def test_resealed_geometry_corruption_rejected(self):
  original=json.loads((ROOT/'silhouette/instances/sil_tentacled_geometry_default.json').read_text())
  mutations=[lambda x:x['geometry']['arms'][0].update(vector=[0,0,1]),lambda x:x['geometry'].update(arm_count=True),lambda x:x['geometry']['arms'].__setitem__(0,None),lambda x:x.update(id='other'),lambda x:x.update(unexpected=1)]
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'record.json'
   for mutate in mutations:
    x=copy.deepcopy(original);mutate(x);x['sentinel']=make_sentinel(x);p.write_text(json.dumps(x))
    with self.subTest(mutate=mutate):self.assertFalse(verify_one(p)['upheld'])
 def test_resealed_wrong_moire_value_rejected(self):
  from verify_moire import verify_one as verify_field
  x=json.loads((ROOT/'moire-fields/moire_phi01_02.json').read_text());x['residue_phi'][0]+=1;x['sentinel']=make_sentinel(x)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'moire_phi01_02.json';p.write_text(json.dumps(x));self.assertFalse(verify_field(p)['upheld'])
