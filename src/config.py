from omegaconf import OmegaConf  
from pathlib import Path  
import shutil  
  
def get_config(config_path, default_config_path=None):  
    config_path = Path(config_path)  
    if not config_path.exists():  
        if default_config_path is None:  
            default_config_path = Path(__file__).parent / "default_config.yaml"  
        if not default_config_path.exists():  
            raise FileNotFoundError(f"Default config file not found: {default_config_path}")  
  
        config_path.parent.mkdir(parents=True, exist_ok=True)  
        shutil.copy(default_config_path, config_path)  
      
    cfg = OmegaConf.load(config_path)  
  
    return cfg  
