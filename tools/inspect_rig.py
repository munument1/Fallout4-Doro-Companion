import bpy,json
r=bpy.data.objects.get('skeleton.nif:ARMATURE')
print(json.dumps({'matrix':[list(row) for row in r.matrix_world],'bones':[{'name':b.name,'head':list(r.matrix_world@b.head_local),'tail':list(r.matrix_world@b.tail_local)} for b in r.data.bones if any(s in b.name.lower() for s in ['head','neck','jaw','spine','pelvis','thigh','knee','ankle','com'])]}))
