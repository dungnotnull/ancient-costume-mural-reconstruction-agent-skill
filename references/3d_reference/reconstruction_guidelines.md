# 3D Reconstruction Guidelines — Ancient Costume Mural Reconstruction

## Overview

This document provides technical guidelines for 3D reconstruction of ancient
costumes from iconographic, construction, and materials analysis.

---

## Modeling Workflow

### Phase 1: Reference Gathering

**Inputs Required:**
- Iconographic analysis (form, drape, layering)
- Construction analysis (pattern, seams, fastening)
- Materials analysis (fabric type, weight, behavior)
- Scale references (human figure, object measurements)

**Deliverables:**
- Layer specification document
- Material assignment per panel
- Confidence grading per element

---

### Phase 2: Body Foundation

**Human Body Base:**
- Use period-appropriate anthropometry (see table below)
- Avoid exaggerated artistic proportions
- Use neutral standing pose (for reconstruction, not action)

| Period | Typical Height (cm) | Characteristics | Stature |
|--------|---------------------|-----------------|---------|
| Han | 165-175 (men), 155-165 (women) | Slender, refined | Medium |
| Tang | 170-180 (men), 158-168 (women) | Fuller, robust | Medium-tall |
| Song | 165-175 (men), 155-165 (women) | Refined, elegant | Medium |
| Ming/Qing | Variable by class | Variable | Variable |

**Body Type Selection:**
- **Elite/Court**: Well-nourished, robust
- **Commoners**: Leaner, working physique
- **Elderly**: Reduced stature, some kyphosis
- **Children**: Age-appropriate proportions

---

### Phase 3: Layer Construction

**Layer Order (inside to outside):**

```
Layer 0: Body foundation (skin base, undergarments if visible)
Layer 1: Under-layer (underwear, chemise, inner robe)
Layer 2: Mid-layer (main garment: robe, tunic, dress)
Layer 3: Outer-layer (jacket, cape, outer robe)
Layer 4: Accessories (sash, belt, headwear, footwear)
```

**For Each Layer:**

1. **Create base mesh**
   - Use quad-based topology
   - Follow fabric weave direction in edge flow
   - Edge length: 1-2cm for adequate drape resolution

2. **Apply material assignment**
   - Assign fabric type per panel
   - Set weight, stiffness, friction parameters
   - Apply color from materials analysis

3. **Add seam details**
   - Mark seam positions from construction analysis
   - Add seam thickness/texture where visible
   - Ensure seams follow period construction

4. **Validate against reference**
   - Check silhouette matches iconography
   - Check drape matches fabric behavior
   - Check layering matches visual evidence

---

### Phase 4: Material Properties

**Fabric Property Parameters:**

```python
# Reference material properties for 3D implementation
material_properties = {
    # Silk varieties
    "silk_fine_gauze": {
        "weight_gsm": 20-40,
        "bending_stiffness": 0.1-0.3,
        "shear_stiffness": 0.2-0.4,
        "drape_factor": 1.5,  # High drape
        "friction": 0.3,
        "stretch": 0.08,
        "transparency": 0.4
    },
    "silk_medium": {
        "weight_gsm": 40-70,
        "bending_stiffness": 0.3-0.5,
        "shear_stiffness": 0.4-0.6,
        "drape_factor": 1.2,
        "friction": 0.4,
        "stretch": 0.05,
        "transparency": 0.1
    },
    "silk_heavy_brocade": {
        "weight_gsm": 80-120,
        "bending_stiffness": 0.5-0.8,
        "shear_stiffness": 0.6-0.9,
        "drape_factor": 0.9,  # Stiffer drape
        "friction": 0.5,
        "stretch": 0.03,
        "transparency": 0.0
    },

    # Bast fibers
    "hemp_medium": {
        "weight_gsm": 150-200,
        "bending_stiffness": 0.8-1.2,
        "shear_stiffness": 1.0-1.5,
        "drape_factor": 0.7,  # Stiff
        "friction": 0.6,
        "stretch": 0.02,
        "transparency": 0.0
    },
    "ramie_fine": {
        "weight_gsm": 80-120,
        "bending_stiffness": 0.6-0.9,
        "shear_stiffness": 0.8-1.2,
        "drape_factor": 0.9,
        "friction": 0.5,
        "stretch": 0.02,
        "transparency": 0.0
    },

    # Other fibers
    "cotton_medium": {
        "weight_gsm": 100-150,
        "bending_stiffness": 0.5-0.8,
        "shear_stiffness": 0.7-1.0,
        "drape_factor": 1.0,
        "friction": 0.5,
        "stretch": 0.04,
        "transparency": 0.0
    }
}
```

**Using These Properties:**
- Adjust simulation parameters in your 3D software
- Use as reference for visual behavior
- Modify based on specific fabric analysis

---

### Phase 5: Detail Level Assignment

**High Detail Areas:**
- Visible seams and stitching
- Fastening mechanisms (ties, buttons, belts)
- Embroidery and woven patterns (if visible)
- Face and hands (if figure shown)

**Medium Detail Areas:**
- General garment drape
- Layer interaction
- Fabric surface texture
- Footwear (if secondary)

**Low Detail Areas:**
- Background garments
- Obscured garment sections
- Underlayers (not visible)
- Distant figures

---

### Phase 6: Scene Composition

**Viewpoint Considerations:**
- Match primary reference viewpoint (usually front)
- If multiple views available, compose for optimal visibility
- Consider lighting conditions of reference source

**Scale Accuracy:**
- 1 unit = 1 cm (recommended scale)
- Verify against human height reference
- Check garment proportions against reference

**Presentation Options:**
- Single view (if that's all reference provides)
- Multiple views (if reference allows)
- Turntable (for 360° presentation, if evidence supports)
- Exploded view (to show layering, with disclaimer about conjecture)

---

## Confidence Grading in 3D

**Per-Element Confidence:**

| Element | High (H) | Medium (M) | Low (L) |
|---------|----------|-----------|---------|
| **Overall silhouette** | Multiple views, clear | Single good view | Fragmentary |
| **Pattern shape** | Extant example | Iconography + construction | Inference |
| **Seam placement** | Visible or from extant | Inferred from construction | Speculative |
| **Material assignment** | Scientific analysis | Visual + period knowledge | Speculative |
| **Color** | Well-preserved visual | Faded but inferable | Lost/faded |
| **Layering** | All layers visible | Some layers inferred | Mostly inferred |

**Overall Model Confidence:**

```
IF all major elements H:
    Overall: Evidence-Based 3D Reconstruction (High confidence)

IF mix of H and M:
    Overall: Evidence-Based 3D Reconstruction (Medium-High confidence)

IF any L elements:
    Overall: Plausible 3D Reconstruction (Medium confidence)
    OR: Speculative 3D Reconstruction (Low confidence)
```

---

## Scenario Building

### Best Case Scenario

**Use:** Ideal reconstruction, maximum confidence

**Characteristics:**
- All elements High confidence
- Multiple extant examples
- Clear iconographic evidence
- Scientific material analysis

**Documentation:**
- Specify which elements are certain
- Note any remaining uncertainties
- Provide alternative interpretations

---

### Base Case Scenario

**Use:** Most likely reconstruction, standard confidence

**Characteristics:**
- Mix of High and Medium confidence
- Single extant example or multiple iconographic sources
- Some inference required
- Standard material knowledge

**Documentation:**
- Specify which elements require inference
- Explain basis for inferences
- Note what would improve confidence

---

### Worst Case Scenario

**Use:** Minimal viable reconstruction, lowest confidence

**Characteristics:**
- Multiple Low confidence elements
- Fragmentary evidence
- Significant reconstruction/conjecture
- Limited sources

**Documentation:**
- Flag all speculative elements
- Provide alternative interpretations
- Explain evidence gaps
- Recommend additional research

---

## Technical Implementation Guidelines

### Topology

**Recommended:**
- Quad-based mesh (better for subdivision)
- Edge flow follows fabric weave direction
- Adequate resolution (edge length 1-2cm)
- Clean poles (avoid triangles at poles)

**Avoid:**
- N-gons (faces with >4 edges)
- Extreme stretching (distorts UVs and simulation)
- Inconsistent edge flow (confuses simulation)

---

### UV Mapping

**Guidelines:**
- Unwrap each layer separately
- Minimize distortion (especially for patterns)
- Organize UVs for texture painting
- Include seam allowances in UVs

---

### Rigging (If Animation Required)

**Simplified Rig:**
- Root → Body → Layers hierarchy
- Simple joint hierarchy for basic poses
- No facial rigging (unless specifically required)

**Full Rig:**
- Complete skeleton for natural movement
- Cloth simulation handles most drape
- Blend shapes for expressions (if needed)

---

### Rendering

**Lighting:**
- Match reference lighting when possible
- Use three-point setup for general presentation
- Avoid dramatic lighting that obscures details

**Materials:**
- Use physically based rendering (PBR)
- Apply roughness maps for fabric realism
- Use normal maps for weave texture
- Consider subsurface scattering for silk

---

## Common Pitfalls to Avoid

### 1. Over-Interpreting Single Views

**Problem:** Reconstructing back view from front view only

**Solution:**
- Clearly flag back view as speculative
- Use period construction knowledge to inform inference
- Provide alternative interpretations

### 2. Ignoring Fabric Behavior

**Problem:** Heavy fabric draping like light fabric

**Solution:**
- Use material properties from analysis
- Test drape with simulation
- Adjust for fabric weight and stiffness

### 3. Modern Silhouette Projection

**Problem:** Ancient garment looking too modern

**Solution:**
- Study period proportions carefully
- Use extant examples when available
- Avoid modern fashion influences

### 4. Excessive Detail

**Problem:** Adding details not supported by evidence

**Solution:**
- Only include details with evidence basis
- Flag speculative details
- Consider confidence grading

### 5. Ignoring Layer Compression

**Problem:** Layers don't compress when multiple layers worn

**Solution:**
- Account for layer compression in simulation
- Adjust volume accordingly
- Consider realistic layer thickness

---

## Validation Checklist

**Before Finalizing:**

- [ ] Silhouette matches iconographic reference?
- [ ] Layer order matches visual evidence?
- [ ] Materials assigned per analysis?
- [ ] Confidence grades assigned to all elements?
- [ ] Scenario built (best/base/worst)?
- [ ] Limitations disclosed?
- [ ] Scale verified against reference?
- [ ] Alternative interpretations documented?

---

## Deliverables Specification

**Required Files:**
1. 3D model files (FBX, OBJ, or native format)
2. Material specification document
3. Confidence grading document
4. Scenario documentation
5. Limitations disclosure
6. Technical notes (implementation guidance)

**Optional Files:**
- Turntable video
- Multiple renders (different views)
- Wireframe renders (showing topology)
- Comparison with reference images

---

## References

- **Iconographic Analysis:** See references/iconography/
- **Construction Methods:** See references/construction/
- **Materials Science:** See references/materials/
- **Academic Sources:** See SECOND-KNOWLEDGE-BRAIN.md §2

---

**Document Version:** 2.0.0
**Last Updated:** 2025-01-27
