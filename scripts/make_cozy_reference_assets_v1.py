import bpy, math, os
from math import radians, sin, cos, pi
from mathutils import Vector

ROOT='/root/3d/assets/cozy_reference_assets_v1'
os.makedirs(ROOT, exist_ok=True)

M={}
def clear():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete()
    for material in list(bpy.data.materials):
        bpy.data.materials.remove(material)
    M.clear()

def mat(n,c):
    m=bpy.data.materials.new(n); m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value=c; bsdf.inputs['Roughness'].default_value=.9
    M[n]=m; return m

def mats():
    for n,c in {
        'wood':(.55,.31,.15,1),'wood_dark':(.32,.18,.09,1),'cream':(.86,.73,.55,1),'cream2':(.96,.84,.64,1),
        'green':(.34,.62,.18,1),'green2':(.48,.75,.23,1),'grass':(.28,.62,.16,1),'red':(.86,.18,.14,1),
        'pink':(.95,.45,.63,1),'purple':(.43,.24,.68,1),'blue':(.34,.70,.95,1),'gold':(.96,.70,.22,1),
        'brown':(.44,.25,.13,1),'stone':(.58,.55,.48,1),'stone2':(.78,.74,.63,1),'black':(.05,.05,.06,1),
        'white':(.96,.96,.90,1),'orange':(.98,.48,.13,1),'skin':(.96,.75,.52,1),'chroma':(.333,.8,.266,1)
    }.items(): mat(n,c)

def assign(o,m): o.data.materials.append(M[m]); return o

def flat(o):
    if hasattr(o.data,'polygons'):
        for p in o.data.polygons: p.use_smooth=False
    return o

def cube(n,loc,scale,m,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=n; o.dimensions=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); assign(o,m)
    if bevel:
        mod=o.modifiers.new('toy bevel','BEVEL'); mod.width=bevel; mod.segments=1
    return flat(o)

def cyl(n,loc,r,d,m,verts=8,rot=(0,0,0),scale=(1,1,1),bevel=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=loc, rotation=rot); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); assign(o,m)
    if bevel:
        mod=o.modifiers.new('toy bevel','BEVEL'); mod.width=bevel; mod.segments=1
    return flat(o)

def cone(n,loc,r1,r2,d,m,verts=8,rot=(0,0,0),scale=(1,1,1)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); assign(o,m); return flat(o)

def sphere(n,loc,r,m,seg=8,rings=4,scale=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=loc); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); assign(o,m); return flat(o)

def poly(n,pts,m,th=.025):
    # pts in local xz, thickness y
    verts=[(x,-th/2,z) for x,z in pts]+[(x,th/2,z) for x,z in pts]
    N=len(pts); faces=[tuple(range(N)),tuple(range(N,2*N))]
    for i in range(N): faces.append((i,(i+1)%N,(i+1)%N+N,i+N))
    mesh=bpy.data.meshes.new(n+'Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(n,mesh); bpy.context.collection.objects.link(o); assign(o,m); return flat(o)

def star(n,loc,s,m):
    pts=[]
    for i in range(10):
        r=s if i%2==0 else s*.45; a=pi/2+i*pi/5; pts.append((r*cos(a),r*sin(a)))
    o=poly(n,pts,m,.035); o.location=loc; return o

def leaf_obj(n,loc,scale,m):
    pts=[(0,.55),(.28,.25),(.38,0),(.22,-.35),(0,-.58),(-.22,-.35),(-.38,0),(-.28,.25)]
    o=poly(n,pts,m,.035); o.location=loc; o.scale=scale; return o

def crystal(n,loc,m='pink',scale=(1,1,1)):
    cone(n+' top', (loc[0],loc[1],loc[2]+.16), .18, 0, .32, m, verts=6, scale=scale)
    cone(n+' bottom', (loc[0],loc[1],loc[2]-.12), .14, .04, .25, m, verts=6, scale=scale)

def grass_base():
    cyl('round grass base',(0,0,-.04),.92,.08,'grass',12,scale=(1,.72,1))
    for x,y in [(-.55,-.35),(.55,-.25),(.42,.32),(-.2,.42)]:
        cone('grass blade',(x,y,.08),.04,.0,.35,'green2',5,rot=(radians(12),0,0),scale=(.55,.55,1))
    for x,y in [(-.65,.2),(.62,.18)]: sphere('small rock',(x,y,.05),.13,'stone',8,4,scale=(1.25,.85,.65))

def camera(target=(0,0,.8),h=2.1,dist=4.6):
    bpy.ops.object.light_add(type='AREA', location=(0,-3.7,4.2)); l=bpy.context.object; l.data.energy=450; l.data.size=5
    bpy.ops.object.camera_add(location=(3.0,-4.6,h)); cam=bpy.context.object
    direction=Vector(target)-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.lens=58; bpy.context.scene.camera=cam
    cube('chroma floor',(0,0,-.09),(5,5,.04),'chroma'); cube('chroma wall',(0,2.0,1.7),(5,.04,3.6),'chroma')

def render(name,target=(0,0,.7),h=2.1):
    camera(target,h); bpy.context.scene.render.engine='BLENDER_EEVEE'; bpy.context.scene.eevee.taa_render_samples=24
    bpy.context.scene.render.resolution_x=900; bpy.context.scene.render.resolution_y=900; bpy.context.scene.view_settings.view_transform='Standard'; bpy.context.scene.world.color=(.333,.8,.266)
    out=os.path.join(ROOT,name); os.makedirs(out,exist_ok=True); bpy.context.scene.render.filepath=os.path.join(out,'perspective.png')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,'source.blend')); bpy.ops.render.render(write_still=True)
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in bpy.context.scene.objects:
        if o.type=='MESH' and not o.name.startswith('chroma'): o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out,'model.glb'), use_selection=True, export_format='GLB')

def rod(name,theme):
    clear(); mats()
    cyl('long wooden fishing rod',(0,0,.72),.055,2.5,'wood',8,rot=(0,radians(82),0),scale=(1,1,1))
    cyl('thick handle',(-1.0,0,.62),.14,.58,'wood',8,rot=(0,radians(82),0),scale=(1.2,.8,1),bevel=.02)
    for x in [-.55,.15,.7]: cyl('gold wrap',(x,0,.68+.05*x),.075,.10,'gold',8,rot=(0,radians(82),0))
    # reel
    cyl('round reel',(-.25,-.10,.45),.24,.12,'cream',10,rot=(radians(90),0,0),bevel=.02); cyl('reel center',(-.25,-.18,.45),.08,.08,'wood_dark',8,rot=(radians(90),0,0)); cyl('small crank',(-.05,-.22,.33),.035,.25,'wood_dark',8,rot=(0,radians(55),0))
    # line and hooks as simple cylinders/cubes
    cyl('line hanging',(1.10,-.02,.43),.012,.65,'white',6,rot=(0,0,0)); cyl('small ring',(0.62,-.03,.57),.045,.025,'wood_dark',8,rot=(radians(90),0,0)); cyl('small ring 2',(0.05,-.03,.62),.045,.025,'wood_dark',8,rot=(radians(90),0,0))
    if theme=='mushroom':
        cone('red mushroom cap handle',(-1.31,0,.56),.30,.13,.28,'red',10,rot=(0,radians(82),0),scale=(1,1,.8));
        for dx,dz in [(-1.42,.63),(-1.28,.70),(-1.18,.55)]: sphere('white mushroom spot',(dx,-.12,dz),.055,'white',6,3)
        cone('tiny red mushroom lure',(1.1,-.02,.08),.12,.045,.14,'red',8); cyl('tiny stem',(1.1,-.02,-.02),.035,.09,'cream',6)
    elif theme=='leaf':
        leaf_obj('big leaf handle',(-1.32,0,.56),(.65,.65,.65),'green2'); leaf_obj('leaf lure',(1.1,-.02,.05),(.22,.22,.22),'green2')
        for x,z in [(-.72,.78),(-.05,.76),(.38,.72)]: leaf_obj('small vine leaf',(x,-.03,z),(.16,.16,.16),'green2')
        cyl('curvy vine wrap',(-.15,-.03,.71),.025,1.35,'green',6,rot=(0,radians(80),0))
    elif theme=='crystal':
        crystal('pink crystal handle',(-1.32,0,.55),'pink',(.9,.9,1.2)); crystal('pink crystal lure',(1.1,-.02,.08),'pink',(.45,.45,.8))
        for x,c in [(-.52,'blue'),(-.16,'purple')]: crystal('small crystal accent'+x.__str__(),(x,-.03,.78),c,(.45,.45,.55))
        cyl('blue wrap',(-.78,0,.62),.085,.12,'blue',8,rot=(0,radians(82),0)); cyl('purple wrap',(-.45,0,.65),.085,.12,'purple',8,rot=(0,radians(82),0))
    else:
        sphere('stone handle cap',(-1.32,0,.55),.25,'stone',8,4,scale=(1.2,.9,1)); sphere('stone lure',(1.1,-.02,.06),.12,'stone',8,4,scale=(1,.8,1))
        for x in [-.85,-.72,-.60]: cyl('brown rope wrap',(x,0,.62),.09,.06,'brown',8,rot=(0,radians(82),0))
    render('rod_'+theme,target=(0,0,.55),h=1.7)

def mailbox(name,theme):
    clear(); mats(); grass_base()
    cyl('wooden post',(0,0,.45),.16,.9,'wood',8,bevel=.02)
    cube('cross supports',(0,-.02,.72),(.75,.12,.12),'wood_dark',.02)
    if theme=='villager':
        cube('barrel mailbox body',(0,0,1.22),(.95,.62,.62),'wood',.04); cyl('round barrel roof',(0,0,1.55),.34,.98,'wood',10,rot=(0,radians(90),0),scale=(1,.55,1)); cube('front dark slot',(0,-.34,1.34),(.42,.04,.08),'black',.005)
        cyl('hanging lantern',(.58,-.15,.72),.11,.18,'gold',6); cube('lantern glass',(.58,-.15,.58),(.16,.10,.18),'cream2',.01)
    elif theme=='mushroom':
        cube('cream box',(0,0,1.25),(.82,.58,.62),'cream',.04); cone('large red mushroom roof',(0,0,1.72),.68,.28,.38,'red',12,scale=(1,.78,1))
        for x,z in [(-.32,1.78),(.05,1.88),(.36,1.70)]: sphere('white roof dot',(x,-.25,z),.075,'white',6,3)
        cube('letter flap',(0,-.33,1.18),(.28,.04,.18),'cream2',.01); cube('slot',(0,-.34,1.41),(.38,.04,.07),'black',.004)
    elif theme=='leaf':
        cube('wood leaf mailbox',(0,0,1.25),(.82,.58,.60),'wood',.035); leaf_obj('front big leaf roof',(-.18,-.03,1.64),(.72,.72,.72),'green2'); leaf_obj('back big leaf roof',(.20,-.02,1.66),(.72,.72,.72),'green')
        cube('slot',(0,-.34,1.42),(.38,.04,.07),'black',.004); leaf_obj('vine front decoration',(.46,-.35,1.10),(.18,.18,.18),'green2'); sphere('white flower',(.50,-.37,1.27),.055,'white',6,3)
    elif theme=='crystal':
        cube('cream crystal mailbox',(0,0,1.22),(.82,.58,.62),'cream',.035); cyl('purple arch trim',(0,-.31,1.33),.36,.08,'purple',10,rot=(radians(90),0,0),scale=(1,.65,1)); crystal('top pink crystal',(0,-.03,1.82),'pink',(.7,.7,.9))
        for x,c in [(-.62,'purple'),(.62,'blue'),(.46,'pink')]: crystal('base crystal'+x.__str__(),(x,-.20,.25),c,(.75,.75,1.1))
        cube('letter flap',(0,-.34,1.15),(.28,.04,.18),'cream2',.01); cube('slot',(0,-.35,1.42),(.38,.04,.07),'black',.004)
    elif theme=='stone':
        cube('stone block mailbox',(0,0,1.25),(.88,.62,.72),'stone2',.035)
        for x in [-.30,0,.30]: cube('stone top block',(x,0,1.67),(.28,.64,.20),'stone2',.02)
        for x,z in [(-.42,1.38),(.42,1.10),(.06,1.48)]: cube('moss patch',(x,-.33,z),(.16,.05,.13),'green',.01)
        cube('slot',(0,-.35,1.42),(.38,.04,.07),'black',.004); cube('letter flap',(0,-.34,1.16),(.28,.04,.18),'cream2',.01)
    elif theme=='fairy':
        cube('pink rounded mailbox',(0,0,1.25),(.78,.56,.62),'pink',.04); cyl('cream arch door',(0,-.32,1.28),.30,.06,'cream',10,rot=(radians(90),0,0),scale=(1,.8,1)); crystal('top jewel',(0,-.02,1.78),'pink',(.55,.55,.7))
        for side,x in [('l',-.52),('r',.52)]:
            leaf_obj('white wing '+side,(x,-.30,1.32),(.38,.38,.38),'white')
        cube('slot',(0,-.36,1.43),(.34,.04,.07),'black',.004); sphere('heart-ish pink knob',(0,-.38,1.14),.07,'red',6,3)
    elif theme=='wizard':
        cube('purple house box',(0,0,1.22),(.86,.58,.60),'purple',.035); cone('wizard hat roof',(0,0,1.78),.55,.12,.70,'purple',9,scale=(1,.78,1)); cyl('gold hat band',(0,0,1.55),.42,.08,'gold',9,scale=(1,.78,1))
        star('front gold star',(0,-.36,1.55),.13,'gold'); cube('slot',(0,-.35,1.35),(.35,.04,.07),'black',.004); crystal('purple side crystal',(.55,-.18,.25),'purple',(.55,.55,.9)); star('hanging star',(.42,-.18,.70),.08,'gold')
    elif theme=='courier':
        cube('red courier mailbox',(0,0,1.25),(.80,.56,.62),'red',.04); cyl('cream arch door',(0,-.32,1.28),.29,.06,'cream',10,rot=(radians(90),0,0),scale=(1,.8,1)); cube('little red flag',(.30,-.02,1.84),(.06,.06,.35),'wood_dark',.01); cube('flag cloth',(.44,-.02,1.94),(.26,.05,.16),'red',.01)
        for side,x in [('l',-.52),('r',.52)]: leaf_obj('white wing '+side,(x,-.30,1.32),(.36,.36,.36),'white')
        cube('letter flap',(0,-.36,1.17),(.28,.04,.18),'cream2',.01); cube('slot',(0,-.36,1.42),(.34,.04,.07),'black',.004)
    render('mailbox_'+theme,target=(0,0,1.05),h=2.25)

def butterfly():
    clear(); mats()
    cyl('red rounded body',(0,0,.75),.32,1.05,'red',10,scale=(.88,.88,1),bevel=.03)
    sphere('big simple head',(0,-.02,1.45),.43,'skin',10,5,scale=(1.05,1,1.02)); sphere('left ear',(-.42,-.02,1.45),.10,'skin',8,4); sphere('right ear',(.42,-.02,1.45),.10,'skin',8,4)
    sphere('left black eye',(-.14,-.38,1.50),.055,'black',8,4,scale=(.65,.35,1.2)); sphere('right black eye',(.14,-.38,1.50),.055,'black',8,4,scale=(.65,.35,1.2))
    # wings as clean toy-like panels behind body: broad rounded silhouette, readable black border,
    # inset orange panels, and a few large white dots (no tiny noisy details).
    for side,sgn in [('left',-1),('right',1)]:
        upper_outer=poly('rounded black upper wing '+side,[(0.00,-0.06),(.24,.34),(.58,.48),(.88,.26),(.96,-.04),(.73,-.31),(.29,-.28)],'black',.040)
        upper_outer.location=(sgn*.20,.20,1.13); upper_outer.scale=(sgn,1,1)
        upper_inner=poly('soft orange upper wing panel '+side,[(.10,-.04),(.30,.24),(.56,.34),(.76,.19),(.80,-.03),(.62,-.20),(.31,-.19)],'orange',.045)
        upper_inner.location=(sgn*.20,.145,1.13); upper_inner.scale=(sgn,1,1)

        lower_outer=poly('rounded black lower wing '+side,[(0.00,.08),(.28,.18),(.64,.02),(.74,-.28),(.50,-.54),(.18,-.40)],'black',.040)
        lower_outer.location=(sgn*.22,.20,.78); lower_outer.scale=(sgn,1,1)
        lower_inner=poly('soft orange lower wing panel '+side,[(.09,.05),(.30,.10),(.52,-.03),(.59,-.24),(.42,-.40),(.20,-.30)],'orange',.045)
        lower_inner.location=(sgn*.22,.145,.78); lower_inner.scale=(sgn,1,1)

        # larger, simpler dots so they read on mobile and do not look like random crumbs
        for xx,zz,rr in [(sgn*.88,1.28,.060),(sgn*.76,1.02,.052),(sgn*.67,.62,.055)]:
            sphere('large clean white wing dot '+side,(xx,.105,zz),rr,'white',6,3,scale=(1,.45,1))
    render('butterfly_avatar',target=(0,0,1.0),h=2.4)

if __name__=='__main__':
    for t in ['mushroom','leaf','crystal','stone']: rod('rod_'+t,t)
    for t in ['mushroom','leaf','crystal','stone','fairy','wizard','villager','courier']: mailbox('mailbox_'+t,t)
    butterfly()
