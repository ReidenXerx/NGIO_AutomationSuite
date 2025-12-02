# 🔍 NGIO Research Findings - Complete Analysis

**Sources:**
- [Step Modifications: Grass LOD Guide](https://stepmodifications.org/wiki/SkyrimSE:Grass_LOD_Guide)
- [Nexus Mods: NGIO Article 6919](https://www.nexusmods.com/skyrimspecialedition/articles/6919)
- [Nexus Mods: NGIO Article 6920](https://www.nexusmods.com/skyrimspecialedition/articles/6920)

**Date:** November 27, 2025  
**Analysis Version:** v1.4.0 Implementation Review

---

## 🚨 CRITICAL GAPS FOUND

### 1. **Missing NGIO Settings** ❌

We currently ONLY set 4 NGIO settings, but there are **MANY MORE** critical ones!

#### What We Currently Set:
```ini
[Settings]
UseGrassCache=1
OnlyLoadFromCache=0
EnableGrassGeneration=1
DynDOLODGrassMode=1
```

#### What We're MISSING:

**A. ExtendGrassDistance** 🚨 CRITICAL
```ini
ExtendGrassDistance=True
```
- **Purpose:** Extends grass rendering distance beyond normal
- **Impact:** Dramatically increases generation time (from minutes to hours!)
- **Recommendation:** Should be **user-configurable**
- **Default:** True (for LOD compatibility)

**B. ExtendGrassCount** 🚨 CRITICAL
```ini
ExtendGrassCount=False
```
- **Purpose:** Increases grass density count
- **Impact:** Can increase generation time from 25 mins to HOURS
- **Recommendation:** Should default to **False**, warn if enabled
- **Step Guide Says:** "dramatically increases precaching time"

**C. SuperDenseGrass** 🚨 CRITICAL
```ini
SuperDenseGrass=False
```
- **Purpose:** Super high density grass
- **Impact:** Can increase generation time from minutes to MANY HOURS
- **Recommendation:** Should default to **False**, strong warning if enabled
- **Step Guide Says:** "dramatically increases precaching time"

**D. EnsureMaxGrassTypesPerTextureSetting** ⚠️ IMPORTANT
```ini
EnsureMaxGrassTypesPerTextureSetting=15
```
- **Purpose:** Max grass types per texture (grass mod specific)
- **Impact:** Varies by grass mod
- **Example:** Cathedral Landscapes uses 15
- **Recommendation:** User-configurable, no universal default
- **Note:** This is BAKED INTO THE CACHE

**E. OverwriteMinGrassSize** ⚠️ IMPORTANT
```ini
OverwriteMinGrassSize=67
```
- **Purpose:** Overrides Skyrim.ini iMinGrassSize
- **Impact:** Controls grass density (higher = less dense = better performance)
- **Example:** Cathedral Landscapes uses 67
- **Recommendation:** User-configurable
- **Note:** This is BAKED INTO THE CACHE, can't change after generation

**F. GlobalGrassScale** ⚠️ IMPORTANT
```ini
GlobalGrassScale=1.15
```
- **Purpose:** Grass height multiplier
- **Impact:** Visual only, slight performance impact
- **Example:** 1.15 makes grass 15% taller
- **Recommendation:** User-configurable
- **Note:** This is BAKED INTO THE CACHE

**G. OnlyPregenerateWorldSpaces** ⚠️ IMPORTANT
```ini
OnlyPregenerateWorldSpaces=Tamriel,DLC2SolstheimWorld,...
```
- **Purpose:** Filter which worldspaces to generate
- **Impact:** Can cut generation time in HALF
- **Recommendation:** Use xEdit script to auto-detect
- **Note:** Huge time saver for users with many modded worldspaces

---

### 2. **OnlyLoadFromCache State Management** 🚨 CRITICAL

We have this **BACKWARDS**!

#### Current Implementation:
```python
# We set OnlyLoadFromCache=0 during generation ✅ CORRECT
# But we DON'T change it back after! ❌ WRONG
```

#### Correct Implementation:
```ini
# DURING GENERATION:
OnlyLoadFromCache=False  # Allow generation

# AFTER GENERATION:
OnlyLoadFromCache=True   # Only use cache, don't regenerate
```

**Why this matters:**
- If left as `False`, game will try to regenerate cache on every launch
- If set to `True`, game uses pre-generated cache (fast loading)
- We have `configure_ngio_for_cache_use()` method but **never call it!**

---

### 3. **Worldspace Filtering** ⚠️ MISSING FEATURE

According to Step Guide, this can **cut generation time in HALF**:

#### Process:
1. Run xEdit script: "List worldspaces with grass"
2. Script outputs list of worldspaces that have grass
3. Add to `OnlyPregenerateWorldSpaces` in GrassControl.ini
4. NGIO only processes those worldspaces (skips irrelevant ones)

#### Example Output:
```
Tamriel
DLC2SolstheimWorld
DLC01Vampire
[modded worldspaces...]
```

**Impact:**
- Without filter: Process ALL worldspaces (including empty ones)
- With filter: Process ONLY worldspaces with grass
- **Time saving: 25-50% reduction**

**Implementation Challenge:**
- Requires xEdit integration (external tool)
- Could provide manual input option
- Could scan for worldspace mods

---

## 📊 NGIO Settings Complete Reference

### Critical Settings Matrix:

| Setting | Current | Correct | Impact | Priority |
|---------|---------|---------|--------|----------|
| UseGrassCache | ✅ 1 | ✅ 1 | Required | Critical |
| EnableGrassGeneration | ✅ 1 | ✅ 1 | Required | Critical |
| OnlyLoadFromCache | ✅ 0 | ⚠️ 0→1 | State mgmt | Critical |
| DynDOLODGrassMode | ✅ 1 | ✅ 1 | LOD compat | Critical |
| ExtendGrassDistance | ❌ Missing | ⚠️ True | LOD req'd | Critical |
| ExtendGrassCount | ❌ Missing | ⚠️ False | Perf | High |
| SuperDenseGrass | ❌ Missing | ⚠️ False | Perf | High |
| OverwriteMinGrassSize | ❌ Missing | 🎨 User | Density | Medium |
| GlobalGrassScale | ❌ Missing | 🎨 User | Height | Medium |
| EnsureMaxGrassTypes... | ❌ Missing | 🎨 User | Compat | Medium |
| OnlyPregenerateWorldSpaces | ❌ Missing | 🎨 User | Perf | Medium |

**Legend:**
- ✅ We handle correctly
- ⚠️ Required, we're missing
- 🎨 User preference
- ❌ Not implemented

---

## 🎯 DynDOLOD & Grass LOD Integration

### NEW REQUIREMENT: LOD Billboard Generation

The user wants to add **grass LOD support**, which requires:

#### 1. **TexGen Integration** (Creates Billboards)

**Purpose:** Generate grass LOD billboard textures and atlases

**Process:**
```
1. Run TexGen with grass LOD enabled
2. TexGen reads grass cache files
3. Creates texture atlases for grass LOD
4. Outputs billboards to TexGen_Output
```

**Settings:**
- Units per pixel (resolution control)
- Ambient/Direct lighting
- Grass brightness modifiers

**Requirements:**
- DynDOLOD 3 installed
- Grass cache must exist first
- TexGen executable: `TexGenx64.exe`

#### 2. **DynDOLOD Integration** (Generates LODs)

**Purpose:** Generate grass LODs using billboards from TexGen

**Process:**
```
1. TexGen billboards created (prerequisite)
2. Run DynDOLOD with Grass LOD checkbox
3. DynDOLOD analyzes grass cache
4. Places grass LOD meshes in LOD4
5. Outputs DynDOLOD_Output mod
```

**Settings:**
- Grass LOD Mode: 1 or 2
  - Mode 1: Full grass to uGridsToLoad, LOD beyond
  - Mode 2: Full grass to uLargeRefLODGridSize, LOD beyond
- Grass LOD Density: 35-100 (lower = better performance)
- Complex Grass: On/Off (for ENB)

**Requirements:**
- DynDOLOD 3 alpha installed
- DynDOLOD Resources SE 3
- TexGen output exists
- Grass cache exists

#### 3. **Workflow Integration**

**Current Workflow:**
```
1. Configure season
2. Launch Skyrim
3. Generate grass cache
4. Process files (rename)
5. Create archive
```

**NEW Workflow (with LOD):**
```
1. Configure season
2. Launch Skyrim
3. Generate grass cache
4. Process files (rename)
5. [NEW] Run TexGen (create billboards)
6. [NEW] Run DynDOLOD (create LODs)
7. Create archive (include LODs)
```

---

## 📝 Implementation Priority

### Phase 1: Fix Critical Gaps (MUST DO)

**Priority 1A: Missing NGIO Settings**
- [ ] Add `ExtendGrassDistance` setting (default: True)
- [ ] Add `ExtendGrassCount` setting (default: False)
- [ ] Add `SuperDenseGrass` setting (default: False)
- [ ] Warn user about performance impact

**Priority 1B: State Management**
- [ ] Set `OnlyLoadFromCache=False` during generation
- [ ] Set `OnlyLoadFromCache=True` after completion
- [ ] Add this to cleanup phase

**Priority 1C: User-Configurable Settings**
- [ ] Add `OverwriteMinGrassSize` to config (default: 60)
- [ ] Add `GlobalGrassScale` to config (default: 1.0)
- [ ] Add `EnsureMaxGrassTypesPerTextureSetting` to config (default: 7)
- [ ] Update YAML config template

### Phase 2: Performance Optimizations (SHOULD DO)

**Priority 2A: Worldspace Filtering**
- [ ] Add `OnlyPregenerateWorldSpaces` support
- [ ] Provide manual input option
- [ ] Document xEdit script process
- [ ] Auto-detect common worldspaces (Tamriel, DLC2SolstheimWorld)

**Priority 2B: Generation Optimizations**
- [ ] Add option to disable ENB during generation
- [ ] Add option to lower resolution during generation
- [ ] Document these optimizations in guide

### Phase 3: LOD Integration (NEW FEATURE)

**Priority 3A: TexGen Integration**
- [ ] Detect TexGen installation
- [ ] Run TexGen with grass LOD settings
- [ ] Parse TexGen output
- [ ] Handle errors and retries

**Priority 3B: DynDOLOD Integration**
- [ ] Detect DynDOLOD installation
- [ ] Run DynDOLOD with grass LOD
- [ ] Configure density settings
- [ ] Parse DynDOLOD output

**Priority 3C: Archive Integration**
- [ ] Include TexGen output in archives
- [ ] Include DynDOLOD output in archives
- [ ] Update installation instructions
- [ ] Add LOD-specific metadata

---

## 🎯 Recommended Configuration Profiles

### Profile 1: Fast Generation (Default)
```ini
[NGIO Settings]
ExtendGrassDistance=False
ExtendGrassCount=False
SuperDenseGrass=False
OverwriteMinGrassSize=80
GlobalGrassScale=1.0
EnsureMaxGrassTypesPerTextureSetting=7

[Estimated Time]
Small load order: 10-15 minutes
Large load order: 30-45 minutes
```

### Profile 2: LOD Compatible (Recommended)
```ini
[NGIO Settings]
ExtendGrassDistance=True   # Required for LOD
ExtendGrassCount=False
SuperDenseGrass=False
OverwriteMinGrassSize=67
GlobalGrassScale=1.0
EnsureMaxGrassTypesPerTextureSetting=15  # Grass mod specific

[Estimated Time]
Small load order: 20-30 minutes
Large load order: 60-90 minutes
```

### Profile 3: Maximum Quality (Advanced)
```ini
[NGIO Settings]
ExtendGrassDistance=True
ExtendGrassCount=True      # WARNING: Can take HOURS
SuperDenseGrass=False      # WARNING: Can take MANY HOURS
OverwriteMinGrassSize=40   # Very dense
GlobalGrassScale=1.15
EnsureMaxGrassTypesPerTextureSetting=15

[Estimated Time]
Small load order: 1-2 hours
Large load order: 3-6 hours
WARNING: ExtendGrassCount can make this 10x longer!
```

---

## 🔍 Settings That Are BAKED Into Cache

These settings **cannot be changed** after generation without regenerating:

1. ✅ `OverwriteMinGrassSize` - Grass density
2. ✅ `GlobalGrassScale` - Grass height
3. ✅ `EnsureMaxGrassTypesPerTextureSetting` - Grass variety
4. ✅ `ExtendGrassDistance` - Grass render distance
5. ✅ `ExtendGrassCount` - Grass count
6. ✅ `SuperDenseGrass` - Ultra density

**Consequence:** User must choose these settings **BEFORE** generation!

---

## 📋 Questions Answered

### Q1: NGIO Settings
**Answer:** We're missing 7 critical settings! See matrix above.

### Q2: Skyrim.ini Settings
**Answer:** NGIO's `OverwriteMinGrassSize` overrides Skyrim.ini's `iMinGrassSize`. We should handle this in NGIO config, not Skyrim.ini.

### Q3: po3_SeasonsOfSkyrim.ini Settings
**Answer:** We only need to change `Season Type = [0-5]`. Current implementation is correct.

### Q4: Worldspace Generation
**Answer:** NGIO generates for ALL loaded worldspaces by default. Can filter with `OnlyPregenerateWorldSpaces`.

### Q5: Completion Indicator
**Answer:** PrecacheGrass.txt deletion is the ONLY reliable indicator. No other files or logs.

### Q6: Post-Generation Steps
**Answer:** We should:
- ✅ Rename files (we do)
- ✅ Create archives (we do)
- ⚠️ Set `OnlyLoadFromCache=True` (we DON'T do!)
- ❌ Optionally run TexGen/DynDOLOD for LODs (new feature)

### Q7: Mod Manager Detection
**Answer:** Not critical. Users typically close MO2 themselves. Could add warning.

### Q8: Special Worldspaces
**Answer:** No special handling needed. NGIO processes all worldspaces equally.

### Q9: Alternative Seasonal Systems
**Answer:** po3_SeasonsOfSkyrim is the standard. Other seasonal mods exist but are less common.

---

## 🚀 Implementation Action Items

### Immediate (v1.5.0):

1. **Add Missing NGIO Settings**
   - ExtendGrassDistance, ExtendGrassCount, SuperDenseGrass
   - OverwriteMinGrassSize, GlobalGrassScale, EnsureMaxGrassTypes...
   - Update config_manager.py

2. **Fix OnlyLoadFromCache State**
   - Set to False during generation
   - Set to True after completion
   - Add to automation_suite.py cleanup

3. **Update YAML Config**
   - Add all new settings
   - Provide sensible defaults
   - Add performance warnings

4. **Update Documentation**
   - NGIO settings reference
   - Performance impact warnings
   - Baked settings explanation

### Future (v1.6.0+):

1. **Worldspace Filtering**
   - Manual input option
   - Auto-detect common worldspaces
   - xEdit script integration (advanced)

2. **TexGen Integration**
   - Detect installation
   - Run with grass LOD
   - Include in archives

3. **DynDOLOD Integration**
   - Detect installation
   - Run with grass LOD
   - Include in archives

---

## 📊 Coverage Update

### Before Research:
- **Critical Settings:** 4/11 = 36% ❌
- **Process Steps:** 5/7 = 71% ⚠️
- **LOD Support:** 0/1 = 0% ❌

### After Implementing Findings:
- **Critical Settings:** 11/11 = 100% ✅
- **Process Steps:** 7/7 = 100% ✅
- **LOD Support:** 1/1 = 100% ✅ (future)

---

## 🎯 Conclusion

**Major Findings:**
1. We're missing 7 critical NGIO settings
2. We have state management backwards (OnlyLoadFromCache)
3. Worldspace filtering can halve generation time
4. LOD integration is a major new feature request
5. Many settings are BAKED and can't be changed post-generation

**Recommended Priority:**
1. ✅ Fix missing settings (v1.5.0)
2. ✅ Fix state management (v1.5.0)
3. ⚠️ Add worldspace filtering (v1.5.0 or v1.6.0)
4. ⚠️ Add LOD integration (v1.6.0 - major feature)

**Impact:**
- Current implementation: Works but suboptimal
- With fixes: Professional, complete, optimal
- With LOD: Industry-leading automation solution

---

**Research Sources:**
- [Step Modifications: Grass LOD Guide](https://stepmodifications.org/wiki/SkyrimSE:Grass_LOD_Guide)
- [Nexus: NGIO Generation Guide](https://www.nexusmods.com/skyrimspecialedition/articles/6919)
- [Nexus: NGIO Seasonal Guide](https://www.nexusmods.com/skyrimspecialedition/articles/6920)

