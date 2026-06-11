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
    # Clean chroma approval render: floor + world color only. Avoid the dark corner wall
    # that made the v1 contact sheets look dirty and less toy-like.
    bpy.ops.object.light_add(type='AREA', location=(0,-3.7,4.2)); l=bpy.context.object; l.data.energy=500; l.data.size=5
    bpy.ops.object.light_add(type='AREA', location=(3,2.8,3.5)); lf=bpy.context.object; lf.data.energy=120; lf.data.size=4
    bpy.ops.object.camera_add(location=(3.0,-4.6,h)); cam=bpy.context.object
    direction=Vector(target)-cam.location; cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); cam.data.lens=58; bpy.context.scene.camera=cam
    cube('chroma floor',(0,0,-.09),(5,5,.04),'chroma')

def render(name,target=(0,0,.7),h=2.1):
    camera(target,h); bpy.context.scene.render.engine='BLENDER_EEVEE'; bpy.context.scene.eevee.taa_render_samples=24
    bpy.context.scene.render.resolution_x=900; bpy.context.scene.render.resolution_y=900; bpy.context.scene.view_settings.view_transform='Standard'
    # Force a clean chroma-green world in Blender 4 headless. Without node setup,
    # EEVEE can render the empty background as dark gray even if scene.world.color is set.
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new('Clean Chroma World')
    bpy.context.scene.world.color=(.333,.8,.266)
    bpy.context.scene.world.use_nodes=True
    bg=bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value=(.333,.8,.266,1)
        bg.inputs['Strength'].default_value=.9
    out=os.path.join(ROOT,name); os.makedirs(out,exist_ok=True); bpy.context.scene.render.filepath=os.path.join(out,'perspective.png')
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out,'source.blend')); bpy.ops.render.render(write_still=True)
    for o in bpy.context.scene.objects: o.select_set(False)
    for o in bpy.context.scene.objects:
        if o.type=='MESH' and not o.name.startswith('chroma'): o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out,'model.glb'), use_selection=True, export_format='GLB')

def rod(name,theme):
    clear(); mats()
    # v2: keep each reference theme, but make the rods read cleaner in thumbnail:
    # thicker toy proportions, fewer tiny crumbs, bigger lure silhouettes, clearer reel.
    cyl('main tapered wooden rod',(0,0,.73),.065,2.45,'wood',8,rot=(0,radians(82),0),scale=(1,1,1),bevel=.008)
    cyl('dark rod tip',(1.08,0,.79),.045,.30,'wood_dark',8,rot=(0,radians(82),0),scale=(1,1,1))
    cyl('rounded handle grip',(-1.04,0,.62),.17,.62,'wood',8,rot=(0,radians(82),0),scale=(1.25,.86,1),bevel=.03)
    cyl('dark handle butt',(-1.34,0,.58),.145,.16,'wood_dark',8,rot=(0,radians(82),0),scale=(1.2,.8,1),bevel=.02)
    for x in [-.62,-.25,.30,.78]:
        cyl('chunky gold binding',(x,0,.69+.045*x),.083,.085,'gold',8,rot=(0,radians(82),0),bevel=.008)
    # Larger reel and simple crank, so it reads as fishing gear rather than random beige shape.
    cyl('round cream reel body',(-.30,-.12,.45),.27,.14,'cream',10,rot=(radians(90),0,0),scale=(1,1,1),bevel=.025)
    cyl('dark reel hole',(-.30,-.21,.45),.10,.055,'wood_dark',8,rot=(radians(90),0,0))
    cyl('short reel arm',(-.08,-.22,.34),.038,.30,'wood_dark',8,rot=(0,radians(58),0))
    sphere('round reel knob',(.04,-.25,.25),.055,'gold',8,4,scale=(1,.75,1))
    # Shorter line; lures are brought up so they do not look disconnected from the asset.
    cyl('straight pale fishing line',(1.03,-.02,.47),.012,.52,'white',6,rot=(0,0,0))
    cyl('front guide ring',(0.62,-.03,.58),.052,.028,'wood_dark',8,rot=(radians(90),0,0))
    cyl('middle guide ring',(0.05,-.03,.62),.052,.028,'wood_dark',8,rot=(radians(90),0,0))
    if theme=='mushroom':
        cone('rounded red mushroom handle cap',(-1.36,0,.56),.34,.16,.30,'red',10,rot=(0,radians(82),0),scale=(1,1,.82))
        cyl('cream mushroom handle stem',(-1.22,0,.59),.09,.22,'cream',8,rot=(0,radians(82),0),scale=(1,.85,1),bevel=.012)
        for dx,dz in [(-1.48,.64),(-1.34,.72),(-1.18,.57)]: sphere('large clear mushroom spot',(dx,-.13,dz),.060,'white',6,3)
        cone('mushroom lure cap',(1.03,-.02,.17),.15,.055,.16,'red',8); cyl('mushroom lure stem',(1.03,-.02,.045),.045,.13,'cream',6)
    elif theme=='leaf':
        leaf_obj('large leaf grip guard',(-1.36,0,.58),(.78,.78,.78),'green2')
        leaf_obj('simple leaf lure',(1.03,-.02,.13),(.30,.30,.30),'green2')
        for x,z,s in [(-.74,.80,.19),(-.06,.77,.17),(.42,.74,.16)]: leaf_obj('readable vine leaf',(x,-.035,z),(s,s,s),'green2')
        cyl('green vine wrap along rod',(-.16,-.035,.71),.030,1.28,'green',6,rot=(0,radians(80),0))
    elif theme=='crystal':
        crystal('large pink crystal pommel',(-1.37,0,.56),'pink',(1.05,1.05,1.25))
        crystal('pink crystal lure',(1.03,-.02,.15),'pink',(.58,.58,.85))
        for x,c in [(-.56,'blue'),(-.20,'purple')]: crystal('big clear crystal accent'+x.__str__(),(x,-.035,.82),c,(.52,.52,.62))
        cyl('blue grip band',(-.78,0,.63),.095,.11,'blue',8,rot=(0,radians(82),0),bevel=.006)
        cyl('purple grip band',(-.44,0,.66),.095,.11,'purple',8,rot=(0,radians(82),0),bevel=.006)
    else:
        sphere('faceted stone pommel',(-1.36,0,.57),.28,'stone',8,4,scale=(1.20,.92,1.05))
        sphere('round stone lure',(1.03,-.02,.12),.14,'stone',8,4,scale=(1,.82,1))
        for x in [-.92,-.76,-.60]: cyl('thick rope grip wrap',(x,0,.62),.10,.065,'brown',8,rot=(0,radians(82),0),bevel=.004)
    render('rod_'+theme,target=(-.05,0,.58),h=1.68)

def mailbox(name,theme):
    clear(); mats(); grass_base()
    # v2: stronger toy proportions, cleaner bases/posts, clearer front mail slots.
    cyl('short rounded wooden post',(0,0,.48),.17,.96,'wood',8,bevel=.025)
    cube('chunky cross support',(0,-.02,.78),(.82,.13,.13),'wood_dark',.025)
    cube('small lower brace',(0,-.02,.64),(.48,.11,.10),'wood_dark',.018)
    if theme=='villager':
        cube('warm barrel mailbox box',(0,0,1.24),(.92,.62,.58),'wood',.045)
        cyl('rounded barrel roof',(0,0,1.55),.34,.94,'wood',10,rot=(0,radians(90),0),scale=(1,.56,1),bevel=.018)
        cube('large dark mail slot',(0,-.345,1.35),(.44,.05,.08),'black',.006)
        cyl('simple hanging lantern',(.58,-.18,.86),.10,.16,'gold',6,bevel=.008); cube('warm lantern glass',(.58,-.18,.70),(.16,.10,.20),'cream2',.012)
        cyl('tiny lantern hanger',(.58,-.18,1.00),.025,.20,'wood_dark',6)
    elif theme=='mushroom':
        cube('cream mushroom mailbox body',(0,0,1.23),(.82,.58,.62),'cream',.045)
        cone('broad red mushroom roof',(0,0,1.68),.72,.30,.34,'red',12,scale=(1,.80,1))
        for x,z in [(-.38,1.73),(-.04,1.83),(.31,1.70)]: sphere('big clean mushroom roof dot',(x,-.28,z),.085,'white',6,3)
        cube('front letter flap',(0,-.35,1.16),(.30,.05,.20),'cream2',.012); cube('wide black slot',(0,-.36,1.41),(.40,.045,.075),'black',.004)
    elif theme=='leaf':
        cube('warm wood leaf mailbox body',(0,0,1.23),(.84,.58,.60),'wood',.04)
        leaf_obj('left upright leaf roof',(-.20,-.03,1.67),(.80,.80,.80),'green2')
        leaf_obj('right upright leaf roof',(.24,-.02,1.68),(.76,.76,.76),'green')
        cube('wide black slot',(0,-.36,1.40),(.40,.045,.075),'black',.004)
        leaf_obj('front vine leaf charm',(.43,-.36,1.08),(.22,.22,.22),'green2'); sphere('single white flower dot',(.47,-.38,1.29),.065,'white',6,3)
    elif theme=='crystal':
        cube('cream crystal mailbox body',(0,0,1.22),(.84,.58,.62),'cream',.04)
        cyl('bold purple front gem frame',(0,-.325,1.35),.38,.09,'purple',10,rot=(radians(90),0,0),scale=(1,.66,1),bevel=.01)
        crystal('large top pink crystal',(0,-.03,1.83),'pink',(.82,.82,1.0))
        for x,c,s in [(-.58,'purple',.85),(.58,'blue',.85),(.36,'pink',.70)]: crystal('clear base crystal'+x.__str__(),(x,-.20,.27),c,(s,s,1.08))
        cube('front letter flap',(0,-.36,1.13),(.30,.05,.19),'cream2',.012); cube('wide black slot',(0,-.37,1.43),(.36,.045,.070),'black',.004)
    elif theme=='stone':
        cube('chunky stone mailbox body',(0,0,1.25),(.90,.62,.72),'stone2',.04)
        for x in [-.31,0,.31]: cube('separate top stone cap '+str(x),(x,0,1.68),(.29,.66,.21),'stone2',.024)
        for x,z in [(-.44,1.39),(.42,1.10),(.05,1.51)]: cube('larger moss patch',(x,-.35,z),(.18,.055,.14),'green',.012)
        cube('wide black slot',(0,-.37,1.42),(.40,.045,.075),'black',.004); cube('front letter flap',(0,-.36,1.15),(.30,.05,.19),'cream2',.012)
    elif theme=='fairy':
        cube('rounded pink fairy mailbox body',(0,0,1.24),(.80,.56,.62),'pink',.045)
        cyl('cream round front door',(0,-.33,1.26),.31,.07,'cream',10,rot=(radians(90),0,0),scale=(1,.82,1),bevel=.012)
        crystal('top pink fairy jewel',(0,-.02,1.78),'pink',(.60,.60,.74))
        for side,x in [('left',-.55),('right',.55)]: leaf_obj('large white fairy wing '+side,(x,-.31,1.32),(.42,.42,.42),'white')
        cube('small black slot',(0,-.38,1.43),(.34,.045,.070),'black',.004); sphere('red heart knob',(0,-.40,1.14),.075,'red',6,3,scale=(1,.7,1))
    elif theme=='wizard':
        cube('purple wizard mailbox body',(0,0,1.22),(.88,.58,.60),'purple',.04)
        cone('tall wizard hat roof',(0,0,1.78),.58,.12,.72,'purple',9,scale=(1,.78,1))
        cyl('clear gold hat band',(0,0,1.55),.44,.085,'gold',9,scale=(1,.78,1),bevel=.006)
        star('large front gold star',(0,-.37,1.56),.145,'gold')
        cube('wide black slot',(0,-.37,1.34),(.36,.045,.075),'black',.004)
        crystal('side purple crystal',(.56,-.18,.28),'purple',(.62,.62,.92)); star('simple hanging star',(.43,-.20,.72),.09,'gold')
    elif theme=='courier':
        cube('rounded red courier mailbox body',(0,0,1.24),(.82,.56,.62),'red',.045)
        cyl('cream front envelope door',(0,-.33,1.26),.30,.07,'cream',10,rot=(radians(90),0,0),scale=(1,.82,1),bevel=.012)
        cube('strong flag pole',(.32,-.02,1.82),(.065,.06,.38),'wood_dark',.012); cube('clear red flag cloth',(.47,-.02,1.95),(.30,.055,.17),'red',.012)
        for side,x in [('left',-.55),('right',.55)]: leaf_obj('large white courier wing '+side,(x,-.31,1.31),(.40,.40,.40),'white')
        cube('front envelope flap',(0,-.38,1.16),(.30,.045,.19),'cream2',.012); cube('wide black slot',(0,-.38,1.42),(.35,.045,.070),'black',.004)
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
