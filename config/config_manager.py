import json
import os
from typing import Dict, Any

class ConfigManager:
    """Handles saving and loading application configuration"""
    
    def __init__(self, config_file: str = "file_organizer_config.json"):
        self.config_file = config_file
        self.default_file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"],
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt", ".xlsx", ".xls", ".ods",
                  ".pptx", ".ppt", ".csv", ".md"],
        "Videos": [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm", ".flv", ".mpeg"],
        "Audio": [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma", ".aiff"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
        "Code": [".py", ".js", ".ts", ".html", ".css", ".scss", ".java", ".cpp", ".c", ".cs",
             ".json", ".xml", ".php", ".sh", ".bat", ".go", ".rb", ".swift"],
        "Executables": [".exe", ".msi", ".apk", ".appimage", ".dmg", ".deb", ".rpm"],
        "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "Design": [".psd", ".ai", ".xd", ".sketch", ".fig"],
        "Ebooks": [".epub", ".mobi", ".azw", ".djvu"]
    }

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file and sync file_types with updated defaults"""
        default_config = {
        'organize_by_date': False,
        'move_files': True,
        'create_folders': True,
        'skip_hidden': True,
        'custom_tags': '',
        'last_folder': '',
        'file_types': self.default_file_types.copy(),
        'manual_assignments': {}
        }
    
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

            # Merge root-level config values
                default_config.update(config)

            # ⚠ Merge file_types with updated defaults
                file_types_from_file = config.get('file_types', {})
                synced_file_types = self.default_file_types.copy()

            # Keep user-modified categories and also add new default ones
                for category, extensions in file_types_from_file.items():
                    synced_file_types[category] = list(set(extensions))

                default_config['file_types'] = synced_file_types

        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
    
        return default_config
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_default_file_types(self) -> Dict[str, list]:
        """Get default file type categories"""
        return self.default_file_types.copy()