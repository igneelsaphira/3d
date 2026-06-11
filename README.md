# 3D Assets

Repositorio de assets 3D low-poly/mobile-friendly para juego social.

## Asset incluido

### Leaf Bed / Camita de hoja

Camita miniatura mágica de bosque/hada, con estructura de madera cálida, colchón crema, almohada simple y una hoja grande como cobertor principal.

**Objetivo visual:** cozy, cute, limpia, low-poly y apta para juego 3D liviano.

**Archivos principales:**

- `assets/leaf_bed_v6/model.glb` — modelo runtime listo para usar.
- `assets/leaf_bed_v6/source.blend` — archivo editable en Blender.
- `assets/leaf_bed_v6/contact_sheet.png` — preview con FRONT, SIDE, BACK, TOP y PERSPECTIVE.
- `assets/leaf_bed_v6/front.png`
- `assets/leaf_bed_v6/side.png`
- `assets/leaf_bed_v6/back.png`
- `assets/leaf_bed_v6/top.png`
- `assets/leaf_bed_v6/perspective.png`
- `scripts/make_leaf_bed_v6.py` — script procedural usado para generar/exportar el asset.

## Especificaciones

- Formato runtime: `.glb`
- Fuente editable: `.blend`
- Estilo: low-poly, mobile-friendly, flat colors
- Triángulos aproximados: 1678
- Tamaño GLB aproximado: 136 KB
- Texturas: no usa texturas externas; materiales simples por color

## Generar nuevamente

Requiere Blender instalado.

```bash
blender --factory-startup -b --python scripts/make_leaf_bed_v6.py
```

El script original exporta a `/root/leaf_bed_v6` porque fue generado en el entorno de trabajo del agente.

## Notas

Este asset es una cama/prop de ambiente. Si se usa en un repositorio de wardrobe/wearables, habría que adaptarlo a un formato compatible, por ejemplo como `bedroll`, mochila o item de mano.
