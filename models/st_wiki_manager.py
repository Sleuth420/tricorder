# --- models/st_wiki_manager.py ---
# Loads and serves cached Star Trek data (characters, spacecraft, species, technology, etc.) for the wiki view.
# Navigation: category list -> item list (within category) -> detail view (scrollable).

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Data dir relative to project root
DATA_DIR_NAME = "data/stapi"
CATEGORIES = ("characters", "spacecraft", "species", "technology", "astronomicalObjects")
DISPLAY_NAMES = {
    "characters": "Characters",
    "spacecraft": "Spacecraft",
    "species": "Species",
    "technology": "Technology",
    "astronomicalObjects": "Locations",
}

VIEW_MODE_CATEGORY = "category"
VIEW_MODE_LIST = "list"
VIEW_MODE_DETAIL = "detail"


class StWikiManager:
    """Loads cached STAPI data from data/stapi/ and provides it for the Star Trek wiki view."""

    def __init__(self, config_module):
        self.config = config_module
        self.project_root = Path(__file__).resolve().parent.parent
        self.data_dir = self.project_root / DATA_DIR_NAME
        self._cache = {}  # category -> list of items
        self._manifest = None
        self._category_index = 0
        self._item_index = 0
        self._view_mode = VIEW_MODE_CATEGORY
        self._detail_scroll_line = 0
        self._detail_lines = []  # cached lines for current detail view
        self._load_data()

    def _load_data(self):
        """Load manifest and category JSON files from data/stapi/."""
        self._cache.clear()
        self._manifest = None
        manifest_path = self.data_dir / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    self._manifest = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Could not load STAPI manifest: %s", e)
        for cat in CATEGORIES:
            path = self.data_dir / f"{cat}.json"
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self._cache[cat] = json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Could not load STAPI %s: %s", cat, e)
                    self._cache[cat] = []
            else:
                self._cache[cat] = []
        logger.debug("STAPI cache: %s", {k: len(v) for k, v in self._cache.items()})

    def reload(self):
        """Reload data from disk (e.g. after fetch from settings)."""
        self._load_data()

    def has_data(self):
        """Return True if at least one category has data."""
        return any(len(self._cache.get(c, [])) > 0 for c in CATEGORIES)

    def get_manifest(self):
        """Return manifest dict (fetched_at, counts) or None."""
        return self._manifest

    def get_categories(self):
        """Return list of (key, display_name) for categories that have data."""
        return [(c, DISPLAY_NAMES.get(c, c)) for c in CATEGORIES if len(self._cache.get(c, [])) > 0]

    def get_category_items(self, category):
        """Return list of items for a category. Each item is a dict (e.g. name, uid, ...)."""
        return self._cache.get(category, [])

    def get_category_index(self):
        return self._category_index

    def set_category_index(self, index):
        cats = self.get_categories()
        if cats:
            self._category_index = max(0, min(index, len(cats) - 1))

    def get_item_index(self):
        return self._item_index

    def set_item_index(self, index):
        cats = self.get_categories()
        if not cats:
            self._item_index = 0
            return
        cat_key = cats[self._category_index][0]
        items = self.get_category_items(cat_key)
        self._item_index = max(0, min(index, len(items) - 1)) if items else 0

    def navigate_next_category(self):
        cats = self.get_categories()
        if not cats:
            return
        self._category_index = (self._category_index + 1) % len(cats)
        self._item_index = 0

    def navigate_prev_category(self):
        cats = self.get_categories()
        if not cats:
            return
        self._category_index = (self._category_index - 1 + len(cats)) % len(cats)
        self._item_index = 0

    def navigate_next_item(self):
        cats = self.get_categories()
        if not cats:
            return
        cat_key = cats[self._category_index][0]
        items = self.get_category_items(cat_key)
        if not items:
            return
        self._item_index = (self._item_index + 1) % len(items)

    def navigate_prev_item(self):
        cats = self.get_categories()
        if not cats:
            return
        cat_key = cats[self._category_index][0]
        items = self.get_category_items(cat_key)
        if not items:
            return
        self._item_index = (self._item_index - 1 + len(items)) % len(items)

    def get_current_item(self):
        """Return the currently selected item dict, or None."""
        cats = self.get_categories()
        if not cats:
            return None
        cat_key = cats[self._category_index][0]
        items = self.get_category_items(cat_key)
        if not items or self._item_index >= len(items):
            return None
        return items[self._item_index]

    def get_current_category_name(self):
        cats = self.get_categories()
        if not cats:
            return ""
        return cats[self._category_index][1]

    # --- View mode: category | list | detail ---
    def get_view_mode(self):
        return self._view_mode

    def enter_list(self):
        """From category screen: open the current category's item list."""
        self._view_mode = VIEW_MODE_LIST
        self._item_index = 0

    def enter_detail(self):
        """From list: open detail view for the selected item. Caches detail lines."""
        item = self.get_current_item()
        if not item:
            return
        cat_key = self.get_categories()[self._category_index][0]
        self._detail_lines = self._build_detail_lines(item, cat_key)
        self._detail_scroll_line = 0
        self._view_mode = VIEW_MODE_DETAIL

    def back_from_list(self):
        """From list: return to category picker."""
        self._view_mode = VIEW_MODE_CATEGORY

    def back_from_detail(self):
        """From detail: return to item list."""
        self._view_mode = VIEW_MODE_LIST
        self._detail_lines = []

    def get_detail_scroll_line(self):
        return self._detail_scroll_line

    def get_detail_lines(self):
        return self._detail_lines

    def get_detail_line_count(self):
        return len(self._detail_lines)

    def navigate_detail_next(self):
        """Scroll detail view down one line."""
        self._detail_scroll_line = min(
            self._detail_scroll_line + 1,
            max(0, len(self._detail_lines) - 1)
        )

    def navigate_detail_prev(self):
        """Scroll detail view up one line."""
        self._detail_scroll_line = max(0, self._detail_scroll_line - 1)

    def _build_detail_lines(self, item, category):
        """Display full record: every key with value shown (null, false, true, or formatted). No hiding."""
        lines = []
        if not item:
            return lines
        name = item.get("name")
        lines.append(f"=== {name if name is not None else '—'} ===")
        lines.append("")
        # Stable order: uid first after title, then rest alphabetically
        keys = sorted(k for k in item.keys() if k != "name")
        if "uid" in keys:
            keys.remove("uid")
            keys.insert(0, "uid")
        for key in keys:
            v = item[key]
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {self._format_detail_value(v)}")
        return lines if lines else ["(No details)"]

    def _format_detail_value(self, v):
        """Format any value for detail line: null, false, true, dict, list, or string/number."""
        if v is None:
            return "null"
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, dict):
            name = v.get("name")
            uid = v.get("uid")
            if name is not None or uid is not None:
                if name is not None and uid is not None:
                    return f"{name} ({uid})"
                return str(name if name is not None else uid)
            parts = [f"{k}: {self._format_detail_value(val)}" for k, val in sorted(v.items())]
            return "{" + ", ".join(parts[:4]) + ("..." if len(parts) > 4 else "") + "}"
        if isinstance(v, list):
            if not v:
                return "[]"
            head = [self._format_detail_value(v[0])]
            if len(v) > 1:
                head.append("..." if len(v) > 2 else self._format_detail_value(v[1]))
            return "[" + ", ".join(head) + "]" + (f" ({len(v)} items)" if len(v) > 2 else "")
        return str(v)

    def format_item_summary(self, item, category):
        """Build a short summary string for one item for display."""
        if not item:
            return ""
        name = item.get("name") or "—"
        if category == "characters":
            gender = item.get("gender")
            yob = item.get("yearOfBirth")
            parts = [name]
            if gender:
                parts.append(f"Gender: {gender}")
            if yob is not None:
                parts.append(f"Born: {yob}")
            return " | ".join(parts)
        if category == "spacecraft":
            reg = item.get("registry") or ""
            status = item.get("status") or ""
            cls = (item.get("spacecraftClass") or {}) if isinstance(item.get("spacecraftClass"), dict) else {}
            class_name = cls.get("name", "") if cls else ""
            parts = [name]
            if reg:
                parts.append(reg)
            if class_name:
                parts.append(class_name)
            if status:
                parts.append(status)
            return " | ".join(parts)
        if category == "species":
            return name
        if category == "technology":
            return name
        if category == "astronomicalObjects":
            return name
        return name
