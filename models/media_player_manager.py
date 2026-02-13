# --- models/media_player_manager.py ---
# Media player: audio and video (MP4) via VLC embedded in the Tricorder window.
# Same pattern as 3D schematics: one window, VLC draws into it (set_hwnd/set_xwindow).

import os
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


class MediaPlayerManager:
    """
    Manages media playback using VLC embedded in the Tricorder window.
    Supports audio (.mp3, .wav, .ogg) and video (.mp4). Same window as the app (like 3D schematics).
    """

    def __init__(self, config):
        self.config = config
        self.media_folder = getattr(config, "MEDIA_FOLDER", "assets/media")
        self.extensions = tuple(
            getattr(config, "MEDIA_EXTENSIONS", (".mp3", ".wav", ".ogg", ".mp4"))
        )
        self.track_list = []  # List of (display_name, full_path)
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
        self._lock = threading.Lock()
        self._vlc_init_failed = False  # Avoid repeated failed inits
        self.vlc_available = _VLC_AVAILABLE
        if not self.vlc_available:
            logger.info("Media player: VLC not available; install python-vlc and VLC application.")
        else:
            self._ensure_vlc_instance()
        self._refresh_track_list()

    def _ensure_vlc_instance(self):
        """Create VLC instance and player if possible. Safe to call multiple times."""
        if not _VLC_AVAILABLE or self._vlc_instance is not None or self._vlc_init_failed:
            return
        try:
            self._vlc_instance = vlc.Instance("--no-video-title-show")
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

    def _refresh_track_list(self):
        """Scan media folder for supported audio and video files."""
        self.track_list = []
        if not os.path.isdir(self.media_folder):
            logger.warning("Media folder not found: %s", self.media_folder)
            return
        try:
            for name in sorted(os.listdir(self.media_folder)):
                _, ext = os.path.splitext(name)
                if ext.lower() in self.extensions:
                    path = os.path.join(self.media_folder, name)
                    if os.path.isfile(path):
                        self.track_list.append((name, path))
            logger.info(
                "Media player: scanned %s, found %d file(s) (extensions: %s)",
                self.media_folder, len(self.track_list), ", ".join(self.extensions),
            )
        except OSError as e:
            logger.error("Media player: could not scan folder %s: %s", self.media_folder, e)

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
                self._player.set_pause(0)
                self.paused = False
                self.playing = True
                logger.info("Media player: resumed %s", self.get_current_track_name())
                return True

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
        """Pause playback. VLC stays attached and shows paused frame."""
        if not self.playing or not self._player:
            return
        try:
            self._player.set_pause(1)
            self.playing = False
            self.paused = True
            logger.info("Media player: paused %s", self.get_current_track_name())
        except Exception as e:
            logger.warning("Media player: pause failed: %s", e)

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.playing:
            self.pause()
        else:
            self.play()

    def stop(self):
        """Stop playback and release current media. Detach VLC so track list is visible."""
        try:
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
        """Move selection to next track in list (no play). For scrolling the list."""
        if not self.track_list:
            return False
        self.current_index = (self.current_index + 1) % len(self.track_list)
        return True

    def navigate_prev(self):
        """Move selection to previous track in list (no play). For scrolling the list."""
        if not self.track_list:
            return False
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

    def on_enter_view(self):
        """Called when entering media player view. Refresh list and reset index if needed."""
        self._refresh_track_list()
        if self.current_index >= len(self.track_list) and self.track_list:
            self.current_index = 0
        self.stop()

    def on_exit_view(self):
        """Called when leaving media player view. Stop playback and release."""
        logger.info("Media player: exiting view, stopping playback.")
        self.stop()
