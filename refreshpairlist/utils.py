from typing import Optional
from pathlib import Path

def find_freqtrade() -> Optional[Path]:
    """
        Find out where freqtrade is installed
    """
    freqtrade_path = None
    try:
        import freqtrade
        # Get the path of the freqtrade module
        freqtrade_module_path = Path(freqtrade.__file__).resolve()
        # Navigate to the parent directory (root of the Freqtrade package)
        freqtrade_path = freqtrade_module_path.parent.parent
    except ImportError:
        raise ModuleNotFoundError("Freqtrade installation not found. Please install Freqtrade.")
    return freqtrade_path
