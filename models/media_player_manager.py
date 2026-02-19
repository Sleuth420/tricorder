# --- models/media_player_manager.py ---
# Media player: audio and video (MP4) via VLC embedded in the Tricorder window.
# Same pattern as 3D schematics: one window, VLC draws into it (set_hwnd/set_xwindow).

import os
import re
import sys
import time
import logging
import threading

logger = logging.getLogger(__name__)

# Optional VLC binding; playback only works if VLC (and python-vlc) are available
try:
    import vlc
    _VLC_AVAILABLE = True
except ImportError:
    vlc = None
    _VLC_AVAILABLE = False
    logger.warning("python-vlc not installed. Media player will show 'VLC not available'. Install: pip install python-vlc (and install VLC app).")

# Optional mutagen for MP4 (and MP3) metadata; display name falls back to filename if unavailable
try:
    from mutagen.mp4 import MP4 as MutagenMP4
    _MUTAGEN_AVAILABLE = True
except ImportError:
    MutagenMP4 = None
    _MUTAGEN_AVAILABLE = False


class MediaPlayerManager:
    """
    Manages media playback using VLC embedded in the Tricorder window.
    Supports audio (.mp3, .wav, .ogg) and video (.mp4). Same window as the app (like 3D schematics).
    """

    def __init__(self, config):
        self.config = config
        self._project_root = self._get_project_root()
        self.media_folder = self._resolve_media_path(getattr(config, "MEDIA_FOLDER", "assets/media"))
        self.extensions = tuple(
            getattr(config, "MEDIA_EXTENSIONS", (".mp3", ".wav", ".ogg", ".mp4"))
        )
        self.track_list = []  # List of (display_name, full_path) — episodes in current season (or flat list if no seasons)
        self.current_index = 0
        self._playing_index = -1  # Index of track currently loaded in VLC (playing or paused); -1 when none
        self.playing = False
        self.paused = False
        self._end_reached = False  # Set by VLC callback (may be from another thread)
        self._vlc_instance = None
        self._player = None
        self._current_media = None
        self._window_handle = None  # HWND (Windows) or X11 window ID (Linux) for embedding
        self._is_attached = False  # True when VLC is currently drawing into our window (avoid per-frame set_xwindow on Linux)
        self.show_file_info_until = 0.0  # Time until which to show file info overlay (long-press D)
        self._volume_before_mute = None  # Restore volume when unmuting (VLC 0-100)
        self._lock = threading.Lock()
        self._vlc_init_failed = False  # Avoid repeated failed inits
        self.vlc_available = _VLC_AVAILABLE
        # Season structure: subdirs of media_folder (e.g. 1, 2, 3 for Star Trek). None = browsing seasons; path = browsing episodes in that folder.
        self._season_folders = []  # List of (display_name, folder_path), e.g. ("Season 1", "assets/media/1")
        self._current_season_folder = None  # None = show season list; else path to season folder
        if not self.vlc_available:
            logger.info("Media player: VLC not available; install python-vlc and VLC application.")
        else:
            self._ensure_vlc_instance()
        self._scan_season_folders()
        self._refresh_track_list()

    def _get_project_root(self):
        """Project root (directory containing config/). Used to resolve relative media paths."""
        try:
            config_file = getattr(self.config, "__file__", None)
            if config_file:
                return os.path.dirname(os.path.dirname(os.path.abspath(config_file)))
        except Exception:
            pass
        return os.getcwd()

    def _resolve_media_path(self, path):
        """Resolve path relative to project root so media/Logs/Captain works regardless of cwd."""
        if not path or os.path.isabs(path):
            return path or ""
        return os.path.normpath(os.path.join(self._project_root, path))

    def set_media_source(self, media_source):
        """
        Switch to a Logs source folder (tv_show, movies, captains_logs).
        Uses config.MEDIA_SOURCE_FOLDERS; falls back to MEDIA_FOLDER if source unknown.
        """
        folders = getattr(self.config, "MEDIA_SOURCE_FOLDERS", None)
        if folders and media_source and media_source in folders:
            self.media_folder = self._resolve_media_path(folders[media_source])
            logger.info("Media player: source=%s, folder=%s", media_source, self.media_folder)
        else:
            self.media_folder = self._resolve_media_path(
                getattr(self.config, "MEDIA_FOLDER", "assets/media"))
        self._current_season_folder = None
        self._scan_season_folders()
        self._refresh_track_list()
        self.current_index = 0

    def _ensure_vlc_instance(self):
        """Create VLC instance and player if possible. Safe to call multiple times."""
        if not _VLC_AVAILABLE or self._vlc_instance is not None or self._vlc_init_failed:
            return
        try:
            # Base options: no on-screen title; enable marquee filter for pause overlay
            vlc_args = ["--no-video-title-show", "--sub-filter=marq"]
            # On Linux (e.g. Raspberry Pi), avoid flicker: disable hw decode if it fights X11 embedding
            if sys.platform != "win32":
                vlc_args.append("--avcodec-hw=none")
            self._vlc_instance = vlc.Instance(" ".join(vlc_args))
            self._player = self._vlc_instance.media_player_new()
            # Window handle is set when we have it (from display); VLC will draw into our window
            events = self._player.event_manager()
            events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end_reached)
            logger.info("Media player: VLC instance and player created successfully.")
        except Exception as e:
            logger.error("Media player: failed to create VLC instance: %s", e, exc_info=True)
            self.vlc_available = False
            self._vlc_init_failed = True
            self._vlc_instance = None
            self._player = None

    def _on_end_reached(self, event):
        """Called by VLC when playback ends (may run on VLC's thread)."""
        with self._lock:
            self._end_reached = True

    def _format_time_for_marquee(self, sec):
        """Format seconds as M:SS for marquee text."""
        if sec is None or sec < 0:
            return "0:00"
        m = int(sec // 60)
        s = int(sec % 60)
        return f"{m}:{s:02d}"

    def _build_pause_marquee_text(self):
        """Build track/media info string for VLC marquee when paused (single line)."""
        name = self.get_current_track_name() or "—"
        if len(name) > 35:
            name = name[:32] + "..."
        pos = self.get_position_sec()
        length = self.get_length_sec()
        pos_str = self._format_time_for_marquee(pos)
        len_str = self._format_time_for_marquee(length) if length > 0 else "—"
        size_b = self.get_current_file_size()
        if size_b is not None:
            if size_b < 1024 * 1024:
                size_str = f"{size_b / 1024:.1f} KB"
            else:
                size_str = f"{size_b / (1024 * 1024):.2f} MB"
        else:
            size_str = "—"
        return f"  PAUSED  —  {name}  —  {pos_str} / {len_str}  —  {size_str}"

    def _set_pause_marquee(self, show):
        """Show or hide the pause overlay using VLC marquee (drawn by VLC on top of video)."""
        if not self._player or not _VLC_AVAILABLE:
            return
        try:
            # LibVLC marquee: Enable=0, Text=1, Position=4, Timeout=7, Size=6
            opt = getattr(vlc, "VideoMarqueeOption", None)
            if opt is None:
                return
            enable_val = 1 if show else 0
            self._player.video_set_marquee_int(opt.Enable, enable_val)
            if show:
                text = self._build_pause_marquee_text()
                self._player.video_set_marquee_string(opt.Text, text)
                self._player.video_set_marquee_int(opt.Position, 0)   # 0=center
                self._player.video_set_marquee_int(opt.Timeout, 0)    # 0=forever
                self._player.video_set_marquee_int(opt.Size, 24)
        except (AttributeError, Exception) as e:
            logger.debug("Media player: marquee not available (%s)", e)

    def tick(self):
        """
        Call once per frame from the main thread when in media player view.
        Processes end-reached flag and optionally auto-advances to next track.
        """
        with self._lock:
            if not self._end_reached:
                return
            if not self.playing:
                self._end_reached = False
                return
            self._end_reached = False
        self.playing = False
        self.paused = False
        # Auto-advance to next track
        if self.track_list:
            self.current_index = (self.current_index + 1) % len(self.track_list)
            logger.info("Media player: advancing to next track: %s", self.get_current_track_name())
            self.play()

    @staticmethod
    def _format_episode_display_name(raw):
        """
        Convert metadata/filename to 's01e06 - Episode Title' when it contains SxxExx.
        Example: "Star Trek TOS S01E06 Mudd's Women" -> "s01e06 - Mudd's Women".
        If no SxxExx pattern is found, return the string trimmed.
        """
        if not raw or not isinstance(raw, str):
            return raw or ""
        raw = raw.strip()
        # Match S01E06 (case insensitive) and everything after as episode title
        m = re.search(r"(s\d+e\d+)\s*(.*)", raw, re.IGNORECASE)
        if m:
            code = m.group(1).lower()
            title = m.group(2).strip()
            if title:
                return f"{code} - {title}"
            return code
        return raw

    def _get_display_name_for_path(self, path):
        """
        Use MP4 metadata (Comment, then Title) or filename, then format as 's01e06 - Episode Title'.
        """
        base = os.path.basename(path)
        name_no_ext = os.path.splitext(base)[0]
        raw = name_no_ext
        if _MUTAGEN_AVAILABLE and os.path.splitext(path)[1].lower() == ".mp4":
            try:
                mp4 = MutagenMP4(path)
                # Comment (©cmt) = Details > Comments; Title (©nam) = Details tab title
                for key in ("\xa9cmt", "\xa9nam"):
                    val = mp4.get(key, [])
                    if val and val[0]:
                        raw = str(val[0]).strip()
                        break
            except Exception as e:
                logger.debug("Could not read MP4 metadata for %s: %s", path, e)
        return self._format_episode_display_name(raw)

    @staticmethod
    def _is_temporary_media_file(name):
        """Return True if the filename looks like a temporary/helper file (e.g. macOS ._* resource forks)."""
        base = os.path.basename(name)
        if base.startswith("._"):
            return True
        if base.startswith(".") and len(base) > 1:
            return True
        return False

    @staticmethod
    def _season_episode_sort_key(path):
        """
        Return (season, episode) for sorting when path/filename contains SxxEyy (e.g. S01E06).
        Falls back to (0, 0) so files without a match sort first, then by natural filename order.
        """
        base = os.path.basename(path)
        name_no_ext = os.path.splitext(base)[0]
        m = re.search(r"s(\d+)e(\d+)", name_no_ext, re.IGNORECASE)
        if m:
            return (int(m.group(1)), int(m.group(2)))
        return (0, 0)

    @staticmethod
    def _natural_sort_key(path):
        """
        Sort key that splits the filename on digit groups so 'Episode 2' comes before 'Episode 10'.
        Used as tie-breaker when SxxEyy is absent or equal.
        Each part is (0, n) for numbers or (1, s) for strings so we never compare str to int.
        """
        base = os.path.basename(path).lower()
        parts = re.split(r"(\d+)", base)
        return tuple(
            (0, int(p)) if p.isdigit() else (1, p)
            for p in parts if p
        )

    @staticmethod
    def _season_folder_sort_key(name):
        """Sort key for season folder names: numeric order when possible (1, 2, 10), else alphabetical."""
        try:
            return (0, int(name))
        except ValueError:
            return (1, name)

    def _scan_season_folders(self):
        """Populate _season_folders with subdirs of media_folder that contain at least one media file. Sorted numerically (1, 2, 3, ... 10)."""
        self._season_folders = []
        if not os.path.isdir(self.media_folder):
            return
        try:
            for name in sorted(os.listdir(self.media_folder), key=self._season_folder_sort_key):
                folder_path = os.path.join(self.media_folder, name)
                if not os.path.isdir(folder_path):
                    continue
                has_media = False
                for f in os.listdir(folder_path):
                    if self._is_temporary_media_file(f):
                        continue
                    _, ext = os.path.splitext(f)
                    if ext.lower() in self.extensions and os.path.isfile(os.path.join(folder_path, f)):
                        has_media = True
                        break
                if has_media:
                    display_name = "Secret" if name.lower() == "secret" else f"Season {name}"
                    self._season_folders.append((display_name, folder_path))
            if self._season_folders:
                logger.info("Media player: found %d season folder(s): %s", len(self._season_folders), [t[0] for t in self._season_folders])
        except OSError as e:
            logger.error("Media player: could not scan media folder %s: %s", self.media_folder, e)

    def get_season_folders(self):
        """Return list of (display_name, folder_path) for season selection. Empty if no subdirs with media."""
        return list(self._season_folders)

    def is_browsing_seasons(self):
        """True when we have season folders and no season is selected (show season list)."""
        return bool(self._season_folders) and self._current_season_folder is None

    def get_selected_season_folder(self):
        """When browsing seasons, return the folder path for the currently selected season index, else None."""
        if not self.is_browsing_seasons() or not self._season_folders:
            return None
        idx = self.current_index % len(self._season_folders)
        return self._season_folders[idx][1]

    def set_season(self, folder_path):
        """Set current season folder and refresh episode list. Episodes are ordered by filename; display name from MP4 comment."""
        if not folder_path or not os.path.isdir(folder_path):
            return False
        self._current_season_folder = folder_path
        self._refresh_track_list()
        self.current_index = 0
        return True

    def clear_season(self):
        """Return to season list (when we have season folders). Clears episode list selection context."""
        self._current_season_folder = None
        self._refresh_track_list()
        self.current_index = 0

    def _refresh_track_list(self):
        """Scan current folder for media: if a season is selected, scan that folder (episodes sorted by filename); else flat scan of media_folder or empty if browsing seasons."""
        self.track_list = []
        scan_folder = self._current_season_folder if self._current_season_folder else self.media_folder
        if self.is_browsing_seasons():
            # Show season list only; no tracks
            return
        if not scan_folder or not os.path.isdir(scan_folder):
            if not self._current_season_folder:
                logger.warning("Media folder not found: %s", self.media_folder)
            return
        try:
            candidates = []
            for name in os.listdir(scan_folder):
                if self._is_temporary_media_file(name):
                    continue
                _, ext = os.path.splitext(name)
                if ext.lower() in self.extensions:
                    path = os.path.join(scan_folder, name)
                    if os.path.isfile(path):
                        display_name = self._get_display_name_for_path(path)
                        candidates.append((display_name, path))
            # Sort by season/episode (SxxEyy), then by natural filename (so Episode 2 < Episode 10), then path
            self.track_list = sorted(
                candidates,
                key=lambda item: (
                    self._season_episode_sort_key(item[1]),
                    self._natural_sort_key(item[1]),
                    item[1],
                ),
            )
            logger.info(
                "Media player: scanned %s, found %d file(s) (extensions: %s)",
                scan_folder, len(self.track_list), ", ".join(self.extensions),
            )
        except OSError as e:
            logger.error("Media player: could not scan folder %s: %s", scan_folder, e)

    def get_track_list(self):
        """Return list of (display_name, path) for UI."""
        return list(self.track_list)

    def get_current_index(self):
        return self.current_index

    def get_playing_index(self):
        """Index of the track currently loaded in VLC (playing or paused). Returns -1 when nothing loaded."""
        return self._playing_index

    def get_current_track_name(self):
        if not self.track_list or self.current_index < 0 or self.current_index >= len(self.track_list):
            return None
        return self.track_list[self.current_index][0]

    def get_current_track_path(self):
        if not self.track_list or self.current_index < 0 or self.current_index >= len(self.track_list):
            return None
        return self.track_list[self.current_index][1]

    def set_window_handle(self, handle):
        """Set the window handle so VLC draws into the Tricorder window (like 3D schematics)."""
        if handle is not None and handle != self._window_handle:
            self._window_handle = handle
            self._is_attached = False  # Force re-attach with new handle on next update
            logger.debug("Media player: window handle set for embedding.")

    def _apply_window_handle(self):
        """Tell VLC to use our window for video output. Call when playing so video is embedded."""
        if not self._player or self._window_handle is None:
            return
        try:
            if sys.platform == "win32":
                self._player.set_hwnd(self._window_handle)
            else:
                self._player.set_xwindow(self._window_handle)
            self._player.video_set_mouse_input(False)
            self._player.video_set_key_input(False)
        except Exception as e:
            logger.warning("Media player: could not set window handle: %s", e)

    def detach_from_window(self):
        """Detach VLC from our window so the track list is visible."""
        if not self._player or not self._is_attached:
            return
        try:
            if sys.platform == "win32":
                self._player.set_hwnd(0)
            else:
                self._player.set_xwindow(0)
            self._is_attached = False
        except Exception as e:
            logger.warning("Media player: could not detach from window: %s", e)

    def attach_to_window(self):
        """Re-attach VLC to our window (e.g. when resuming from pause)."""
        if self._is_attached:
            return
        self._apply_window_handle()
        self._is_attached = True

    def update_window_attachment(self, show_video):
        """
        Attach or detach VLC from the window only when the desired state changes.
        Calling set_xwindow/set_hwnd every frame on Linux causes flicker; only transition when needed.
        """
        if show_video and not self._is_attached:
            self.attach_to_window()
        elif not show_video and self._is_attached:
            self.detach_from_window()

    def is_playing(self):
        return self.playing

    def is_paused(self):
        return self.paused

    def play(self):
        """Start or resume playback in VLC (embedded in Tricorder window)."""
        if not self.track_list:
            return False
        if not self.vlc_available:
            logger.warning("Media player: play ignored, VLC not available.")
            return False
        path = self.get_current_track_path()
        if not path:
            return False
        self._ensure_vlc_instance()
        if not self._player:
            return False
        try:
            if self.paused:
                self._set_pause_marquee(False)
                self._player.set_pause(0)
                self.paused = False
                self.playing = True
                logger.info("Media player: resumed %s", self.get_current_track_name())
                return True

            self._set_pause_marquee(False)
            self._apply_window_handle()
            self._current_media = self._vlc_instance.media_new_path(os.path.abspath(path))
            self._player.set_media(self._current_media)
            self._player.play()
            self.playing = True
            self.paused = False
            self._playing_index = self.current_index
            logger.info("Media player: playing %s", self.get_current_track_name())
            return True
        except Exception as e:
            logger.error("Media player: play failed for %s: %s", path, e, exc_info=True)
            return False

    def pause(self):
        """Pause playback. VLC stays attached; marquee shows 'Paused' and track info on video."""
        if not self.playing or not self._player:
            return
        try:
            self._player.set_pause(1)
            self.playing = False
            self.paused = True
            self._set_pause_marquee(True)
            logger.info("Media player: paused %s", self.get_current_track_name())
        except Exception as e:
            logger.warning("Media player: pause failed: %s", e)

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.playing:
            self.pause()
        else:
            self.play()

    def get_volume(self):
        """Current VLC volume 0-100. Returns 0 if unavailable."""
        if not self._player:
            return 0
        try:
            v = self._player.audio_get_volume()
            return max(0, v) if v >= 0 else 0
        except Exception:
            return 0

    def set_volume(self, level):
        """Set VLC volume (0-100)."""
        if not self._player:
            return
        try:
            level = max(0, min(100, int(level)))
            self._player.audio_set_volume(level)
            if level > 0:
                self._volume_before_mute = None
        except Exception as e:
            logger.debug("Media player: set_volume failed: %s", e)

    def volume_up(self):
        """Increase VLC volume by 10, cap at 100."""
        v = self.get_volume()
        self.set_volume(min(100, v + 10))
        logger.debug("Media player: volume up -> %d", self.get_volume())

    def volume_down(self):
        """Decrease VLC volume by 10, floor at 0."""
        v = self.get_volume()
        self.set_volume(max(0, v - 10))
        logger.debug("Media player: volume down -> %d", self.get_volume())

    def toggle_mute(self):
        """Toggle mute: if current volume is 0, restore previous; else save and set 0."""
        if not self._player:
            return
        try:
            v = self._player.audio_get_volume()
            if v is None or v <= 0:
                # Unmute: restore saved level or 70
                restore = self._volume_before_mute if self._volume_before_mute is not None else 70
                self._volume_before_mute = None
                self._player.audio_set_volume(restore)
                logger.info("Media player: unmuted -> %d", restore)
            else:
                self._volume_before_mute = v
                self._player.audio_set_volume(0)
                logger.info("Media player: muted")
        except Exception as e:
            logger.debug("Media player: toggle_mute failed: %s", e)

    def stop(self):
        """Stop playback and release current media. Detach VLC so track list is visible."""
        try:
            self._set_pause_marquee(False)
            if self._player:
                self._player.stop()
            self.playing = False
            self.paused = False
            self._playing_index = -1
            self._current_media = None
            with self._lock:
                self._end_reached = False
            self.detach_from_window()  # Ensure menu is visible when stopped
            logger.info("Media player: stopped.")
        except Exception as e:
            logger.warning("Media player: stop failed: %s", e)

    def navigate_next(self):
        """Move selection to next item (season when browsing seasons, else episode). No play."""
        if self.is_browsing_seasons():
            if not self._season_folders:
                return False
            self.current_index = (self.current_index + 1) % len(self._season_folders)
            return True
        if not self.track_list:
            # Empty state: two virtual items (no-media message, Back)
            self.current_index = (self.current_index + 1) % 2
            return True
        self.current_index = (self.current_index + 1) % len(self.track_list)
        return True

    def navigate_prev(self):
        """Move selection to previous item (season when browsing seasons, else episode). No play."""
        if self.is_browsing_seasons():
            if not self._season_folders:
                return False
            self.current_index = (self.current_index - 1) % len(self._season_folders)
            return True
        if not self.track_list:
            # Empty state: two virtual items (no-media message, Back)
            self.current_index = (self.current_index - 1) % 2
            return True
        self.current_index = (self.current_index - 1) % len(self.track_list)
        return True

    def next_track(self):
        """Go to next track and play."""
        if not self.track_list:
            return False
        self.stop()
        self.current_index = (self.current_index + 1) % len(self.track_list)
        logger.info("Media player: next track -> %s", self.get_current_track_name())
        return self.play()

    def prev_track(self):
        """Go to previous track and play."""
        if not self.track_list:
            return False
        self.stop()
        self.current_index = (self.current_index - 1) % len(self.track_list)
        logger.info("Media player: prev track -> %s", self.get_current_track_name())
        return self.play()

    def select_track(self, index):
        """Select track by index (0-based). Does not auto-play."""
        if 0 <= index < len(self.track_list):
            self.stop()
            self.current_index = index
            return True
        return False

    def get_position_sec(self):
        """Current playback position in seconds. Returns 0 if not available."""
        if not self._player:
            return 0.0
        try:
            t_ms = self._player.get_time()
            return (t_ms / 1000.0) if t_ms >= 0 else 0.0
        except Exception:
            return 0.0

    def get_length_sec(self):
        """Total length of current media in seconds. Returns 0 if not available."""
        if not self._player or not self._current_media:
            return 0.0
        try:
            length_ms = self._current_media.get_duration()
            return (length_ms / 1000.0) if length_ms >= 0 else 0.0
        except Exception:
            return 0.0

    def get_current_file_size(self):
        """File size in bytes for current track, or None if not available."""
        path = self.get_current_track_path()
        if not path or not os.path.isfile(path):
            return None
        try:
            return os.path.getsize(path)
        except OSError:
            return None

    def set_show_file_info(self, duration_sec=5.0):
        """Show file info overlay for this many seconds (e.g. after long-press D)."""
        self.show_file_info_until = time.time() + duration_sec

    def is_showing_file_info(self):
        """True if file info overlay should be visible."""
        return time.time() < self.show_file_info_until

    def on_enter_view(self, media_source=None):
        """
        Called when entering media player view.
        If media_source is set (tv_show, movies, captains_logs), switch to that folder first.
        Then start at season list if using seasons; refresh episode list and reset index otherwise.
        """
        self.stop()
        if media_source is not None:
            self.set_media_source(media_source)
        else:
            self._scan_season_folders()
            self.clear_season()
        if not self.is_browsing_seasons() and self.track_list and self.current_index >= len(self.track_list):
            self.current_index = 0

    def on_exit_view(self):
        """Called when leaving media player view. Stop playback and release."""
        logger.info("Media player: exiting view, stopping playback.")
        self.stop()
