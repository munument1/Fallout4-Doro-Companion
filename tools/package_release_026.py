"""Promote RC2 to v0.2.6 without changing any game payload bytes."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    source=ROOT/'build/DoroFollower_FO4_0.2.6_RC2.zip'
    with zipfile.ZipFile(source) as z:files={p:z.read(p) for p in z.namelist()}
    assert all(sha(files[p])==v for p,v in json.loads(files['SHA256.json']).items())
    original=dict(files);files.pop('SHA256.json')
    files['README_KO.txt']=(ROOT/'docs/RELEASE_026_FINAL_KO.md').read_bytes()
    report=json.loads(files['release_validation.json'])
    report.update(version='0.2.6',promoted_from='0.2.6 RC2',user_authorized_release=True,
                  game_payload_identical_to_rc2=True,source_archive_sha256=sha(source.read_bytes()))
    files['release_validation.json']=json.dumps(report,ensure_ascii=False,indent=2).encode('utf-8')
    assert all(value==original[name] for name,value in files.items() if name not in ['README_KO.txt','release_validation.json'])
    files['SHA256.json']=json.dumps({p:sha(v) for p,v in files.items()},indent=2).encode()
    dest=ROOT/'build/DoroFollower_FO4_0.2.6.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for p,v in files.items():z.writestr(p,v)
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        assert all(sha(z.read(p))==h for p,h in json.loads(z.read('SHA256.json')).items())
    dest.with_name(dest.name+'.sha256').write_text(sha(dest.read_bytes())+'  '+dest.name+'\n',encoding='ascii')
    print(dest)
if __name__=='__main__':main()
