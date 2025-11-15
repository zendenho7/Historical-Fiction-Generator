
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from character_manager import CharacterManager
from causal_chain import CausalEventChain


class SessionManager:
    """Manages persistent sessions with character rosters and event chains"""
    
    def __init__(self, session_id: Optional[str] = None, theme: str = "", custom_input: str = ""):
        if session_id:
            self.session_id = session_id
        elif theme:  # Generate story-based ID if theme provided
            self.session_id = self.generate_story_based_id(theme, custom_input)
        else:  # Fallback to timestamp-based ID
            self.session_id = self._generate_session_id()

        self.character_manager = CharacterManager()
        self.event_chain = CausalEventChain()
        self.metadata = {
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'theme': '',
            'generation_count': 0,
            'persona_settings': {}
        }
        self.sessions_dir = Path('sessions')
        self.sessions_dir.mkdir(exist_ok=True)

    def generate_story_based_id(self, theme: str = "", custom_input: str = "") -> str:
        """
        Generate human-readable session ID based on story content
        Format: "FantasyKingdom_DragonRiders_Nov15_2340"
        """
        import re
        from datetime import datetime
        
        # Clean theme for use in filename
        theme_clean = re.sub(r'[^\w\s-]', '', theme)
        theme_clean = re.sub(r'[-\s]+', '', theme_clean)  # Remove spaces and hyphens
        
        # Extract keywords from custom input (first 2-3 significant words)
        keywords = []
        if custom_input:
            # Remove common words
            stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
                        'by', 'from', 'about', 'and', 'or', 'but', 'is', 'was', 'were'}
            
            words = re.findall(r'\b[A-Z][a-z]+\b|\b[a-z]{4,}\b', custom_input)
            keywords = [w for w in words if w.lower() not in stop_words][:2]
        
        # Build ID components
        theme_part = theme_clean[:20] if theme_clean else "Story"
        
        if keywords:
            keyword_part = ''.join([k.capitalize() for k in keywords])[:15]
            base_name = f"{theme_part}_{keyword_part}"
        else:
            base_name = theme_part
        
        # Add timestamp (short format)
        timestamp = datetime.now().strftime("%b%d_%H%M")
        
        # Combine
        session_id = f"{base_name}_{timestamp}"
        
        # Ensure valid filename (remove any remaining special chars)
        session_id = re.sub(r'[^\w\-]', '', session_id)
        
        return session_id

    def set_story_context(self, theme: str, custom_input: str = ""):
        """
        Update session ID based on story content (call after first generation)
        """
        if not self.metadata.get('theme') or self.metadata.get('generation_count', 0) == 0:
            # Update session ID with story-based name
            new_id = self.generate_story_based_id(theme, custom_input)
            
            # Rename session file if it already exists
            old_filepath = self.sessions_dir / f"{self.session_id}.json"
            if old_filepath.exists():
                old_filepath.unlink()  # Delete old file
            
            self.session_id = new_id
            self.metadata['theme'] = theme
            self.metadata['custom_input'] = custom_input

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def update_metadata(self, theme: str = None, persona_settings: dict = None):
        """Update session metadata"""
        self.metadata['last_modified'] = datetime.now().isoformat()
        
        if theme:
            self.metadata['theme'] = theme
        
        if persona_settings:
            self.metadata['persona_settings'] = persona_settings
    
    def increment_generation_count(self):
        """Increment generation counter"""
        self.metadata['generation_count'] += 1
        self.metadata['last_modified'] = datetime.now().isoformat()
    
    def get_session_summary(self) -> str:
        """Get human-readable session summary"""
        summary = f"""
SESSION: {self.session_id}
Theme: {self.metadata.get('theme', 'Not set')}
Created: {self.metadata.get('created_at', 'Unknown')}
Last Modified: {self.metadata.get('last_modified', 'Unknown')}
Generations: {self.metadata.get('generation_count', 0)}

Characters: {len(self.character_manager.roster)} total
  - Active: {len(self.character_manager.get_active_characters())}
  - Deceased: {len(self.character_manager.get_deceased_characters())}

Events: {len(self.event_chain.events)}
Open Threads: {len(self.event_chain.open_threads)}
"""
        return summary.strip()
    
    def to_dict(self) -> dict:
        """Convert entire session to dictionary"""
        return {
            'session_id': self.session_id,
            'metadata': self.metadata,
            'character_manager': self.character_manager.to_dict(),
            'event_chain': self.event_chain.to_dict()
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Create SessionManager from dictionary"""
        session = SessionManager(session_id=data.get('session_id'))
        session.metadata = data.get('metadata', {})
        
        # Restore character manager
        char_data = data.get('character_manager', {})
        session.character_manager = CharacterManager.from_dict(char_data)
        
        # Restore event chain
        event_data = data.get('event_chain', {})
        session.event_chain = CausalEventChain.from_dict(event_data)
        
        return session
    
    def save(self, custom_name: Optional[str] = None) -> str:
        """
        Save session to JSON file
        Returns: filepath of saved session
        """
        if custom_name:
            filename = f"{custom_name}.json"
        else:
            filename = f"{self.session_id}.json"
        
        filepath = self.sessions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return str(filepath)
    
    @staticmethod
    def load(session_id: str) -> 'SessionManager':
        """Load session from file"""
        sessions_dir = Path('sessions')
        
        # Try with .json extension
        filepath = sessions_dir / f"{session_id}.json"
        if not filepath.exists():
            # Try without extension
            filepath = sessions_dir / session_id
        
        if not filepath.exists():
            raise FileNotFoundError(f"Session file not found: {session_id}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return SessionManager.from_dict(data)
    
    @staticmethod
    def list_available_sessions() -> List[Dict[str, str]]:
        """
        List all available session files
        Returns: List of dicts with session info
        """
        sessions_dir = Path('sessions')
        if not sessions_dir.exists():
            return []
        
        sessions = []
        for filepath in sessions_dir.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                sessions.append({
                    'session_id': data.get('session_id', filepath.stem),
                    'filename': filepath.name,
                    'theme': data.get('metadata', {}).get('theme', 'Unknown'),
                    'created': data.get('metadata', {}).get('created_at', 'Unknown'),
                    'last_modified': data.get('metadata', {}).get('last_modified', 'Unknown'),
                    'generations': data.get('metadata', {}).get('generation_count', 0),
                    'events': len(data.get('event_chain', {}).get('events', [])),
                    'characters': len(data.get('character_manager', {}).get('roster', {}))
                })
            except Exception as e:
                # Skip corrupted files
                continue
        
        # Sort by last modified (most recent first)
        sessions.sort(key=lambda x: x['last_modified'], reverse=True)
        
        return sessions
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete a session file"""
        sessions_dir = Path('sessions')
        filepath = sessions_dir / f"{session_id}.json"
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False
    
    def export_readable_summary(self, output_path: str):
        """Export human-readable summary of session"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"SESSION SUMMARY: {self.session_id}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(self.get_session_summary())
            f.write("\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("CHARACTER ROSTER\n")
            f.write("=" * 60 + "\n\n")
            f.write(self.character_manager.get_roster_summary())
            f.write("\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("EVENT CHAIN\n")
            f.write("=" * 60 + "\n\n")
            f.write(self.event_chain.get_chain_summary())

