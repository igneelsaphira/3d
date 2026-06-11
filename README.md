# 3D Assets

Repositorio de assets 3D low-poly/mobile-friendly para juego social.

## Asset incluido

### Leaf Bed / Camita de hoja

Camita miniatura mágica de bosque/hada, con estructura de madera cálida, colchón crema, almohada simple y una hoja grande como cobertor principal.

**Objetivo visual:** cozy, cute, limpia, low-poly y apta para juego 3D liviano.

**Versión actual recomendada:** `leaf_bed_final_clean_v1`

**Archivos principales:**

- `assets/leaf_bed_final_clean_v1/model.glb` — modelo runtime listo para usar.
- `assets/leaf_bed_final_clean_v1/source.blend` — archivo editable en Blender.
- `assets/leaf_bed_final_clean_v1/perspective.png` — preview perspective final.
- `scripts/make_leaf_bed_final_clean_v1.py` — script procedural usado para generar/exportar el asset.
- `prompts/leaf_bed_prompt.md` — prompt actualizado y reglas aprendidas para recrear/mejorar la camita.

**Versión histórica:** `assets/leaf_bed_v6/` conserva la versión con contact sheet FRONT, SIDE, BACK, TOP y PERSPECTIVE.

## Especificaciones

- Formato runtime: `.glb`
- Fuente editable: `.blend`
- Estilo: low-poly, mobile-friendly, flat colors
- Triángulos aproximados: 1429
- Tamaño GLB aproximado: 116 KB
- Texturas: no usa texturas externas; materiales simples por color

## Generar nuevamente

Requiere Blender instalado.

```bash
blender --factory-startup -b --python scripts/make_leaf_bed_final_clean_v1.py
```

El script exporta a `/root/leaf_bed_final_clean_v1` porque fue generado en el entorno de trabajo del agente.

## Notas

Este asset es una cama/prop de ambiente. Si se usa en un repositorio de wardrobe/wearables, habría que adaptarlo a un formato compatible, por ejemplo como `bedroll`, mochila o item de mano.
