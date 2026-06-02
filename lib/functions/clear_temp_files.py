import os
import shutil
import stat
import tempfile
from lib import log, system


def clear_temp_files(target_dir: str | None = None) -> bool:
    """Clear temporary files safely.

    If `target_dir` is provided, only that directory will be emptied.
    Otherwise the platform default temp location is used.
    Returns True on success, False on error.
    """
    SKIP_SUBSTRINGS = ('.net', 'Auto Install Programs', 'jre', '_internal', 'is-CBYLUMBBLP')

    def _clear_dir(base: str) -> tuple[int, int, int]:
        """Remove contents of `base`. Returns (removed_files, removed_dirs, skipped)."""
        removed_files = 0
        removed_dirs = 0
        skipped = 0

        if not os.path.exists(base):
            log.warning(f"Target temp dir does not exist: {base}")
            return (0, 0, 0)

        for name in os.listdir(base):
            path = os.path.join(base, name)
            # Skip known protected or installer-related temp folders to avoid noisy errors
            if any(substr in name for substr in SKIP_SUBSTRINGS):
                # Keep skipped count but only warn at debug level
                log.info(f"Skipping protected temp entry: {path}")
                skipped += 1
                continue
            try:
                if os.path.islink(path) or os.path.isfile(path):
                    try:
                        os.remove(path)
                        removed_files += 1
                    except PermissionError as pe:
                        try:
                            os.chmod(path, stat.S_IWRITE)
                            os.remove(path)
                            removed_files += 1
                        except Exception as e:
                            # File locked or access denied — expected on Windows for some temp files
                            if getattr(e, 'winerror', None) in (5, 32) or getattr(pe, 'winerror', None) in (5, 32):
                                log.debug(f"Skipping in-use/protected file: {path}: {e}")
                            else:
                                log.error(f"Failed to remove {path}: {e}")
                            skipped += 1
                elif os.path.isdir(path):
                    try:
                        shutil.rmtree(path)
                        removed_dirs += 1
                    except PermissionError as pe:
                        try:
                            for root, dirs, files in os.walk(path):
                                for fname in files:
                                    fp = os.path.join(root, fname)
                                    try:
                                        os.chmod(fp, stat.S_IWRITE)
                                    except Exception:
                                        pass
                            shutil.rmtree(path)
                            removed_dirs += 1
                        except Exception as e:
                            if getattr(e, 'winerror', None) in (5, 32) or getattr(pe, 'winerror', None) in (5, 32):
                                log.debug(f"Skipping in-use/protected directory: {path}: {e}")
                            else:
                                log.error(f"Failed to remove {path}: {e}")
                            skipped += 1
            except Exception as e:
                # Could be file-in-use (Windows) or other OS error — skip and continue
                if getattr(e, 'winerror', None) in (5, 32) or getattr(e, 'errno', None) in (13, 32):
                    log.debug(f"Skipping in-use/protected path: {path}: {e}")
                else:
                    log.error(f"Failed to remove {path}: {e}")
                skipped += 1

        return (removed_files, removed_dirs, skipped)

    # Determine the base dir once and log a single entry
    if target_dir:
        base_dir = os.path.abspath(target_dir)
    else:
        if system.name() == 'Windows':
            base_dir = os.environ.get('TEMP') or tempfile.gettempdir()
        elif system.name() in ['Linux', 'Darwin']:
            base_dir = '/tmp'
        else:
            log.warning(f"Unsupported system: {system.name()}")
            return False

    log.info(f'Clearing temporary files: {base_dir}')
    try:
        removed_files, removed_dirs, skipped = _clear_dir(base_dir)
        log.info(f"Temporary files cleared. Removed files: {removed_files}, removed dirs: {removed_dirs}, skipped: {skipped}")
        return True
    except Exception as e:
        log.error(f"An error occurred while clearing temporary files: {e}")
        return False

