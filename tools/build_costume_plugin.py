import struct,json
from pathlib import Path
from fo4_records import GAME,records,subs

root=Path(__file__).resolve().parent.parent
plugin=root/'build/DoroFollower/DoroFollower.esp'
U=lambda n:struct.pack('<I',n)

# Costumes are no longer emitted as DoroCostumes.esp.
# build_doro_plugin.py owns these records in the single ESL-flagged DoroFollower.esp.
if not plugin.exists():
    raise FileNotFoundError('Build DoroFollower.esp first with tools/build_doro_plugin.py')

own=lambda n:0x01000000+n
helmet,hAA,dog,dAA,category,hRecipe,dRecipe=map(own,range(0x840,0x847))
rows=list(records(plugin))
by_id={f:(t,fl,b) for t,f,fl,b in rows}

for fid,typ in [
    (helmet,'ARMO'),(hAA,'ARMA'),(dog,'ARMO'),(dAA,'ARMA'),
    (category,'KYWD'),(hRecipe,'COBJ'),(dRecipe,'COBJ'),
]:
    assert fid in by_id,(hex(fid),typ)
    assert by_id[fid][0]==typ,(hex(fid),by_id[fid][0],typ)

recipe_utility=None
for t,f,flags,b in records(GAME/'Data/Fallout4.esm'):
    if f==0x6980c:
        recipe_utility=dict(subs(b))
        break
assert recipe_utility is not None
recipe_filter_tnam=recipe_utility.get('TNAM')
assert recipe_filter_tnam is not None
assert dict(subs(by_id[category][2])).get('TNAM')==recipe_filter_tnam

for fid in [hRecipe,dRecipe]:
    ss=dict(subs(by_id[fid][2]))
    assert ss['BNAM']==U(0x102158)
    assert ss['FNAM']==U(category)
    assert not any(s in ss for s in ['FVPA','CTDA','COCT','CNTO'])

result={
    'plugin':'DoroFollower.esp',
    'plugin_type':'ESL-flagged ESP (ESP-FE)',
    'standalone_costume_plugin':False,
    'costume_records':7,
    'recipes':2,
    'ingredient_and_perk_requirements':0,
    'recipe_filter_donor':'RecipeUtility [KYWD:0006980C]',
    'chemistry_workbench':'WorkbenchChemlab [KYWD:00102158]',
    'ingame_tested':False,
}
(root/'build/costume_plugin_validation.json').write_text(json.dumps(result,indent=2))
print('COSTUMES_IN_UNIFIED_PLUGIN_OK',len(rows))
