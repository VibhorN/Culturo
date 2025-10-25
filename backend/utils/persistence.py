"""
Simple file-based persistence for agent data
Perfect for localhost testing without database setup
"""

import json
import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FilePersistence:
    """Simple file-based data persistence for testing"""
    
    def __init__(self, data_dir: str = "agent_data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def save_user_data(self, agent_name: str, user_id: str, data: Dict[str, Any]):
        """Save user data to file"""
        try:
            filename = f"{agent_name}_{user_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            # Add metadata
            data_with_meta = {
                "data": data,
                "last_updated": datetime.now().isoformat(),
                "agent_name": agent_name,
                "user_id": user_id
            }
            
            with open(filepath, 'w') as f:
                json.dump(data_with_meta, f, indent=2)
            
            logger.info(f"Saved {agent_name} data for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")
    
    def load_user_data(self, agent_name: str, user_id: str) -> Dict[str, Any]:
        """Load user data from file"""
        try:
            filename = f"{agent_name}_{user_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                logger.info(f"No data file found for {agent_name} user {user_id}")
                return {}
            
            with open(filepath, 'r') as f:
                data_with_meta = json.load(f)
            
            logger.info(f"Loaded {agent_name} data for user {user_id}")
            return data_with_meta.get("data", {})
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return {}
    
    def get_all_users(self, agent_name: str) -> list:
        """Get list of all users for an agent"""
        try:
            users = []
            for filename in os.listdir(self.data_dir):
                if filename.startswith(f"{agent_name}_") and filename.endswith(".json"):
                    user_id = filename.replace(f"{agent_name}_", "").replace(".json", "")
                    users.append(user_id)
            return users
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return []
    
    def delete_user_data(self, agent_name: str, user_id: str):
        """Delete user data file"""
        try:
            filename = f"{agent_name}_{user_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted {agent_name} data for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error deleting data: {str(e)}")
    
    def get_data_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        try:
            stats = {
                "total_files": 0,
                "agents": {},
                "total_users": 0
            }
            
            for filename in os.listdir(self.data_dir):
                if filename.endswith(".json"):
                    stats["total_files"] += 1
                    
                    # Extract agent name
                    parts = filename.split("_")
                    if len(parts) >= 2:
                        agent_name = parts[0]
                        if agent_name not in stats["agents"]:
                            stats["agents"][agent_name] = 0
                        stats["agents"][agent_name] += 1
            
            stats["total_users"] = len(set([f.split("_")[1].replace(".json", "") for f in os.listdir(self.data_dir) if f.endswith(".json")]))
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}


# Global persistence instance
persistence = FilePersistence()
