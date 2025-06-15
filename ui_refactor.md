# UI Refactoring Plan: Scalable Component Architecture

## Problem Statement

### Current Issues
- **Inconsistent sizing**: Mix of hardcoded values (`margin = 15`) and proportional calculations (`screen_width // 30`)
- **Header duplication**: 8+ files manually create headers with `pygame.Rect(0, header_top_margin, screen_width, header_height)`
- **No resolution awareness**: Components don't adapt to different screen sizes
- **Scattered layout logic**: Each component calculates spacing differently
- **Fullscreen Pi constraint**: App uses `FULLSCREEN = True` on Pi, requiring precise scaling

### Why This Matters
- **Multi-resolution support**: Need to work on Pi (320x240) and development (800x600+)
- **Maintainability**: Currently changing spacing requires editing multiple files
- **Consistency**: UI elements should look proportional across all screen sizes
- **Future-proofing**: Easy to add new screen size support

## Solution Architecture

### Core Principle: Single Responsibility + Centralized Scaling
- **UIScaler**: Handles all size/spacing calculations
- **Components**: Focus on their specific functionality
- **Views**: Compose components without layout concerns

## Implementation Plan

### Phase 1: Foundation - UIScaler System
**File:** `utils/ui_scaler.py`

**Purpose:** Centralize all UI scaling logic to eliminate hardcoded values and inconsistent calculations

**Key Features:**
- Screen-aware scaling based on base resolution (320x240)
- Standardized margin/padding calculations
- Font scaling with minimum/maximum bounds
- Component size scaling

**Replaces:** 
- `screen_width // 30` calculations in multiple files
- Hardcoded margins like `15`, `20`, `30`
- Mixed `max(8, screen_width // 30)` logic

### Phase 2: Header Component Creation
**File:** `ui/components/header.py`

**Purpose:** Eliminate header duplication across 8+ files

**Current Duplication Pattern:**
```python
# Found in system_info_view.py, controls_view.py, etc.
header_height = config_module.HEADER_HEIGHT
header_rect = pygame.Rect(0, header_top_margin, screen_width, header_height)
pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)
```

**Benefits:**
- Single implementation for all headers
- Consistent styling and positioning
- Automatic scaling integration

### Phase 3: Component Scaling Integration

#### `ui/components/horizontal_status_bar.py`
**Problem:** Uses `max(5, self.rect.width // 40)` for margins
**Solution:** Replace with `ui_scaler.margin()`

#### `ui/components/vertical_bar_graph.py`
**Problem:** Hardcoded values like `self.scale_top_y = self.scale_rect.top + 15`
**Solution:** Replace with `ui_scaler.padding()`

#### `ui/components/character_selector.py`
**Problem:** Complex layout with hardcoded `title_height = 30`, `padding = 20`
**Solution:** Use UIScaler for all dimensions

#### `ui/components/list_menu_base.py`
**Problem:** `header_top_margin = screen_height // 20` calculations
**Solution:** Use UIScaler standardized spacing

### Phase 4: View Updates

**Files Requiring Header Component:**
- `ui/views/system_info_view.py` - Manual header creation
- `ui/views/settings/controls_view.py` - Manual header creation
- `ui/views/sensors_menu_view.py` - Manual header creation
- `ui/views/schematics_menu_view.py` - Manual header creation
- `ui/views/schematics_3d_viewer.py` - Manual header creation
- `ui/views/secret_games_view.py` - Manual header creation
- `ui/views/sensor_view.py` - Uses `render_title()` but inconsistently

**Migration Pattern:**
```python
# Before
header_rect = pygame.Rect(0, screen_height // 20, screen_width, config.HEADER_HEIGHT)

# After  
header = Header(ui_scaler, config)
header_rect = header.draw(screen, "Title", fonts)
```

### Phase 5: Display Manager Integration
**File:** `ui/display_manager.py`

**Changes:**
- Create UIScaler in `init_display()`
- Pass UIScaler to all view functions
- Update function signatures to include `ui_scaler` parameter

### Phase 6: Configuration Updates
**File:** `config/ui.py`

**Additions:**
- UI scaling configuration options
- Responsive breakpoints for different screen sizes
- Base resolution definition

## Benefits

### Immediate
- **Consistency**: All UI elements scale proportionally
- **Maintainability**: Change spacing in one place
- **Code reduction**: Eliminate 8+ header implementations

### Long-term
- **Multi-resolution support**: Easy to add new screen sizes
- **Component reusability**: Scaled components work anywhere
- **Future-proofing**: New components automatically scale correctly

## Implementation Strategy

### Order of Execution
1. **UIScaler creation** - Foundation for everything else
2. **Header component** - Immediate impact on code duplication
3. **Display manager integration** - Plumbing to pass UIScaler
4. **Component updates** - One component at a time
5. **View updates** - One view at a time
6. **Testing** - Both Pi (320x240) and Windows (800x600+)

### Risk Mitigation
- **One file at a time**: Maintains working system during transition
- **No breaking changes**: Existing code continues working
- **Incremental testing**: Verify each component works before moving to next

## Success Criteria
- [ ] All hardcoded spacing values eliminated
- [ ] Header duplication removed
- [ ] UI scales correctly on Pi (320x240) and Windows (800x600)
- [ ] No visual regressions on existing functionality
- [ ] Easy to add new screen size support

## Files to be Modified

### New Files
- `utils/ui_scaler.py`
- `ui/components/header.py`

### Modified Files
- `ui/display_manager.py`
- `config/ui.py`
- `ui/components/horizontal_status_bar.py`
- `ui/components/vertical_bar_graph.py`
- `ui/components/character_selector.py`
- `ui/components/list_menu_base.py`
- `ui/views/system_info_view.py`
- `ui/views/settings/controls_view.py`
- `ui/views/sensors_menu_view.py`
- `ui/views/schematics_menu_view.py`
- `ui/views/schematics_3d_viewer.py`
- `ui/views/secret_games_view.py`
- `ui/views/sensor_view.py` 