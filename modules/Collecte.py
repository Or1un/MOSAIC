#!/usr/bin/env python3
"""
Mosaic v2.0
Unified extraction system for all social platforms
Author: Or1un
"""

import sys
import os
import json
import time
import shutil
import glob
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

# ============================================================================
# UI SYSTEM - Terminal Interface
# ============================================================================

class Theme:
    """ANSI color codes for elegant terminal UI"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Colors
    PRIMARY = "\033[38;5;75m"      # Blue
    SUCCESS = "\033[38;5;82m"      # Green
    WARNING = "\033[38;5;221m"     # Yellow
    ERROR = "\033[38;5;203m"       # Red
    MUTED = "\033[38;5;240m"       # Gray
    INFO = "\033[38;5;117m"        # Light blue
    
    # Box drawing
    BOX_V = "│"
    BOX_H = "─"
    BOX_TL = "┌"
    BOX_TR = "┐"
    BOX_BL = "└"
    BOX_BR = "┘"
    BOX_VR = "├"
    BOX_VL = "┤"
    BOX_HU = "┴"
    BOX_HD = "┬"
    BOX_CROSS = "┼"


class Icons:
    """Unicode icons for visual feedback"""
    # Platform icons
    GITHUB = "🐙"
    STACKOVERFLOW = "📚"
    YOUTUBE = "📺"
    BLUESKY = "🦋"
    MASTODON = "🐘"
    REDDIT = "👽"
    MEDIUM = "📰"
    TELEGRAM = "✈️"
    
    # Status icons
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    
    # Action icons
    PROCESSING = "⚙"
    STATS = "📊"
    TIME = "⏱"
    CALENDAR = "📅"
    USER = "👤"
    STAR = "⭐"
    CHART = "📈"
    BULLET = "•"


class UI:
    """terminal UI system with box-drawing and colors"""
    
    def __init__(self):
        self.indent_level = 0
        self.indent_str = "  "
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text"""
        return f"{color}{text}{Theme.RESET}"
    
    def _prefix(self) -> str:
        """Get current indentation prefix"""
        return self.indent_str * self.indent_level
    
    def indent(self):
        """Context manager for indentation"""
        class IndentContext:
            def __init__(self, ui_instance):
                self.ui = ui_instance
            
            def __enter__(self):
                self.ui.indent_level += 1
                return self
            
            def __exit__(self, *args):
                self.ui.indent_level -= 1
        
        return IndentContext(self)
    
    def header(self, title: str, icon: str = ""):
        """Display section header"""
        prefix = self._prefix()
        icon_str = f"{icon} " if icon else ""
        print(f"\n{prefix}{self._colorize(f'{icon_str}{title}', Theme.BOLD + Theme.PRIMARY)}")
    
    def section(self, title: str):
        """Display section title"""
        prefix = self._prefix()
        print(f"\n{prefix}{self._colorize(title, Theme.BOLD)}")
    
    def subsection(self, title: str):
        """Display subsection title"""
        prefix = self._prefix()
        print(f"{prefix}{self._colorize(title, Theme.PRIMARY)}")
    
    def success(self, message: str, detail: str = ""):
        """Display success message"""
        prefix = self._prefix()
        icon = self._colorize(Icons.SUCCESS, Theme.SUCCESS)
        msg = self._colorize(message, Theme.SUCCESS)
        detail_str = f" {self._colorize(detail, Theme.MUTED)}" if detail else ""
        print(f"{prefix}{icon} {msg}{detail_str}")
    
    def error(self, message: str, detail: str = ""):
        """Display error message"""
        prefix = self._prefix()
        icon = self._colorize(Icons.ERROR, Theme.ERROR)
        msg = self._colorize(message, Theme.ERROR)
        detail_str = f"\n{prefix}  {self._colorize(detail, Theme.MUTED)}" if detail else ""
        print(f"{prefix}{icon} {msg}{detail_str}")
    
    def warning(self, message: str, detail: str = ""):
        """Display warning message"""
        prefix = self._prefix()
        icon = self._colorize(Icons.WARNING, Theme.WARNING)
        msg = self._colorize(message, Theme.WARNING)
        detail_str = f" {self._colorize(detail, Theme.MUTED)}" if detail else ""
        print(f"{prefix}{icon} {msg}{detail_str}")
    
    def info(self, message: str, detail: str = ""):
        """Display info message"""
        prefix = self._prefix()
        msg = self._colorize(message, Theme.INFO)
        detail_str = f": {detail}" if detail else ""
        print(f"{prefix}{Icons.INFO} {msg}{detail_str}")
    
    def step(self, message: str):
        """Display step message"""
        prefix = self._prefix()
        print(f"{prefix}{self._colorize('→', Theme.PRIMARY)} {message}")
    
    def muted(self, message: str):
        """Display muted/dimmed message"""
        prefix = self._prefix()
        print(f"{prefix}{self._colorize(message, Theme.MUTED)}")
    
    def spinner(self, message: str):
        """Display loading message"""
        prefix = self._prefix()
        print(f"{prefix}{self._colorize('⣾', Theme.PRIMARY)} {message}")
    
    def keyvalue(self, key: str, value: str, icon: str = ""):
        """Display key-value pair"""
        prefix = self._prefix()
        icon_str = f"{icon} " if icon else ""
        key_str = self._colorize(f"{icon_str}{key}:", Theme.MUTED)
        print(f"{prefix}{key_str} {value}")
    
    def metric(self, label: str, value: str, icon: str = ""):
        """Display metric"""
        prefix = self._prefix()
        icon_str = f"{icon} " if icon else Icons.BULLET + " "
        label_str = self._colorize(label, Theme.MUTED)
        value_str = self._colorize(value, Theme.BOLD)
        print(f"{prefix}{icon_str}{label_str}: {value_str}")
    
    def stat_row(self, stats: Dict[str, str]):
        """Display stats in a row"""
        prefix = self._prefix()
        parts = []
        for label, value in stats.items():
            label_str = self._colorize(label, Theme.MUTED)
            value_str = self._colorize(value, Theme.BOLD)
            parts.append(f"{label_str}: {value_str}")
        print(f"{prefix}{' │ '.join(parts)}")
    
    def progress(self, current: int, total: int, label: str = "items"):
        """Display progress"""
        prefix = self._prefix()
        percentage = (current / total * 100) if total > 0 else 0
        bar_length = 30
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_str = self._colorize(f"{percentage:5.1f}%", Theme.PRIMARY)
        count_str = self._colorize(f"{current:,}/{total:,}", Theme.MUTED)
        
        print(f"\r{prefix}{bar} {progress_str} {count_str} {label}", end="", flush=True)
        
        if current >= total:
            print()  # New line when complete
    
    def list_item(self, text: str, level: int = 0):
        """Display list item"""
        prefix = self._prefix()
        indent = "  " * level
        print(f"{prefix}{indent}{self._colorize('•', Theme.PRIMARY)} {text}")
    
    def choice_list(self, items: List[str]):
        """Display numbered choice list"""
        prefix = self._prefix()
        print()
        with self.indent():
            for i, item in enumerate(items, 1):
                num = self._colorize(f"{i}.", Theme.PRIMARY)
                print(f"{prefix}{self.indent_str}{num} {item}")
        print()
    
    def separator(self):
        """Display separator line"""
        prefix = self._prefix()
        line = self._colorize(Theme.BOX_H * 60, Theme.MUTED)
        print(f"{prefix}{line}")
    
    def space(self):
        """Add vertical space"""
        print()


# ============================================================================
# BASE EXTRACTOR CLASS
# ============================================================================

class BaseExtractor(ABC):
    """Abstract base class for all platform extractors"""
    
    def __init__(self, ui: UI):
        self.ui = ui
    
    @abstractmethod
    def run(self, username: str) -> Optional[str]:
        """
        Execute extraction for given username
        Returns: filename of saved data, or None if failed
        """
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Platform name (lowercase)"""
        pass
    
    @property
    @abstractmethod
    def platform_icon(self) -> str:
        """Platform icon"""
        pass
    
    def _save_json(self, data: Dict[str, Any], username: str) -> str:
        """Save data to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.platform_name}_{username}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def _parse_date(self, date_str: str) -> str:
        """Parse ISO date to readable format"""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return date_str


# ============================================================================
# GITHUB EXTRACTOR
# ============================================================================

class GitHubExtractor(BaseExtractor):
    """Extract data from GitHub user profiles"""
    
    platform_name = "github"
    platform_icon = Icons.GITHUB
    
    def __init__(self, ui: UI, token: Optional[str] = None):
        super().__init__(ui)
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OSINT-Extractor'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def run(self, username: str) -> Optional[str]:
        """Extract GitHub user data"""
        try:
            import requests
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("GITHUB EXTRACTOR", self.platform_icon)
        self.ui.step(f"Target: {username}")
        self.ui.space()
        
        # Get user info
        user_info = self._get_user_info(requests, username)
        if not user_info:
            return None
        
        # Get repositories
        repos = self._get_repositories(requests, username)
        
        # Get events
        events = self._get_events(requests, username)
        
        # Save
        data = {
            'user_info': user_info,
            'repositories': repos,
            'events': events,
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success("Data saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _get_user_info(self, requests, username: str) -> Optional[Dict]:
        """Get user profile information"""
        self.ui.section("User Profile")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching profile...")
                
                response = requests.get(
                    f"{self.base_url}/users/{username}",
                    headers=self.headers,
                    timeout=15
                )
                response.raise_for_status()
                
                user = response.json()
                
                info = {
                    'username': user.get('login', ''),
                    'name': user.get('name', ''),
                    'bio': user.get('bio', ''),
                    'company': user.get('company', ''),
                    'location': user.get('location', ''),
                    'email': user.get('email', ''),
                    'blog': user.get('blog', ''),
                    'twitter': user.get('twitter_username', ''),
                    'public_repos': user.get('public_repos', 0),
                    'public_gists': user.get('public_gists', 0),
                    'followers': user.get('followers', 0),
                    'following': user.get('following', 0),
                    'created_at': user.get('created_at', ''),
                    'updated_at': user.get('updated_at', ''),
                    'profile_url': user.get('html_url', '')
                }
                
                # Display info
                self.ui.keyvalue("Name", info['name'] or info['username'], Icons.USER)
                if info['bio']:
                    bio = info['bio'][:100] + "..." if len(info['bio']) > 100 else info['bio']
                    self.ui.keyvalue("Bio", bio)
                
                self.ui.space()
                self.ui.stat_row({
                    "Repos": f"{info['public_repos']:,}",
                    "Followers": f"{info['followers']:,}",
                    "Following": f"{info['following']:,}"
                })
                
                self.ui.space()
                self.ui.success("Profile retrieved")
                
                return info
                
            except requests.RequestException as e:
                self.ui.error("Failed to fetch profile", str(e))
                return None
    
    def _get_repositories(self, requests, username: str) -> List[Dict]:
        """Get user repositories"""
        self.ui.section("Repositories")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching repositories...")
                
                response = requests.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={'per_page': 100, 'sort': 'updated'},
                    timeout=15
                )
                response.raise_for_status()
                
                repos = response.json()
                
                parsed_repos = []
                for repo in repos:
                    parsed_repos.append({
                        'name': repo.get('name', ''),
                        'description': repo.get('description', ''),
                        'language': repo.get('language', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'watchers': repo.get('watchers_count', 0),
                        'created_at': repo.get('created_at', ''),
                        'updated_at': repo.get('updated_at', ''),
                        'url': repo.get('html_url', ''),
                        'topics': repo.get('topics', [])
                    })
                
                self.ui.success(f"{len(parsed_repos)} repository(ies) retrieved")
                
                return parsed_repos
                
            except requests.RequestException as e:
                self.ui.warning("Failed to fetch repositories", str(e))
                return []
    
    def _get_events(self, requests, username: str) -> List[Dict]:
        """Get user events"""
        self.ui.section("Recent Events")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching events...")
                
                response = requests.get(
                    f"{self.base_url}/users/{username}/events/public",
                    headers=self.headers,
                    params={'per_page': 100},
                    timeout=15
                )
                response.raise_for_status()
                
                events = response.json()
                
                parsed_events = []
                for event in events:
                    parsed_events.append({
                        'type': event.get('type', ''),
                        'repo': event.get('repo', {}).get('name', ''),
                        'created_at': event.get('created_at', ''),
                        'payload': event.get('payload', {})
                    })
                
                self.ui.success(f"{len(parsed_events)} event(s) retrieved")
                
                return parsed_events
                
            except requests.RequestException as e:
                self.ui.warning("Failed to fetch events", str(e))
                return []


# ============================================================================
# STACKOVERFLOW EXTRACTOR
# ============================================================================

class StackOverflowExtractor(BaseExtractor):
    """Extract data from Stack Overflow user profiles"""
    
    platform_name = "stackoverflow"
    platform_icon = Icons.STACKOVERFLOW
    
    def __init__(self, ui: UI, api_key: Optional[str] = None):
        super().__init__(ui)
        self.api_key = api_key
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
    
    def run(self, username: str) -> Optional[str]:
        """Extract Stack Overflow user data"""
        try:
            import requests
            import gzip
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("STACK OVERFLOW EXTRACTOR", self.platform_icon)
        
        if self.api_key:
            self.ui.info("API Key configured", "Rate limit: 10,000 req/day")
        else:
            self.ui.info("No API key", "Rate limit: 300 req/day")
        
        self.ui.space()
        
        # Search users
        users = self._search_users(requests, username)
        if not users:
            return None
        
        # User selection (can be multiple)
        selected_ids = self._select_user(users)
        if not selected_ids:
            return None
        
        # Extract each user data
        all_users_data = []
        for idx, user_id in enumerate(selected_ids, 1):
            if len(selected_ids) > 1:
                self.ui.space()
                self.ui.separator()
                self.ui.space()
                self.ui.subsection(f"Extracting User {idx}/{len(selected_ids)}")
                self.ui.space()
            
            data = self._extract_user_data(requests, gzip, user_id)
            if data:
                all_users_data.append(data)
            
            # Cooldown between users
            if idx < len(selected_ids):
                time.sleep(1)
        
        if not all_users_data:
            return None
        
        # Save (with all users in single file)
        export_data = {
            'users': all_users_data,
            'total_users': len(all_users_data),
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(export_data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success(f"{len(all_users_data)} user(s) saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _search_users(self, requests, username: str) -> Optional[List[Dict]]:
        """Search for users"""
        self.ui.section("User Search")
        
        with self.ui.indent():
            self.ui.step(f"Searching for: {username}")
            self.ui.space()
            
            try:
                params = {
                    'inname': username,
                    'pagesize': 10,
                    'order': 'desc',
                    'sort': 'reputation',
                    'site': self.site
                }
                
                if self.api_key:
                    params['key'] = self.api_key
                
                response = requests.get(
                    f"{self.base_url}/users",
                    params=params,
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                users = data.get('items', [])
                
                if users:
                    self.ui.success(f"Found {len(users)} user(s)")
                else:
                    self.ui.error("No users found")
                
                return users
                
            except requests.RequestException as e:
                self.ui.error("Search failed", str(e))
                return None
    
    def _select_user(self, users: List[Dict]) -> Optional[List[int]]:
        """Let user select from found users (supports multiple selection)"""
        self.ui.space()
        self.ui.subsection("Users Found")
        self.ui.space()
        
        with self.ui.indent():
            for i, user in enumerate(users[:5], 1):
                name = user.get('display_name', 'N/A')
                rep = user.get('reputation', 0)
                self.ui.list_item(f"{name} - {rep:,} reputation", level=0)
        
        self.ui.space()
        
        with self.ui.indent():
            try:
                choice = input(self.ui._colorize(
                    "→ Select user(s) (e.g., 1 or 1,2,3 or Enter for all): ",
                    Theme.PRIMARY
                )).strip()
                
                if not choice:
                    # Default: all users
                    selected_indices = list(range(len(users)))
                else:
                    # Parse comma-separated list
                    selected_indices = []
                    for part in choice.split(','):
                        idx = int(part.strip()) - 1
                        if 0 <= idx < len(users):
                            selected_indices.append(idx)
                    
                    if not selected_indices:
                        self.ui.warning("Invalid selection, using first user")
                        selected_indices = [0]
                
                # Show selection
                selected_names = [users[i]['display_name'] for i in selected_indices]
                if len(selected_names) == 1:
                    self.ui.success(f"Selected: {selected_names[0]}")
                else:
                    self.ui.success(f"Selected {len(selected_names)} user(s): {', '.join(selected_names)}")
                
                # Return list of user IDs
                return [users[i]['user_id'] for i in selected_indices]
                
            except (ValueError, KeyError):
                self.ui.warning("Invalid selection, using first user")
                return [users[0]['user_id']]
    
    def _extract_user_data(self, requests, gzip, user_id: int) -> Optional[Dict]:
        """Extract all data for a user"""
        self.ui.space()
        self.ui.separator()
        self.ui.space()
        
        # Get profile
        user_info = self._get_profile(requests, gzip, user_id)
        if not user_info:
            return None
        
        # Get questions
        questions = self._get_questions(requests, gzip, user_id)
        
        # Get answers
        answers = self._get_answers(requests, gzip, user_id)
        
        # Get badges
        badges = self._get_badges(requests, gzip, user_id)
        
        return {
            'user_info': user_info,
            'questions': questions,
            'answers': answers,
            'badges': badges,
            'extraction_date': datetime.now().isoformat()
        }
    
    def _make_request(self, requests, gzip, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with proper handling"""
        params['site'] = self.site
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            # Handle gzipped response
            if response.content[:2] == b'\x1f\x8b':
                data = json.loads(gzip.decompress(response.content))
            else:
                data = response.json()
            
            return data
            
        except requests.RequestException:
            return None
    
    def _get_profile(self, requests, gzip, user_id: int) -> Optional[Dict]:
        """Get user profile"""
        self.ui.section("Profile")
        
        with self.ui.indent():
            self.ui.spinner("Fetching profile...")
            
            data = self._make_request(
                requests, gzip,
                f'users/{user_id}',
                {'filter': 'withbody'}
            )
            
            if not data or 'items' not in data or not data['items']:
                self.ui.error("User not found")
                return None
            
            user = data['items'][0]
            
            info = {
                'user_id': user['user_id'],
                'display_name': user['display_name'],
                'link': user['link'],
                'reputation': user['reputation'],
                'badge_counts': user['badge_counts'],
                'creation_date': datetime.fromtimestamp(user['creation_date']).strftime('%Y-%m-%d'),
                'location': user.get('location'),
                'website_url': user.get('website_url')
            }
            
            self.ui.keyvalue("Name", info['display_name'], Icons.USER)
            self.ui.keyvalue("Reputation", f"{info['reputation']:,}", Icons.STAR)
            
            badges = info['badge_counts']
            self.ui.space()
            self.ui.stat_row({
                "🥇 Gold": str(badges.get('gold', 0)),
                "🥈 Silver": str(badges.get('silver', 0)),
                "🥉 Bronze": str(badges.get('bronze', 0))
            })
            
            self.ui.space()
            self.ui.success("Profile retrieved")
            
            return info
    
    def _get_questions(self, requests, gzip, user_id: int) -> List[Dict]:
        """Get user questions"""
        self.ui.section("Questions")
        
        with self.ui.indent():
            self.ui.spinner("Fetching questions...")
            
            data = self._make_request(
                requests, gzip,
                f'users/{user_id}/questions',
                {'page': 1, 'pagesize': 100, 'order': 'desc', 'sort': 'votes'}
            )
            
            questions = data.get('items', []) if data else []
            self.ui.success(f"{len(questions)} question(s) retrieved")
            
            return questions
    
    def _get_answers(self, requests, gzip, user_id: int) -> List[Dict]:
        """Get user answers"""
        self.ui.section("Answers")
        
        with self.ui.indent():
            self.ui.spinner("Fetching answers...")
            
            data = self._make_request(
                requests, gzip,
                f'users/{user_id}/answers',
                {'page': 1, 'pagesize': 100, 'order': 'desc', 'sort': 'votes'}
            )
            
            answers = data.get('items', []) if data else []
            self.ui.success(f"{len(answers)} answer(s) retrieved")
            
            return answers
    
    def _get_badges(self, requests, gzip, user_id: int) -> List[Dict]:
        """Get user badges"""
        self.ui.section("Badges")
        
        with self.ui.indent():
            self.ui.spinner("Fetching badges...")
            
            data = self._make_request(
                requests, gzip,
                f'users/{user_id}/badges',
                {'page': 1, 'pagesize': 100, 'order': 'desc', 'sort': 'rank'}
            )
            
            badges = data.get('items', []) if data else []
            self.ui.success(f"{len(badges)} badge(s) retrieved")
            
            return badges


# ============================================================================
# YOUTUBE EXTRACTOR
# ============================================================================

class YouTubeExtractor(BaseExtractor):
    """Extract data from YouTube channels"""
    
    platform_name = "youtube"
    platform_icon = Icons.YOUTUBE
    
    def __init__(self, ui: UI, api_key: Optional[str] = None):
        super().__init__(ui)
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def run(self, username: str) -> Optional[str]:
        """Extract YouTube channel data"""
        if not self.api_key:
            self.ui.error("YouTube API key required", "Add to config.yaml")
            return None
        
        try:
            import requests
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("YOUTUBE EXTRACTOR", self.platform_icon)
        self.ui.step(f"Searching for: {username}")
        self.ui.space()
        
        # Search for channels
        channels = self._search_channels(requests, username)
        if not channels:
            return None
        
        # User selection (can be multiple)
        selected_ids = self._select_channels(channels)
        if not selected_ids:
            return None
        
        # Extract each channel data
        all_channels_data = []
        for idx, channel_id in enumerate(selected_ids, 1):
            if len(selected_ids) > 1:
                self.ui.space()
                self.ui.separator()
                self.ui.space()
                self.ui.subsection(f"Extracting Channel {idx}/{len(selected_ids)}")
                self.ui.space()
            
            data = self._extract_channel_data(requests, channel_id)
            if data:
                all_channels_data.append(data)
            
            # Cooldown between channels
            if idx < len(selected_ids):
                time.sleep(1)
        
        if not all_channels_data:
            return None
        
        # Save (with all channels in single file)
        export_data = {
            'channels': all_channels_data,
            'total_channels': len(all_channels_data),
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(export_data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success(f"{len(all_channels_data)} channel(s) saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _search_channels(self, requests, query: str) -> Optional[List[Dict]]:
        """Search for channels"""
        self.ui.section("Channel Search")
        
        with self.ui.indent():
            self.ui.spinner(f"Searching for: {query}")
            self.ui.space()
            
            try:
                # Search by query
                response = requests.get(
                    f"{self.base_url}/search",
                    params={
                        'part': 'snippet',
                        'q': query,
                        'type': 'channel',
                        'maxResults': 10,
                        'key': self.api_key
                    },
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', [])
                
                if not items:
                    self.ui.error("No channels found")
                    return None
                
                # Get channel IDs and fetch full details
                channel_ids = [item['snippet']['channelId'] for item in items]
                
                # Get statistics for all channels
                response = requests.get(
                    f"{self.base_url}/channels",
                    params={
                        'part': 'snippet,statistics',
                        'id': ','.join(channel_ids),
                        'key': self.api_key
                    },
                    timeout=15
                )
                response.raise_for_status()
                
                channels_data = response.json()
                channels = channels_data.get('items', [])
                
                if channels:
                    self.ui.success(f"Found {len(channels)} channel(s)")
                else:
                    self.ui.error("No channels found")
                
                return channels
                
            except requests.RequestException as e:
                self.ui.error("Search failed", str(e))
                return None
    
    def _select_channels(self, channels: List[Dict]) -> Optional[List[str]]:
        """Let user select from found channels (supports multiple selection)"""
        self.ui.space()
        self.ui.subsection("Channels Found")
        self.ui.space()
        
        with self.ui.indent():
            for i, channel in enumerate(channels[:10], 1):
                snippet = channel.get('snippet', {})
                stats = channel.get('statistics', {})
                
                title = snippet.get('title', 'N/A')
                subscribers = int(stats.get('subscriberCount', 0))
                video_count = int(stats.get('videoCount', 0))
                
                self.ui.list_item(
                    f"{title} - {subscribers:,} subscribers, {video_count:,} videos",
                    level=0
                )
        
        self.ui.space()
        
        with self.ui.indent():
            try:
                choice = input(self.ui._colorize(
                    "→ Select channel(s) (e.g., 1 or 1,2,3 or Enter for all): ",
                    Theme.PRIMARY
                )).strip()
                
                if not choice:
                    # Default: all channels
                    selected_indices = list(range(len(channels)))
                else:
                    # Parse comma-separated list
                    selected_indices = []
                    for part in choice.split(','):
                        idx = int(part.strip()) - 1
                        if 0 <= idx < len(channels):
                            selected_indices.append(idx)
                    
                    if not selected_indices:
                        self.ui.warning("Invalid selection, using first channel")
                        selected_indices = [0]
                
                # Show selection
                selected_names = [channels[i]['snippet']['title'] for i in selected_indices]
                if len(selected_names) == 1:
                    self.ui.success(f"Selected: {selected_names[0]}")
                else:
                    self.ui.success(f"Selected {len(selected_names)} channel(s): {', '.join(selected_names)}")
                
                # Return list of channel IDs
                return [channels[i]['id'] for i in selected_indices]
                
            except (ValueError, KeyError, IndexError):
                self.ui.warning("Invalid selection, using first channel")
                return [channels[0]['id']]
    
    def _extract_channel_data(self, requests, channel_id: str) -> Optional[Dict]:
        """Extract all data for a channel"""
        # Get channel info
        channel_info = self._get_channel_info(requests, channel_id)
        if not channel_info:
            return None
        
        # Get videos
        videos = self._get_videos(requests, channel_id)
        
        return {
            'channel_info': channel_info,
            'videos': videos,
            'extraction_date': datetime.now().isoformat()
        }
    
    def _get_channel_info(self, requests, channel_id: str) -> Optional[Dict]:
        """Get channel information"""
        self.ui.section("Channel Info")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching channel...")
                
                response = requests.get(
                    f"{self.base_url}/channels",
                    params={
                        'part': 'snippet,statistics',
                        'id': channel_id,
                        'key': self.api_key
                    },
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                
                if 'items' not in data or not data['items']:
                    self.ui.error("Channel not found")
                    return None
                
                channel = data['items'][0]
                snippet = channel['snippet']
                stats = channel['statistics']
                
                info = {
                    'id': channel['id'],
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'published_at': snippet['publishedAt'],
                    'thumbnail': snippet['thumbnails']['high']['url'],
                    'subscribers': int(stats.get('subscriberCount', 0)),
                    'video_count': int(stats.get('videoCount', 0)),
                    'view_count': int(stats.get('viewCount', 0)),
                    'url': f"https://www.youtube.com/channel/{channel['id']}"
                }
                
                self.ui.keyvalue("Channel", info['title'], Icons.YOUTUBE)
                self.ui.space()
                self.ui.stat_row({
                    "Subscribers": f"{info['subscribers']:,}",
                    "Videos": f"{info['video_count']:,}",
                    "Views": f"{info['view_count']:,}"
                })
                
                self.ui.space()
                self.ui.success("Channel retrieved")
                
                return info
                
            except requests.RequestException as e:
                self.ui.error("Failed to fetch channel", str(e))
                return None
    
    def _get_videos(self, requests, channel_id: str) -> List[Dict]:
        """Get channel videos"""
        self.ui.section("Videos")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching videos...")
                
                response = requests.get(
                    f"{self.base_url}/search",
                    params={
                        'part': 'snippet',
                        'channelId': channel_id,
                        'type': 'video',
                        'order': 'date',
                        'maxResults': 50,
                        'key': self.api_key
                    },
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                videos = []
                
                for item in data.get('items', []):
                    snippet = item['snippet']
                    videos.append({
                        'video_id': item['id']['videoId'],
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'published_at': snippet['publishedAt'],
                        'thumbnail': snippet['thumbnails']['high']['url'],
                        'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                    })
                
                self.ui.success(f"{len(videos)} video(s) retrieved")
                
                return videos
                
            except requests.RequestException as e:
                self.ui.warning("Failed to fetch videos", str(e))
                return []


# ============================================================================
# BLUESKY EXTRACTOR
# ============================================================================

class BlueskyExtractor(BaseExtractor):
    """Extract posts from Bluesky user profiles"""
    
    platform_name = "bluesky"
    platform_icon = Icons.BLUESKY
    
    def __init__(self, ui: UI):
        super().__init__(ui)
        self.base_url = "https://public.api.bsky.app"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def run(self, username: str) -> Optional[str]:
        """Extract Bluesky user data"""
        try:
            import requests
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("BLUESKY EXTRACTOR", self.platform_icon)
        self.ui.step(f"Target: {username}")
        self.ui.space()
        
        # Resolve handle
        did = self._resolve_handle(requests, username)
        if not did:
            return None
        
        # Get profile
        profile = self._get_profile(requests, did)
        if not profile:
            return None
        
        # Get posts
        posts = self._get_posts(requests, did)
        
        # Save
        data = {
            'profile': profile,
            'posts': posts,
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success("Data saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _resolve_handle(self, requests, handle: str) -> Optional[str]:
        """Resolve handle to DID"""
        self.ui.section("Handle Resolution")
        
        with self.ui.indent():
            handle = handle.replace('@', '').strip()
            
            # Try multiple variations
            handles_to_try = [handle]
            if '.' not in handle:
                handles_to_try.append(f"{handle}.bsky.social")
                handles_to_try.append(f"{handle}.com")
            
            url = f"{self.base_url}/xrpc/com.atproto.identity.resolveHandle"
            
            for h in handles_to_try:
                self.ui.muted(f"Trying: {h}")
                
                try:
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params={'handle': h},
                        timeout=15
                    )
                    response.raise_for_status()
                    
                    data = response.json()
                    did = data.get('did')
                    
                    if did:
                        self.ui.success(f"Handle resolved: {h}")
                        return did
                        
                except requests.RequestException:
                    continue
            
            self.ui.error("Handle not found")
            return None
    
    def _get_profile(self, requests, actor: str) -> Optional[Dict]:
        """Get profile information"""
        self.ui.section("Profile")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching profile...")
                
                url = f"{self.base_url}/xrpc/app.bsky.actor.getProfile"
                response = requests.get(
                    url,
                    headers=self.headers,
                    params={'actor': actor},
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                
                profile = {
                    'handle': data.get('handle', ''),
                    'display_name': data.get('displayName', ''),
                    'description': data.get('description', ''),
                    'followers_count': data.get('followersCount', 0),
                    'follows_count': data.get('followsCount', 0),
                    'posts_count': data.get('postsCount', 0),
                    'profile_url': f"https://bsky.app/profile/{data.get('handle', '')}"
                }
                
                self.ui.keyvalue("Handle", profile['handle'], Icons.USER)
                self.ui.keyvalue("Name", profile['display_name'])
                
                self.ui.space()
                self.ui.stat_row({
                    "Posts": f"{profile['posts_count']:,}",
                    "Followers": f"{profile['followers_count']:,}",
                    "Following": f"{profile['follows_count']:,}"
                })
                
                self.ui.space()
                self.ui.success("Profile retrieved")
                
                return profile
                
            except requests.RequestException as e:
                self.ui.error("Failed to fetch profile", str(e))
                return None
    
    def _get_posts(self, requests, actor: str) -> List[Dict]:
        """Get user posts"""
        self.ui.section("Posts Extraction")
        
        with self.ui.indent():
            all_posts = []
            cursor = None
            max_posts = 200
            
            self.ui.info(f"Fetching up to {max_posts} posts...")
            self.ui.space()
            
            url = f"{self.base_url}/xrpc/app.bsky.feed.getAuthorFeed"
            
            while len(all_posts) < max_posts:
                try:
                    params = {'actor': actor, 'limit': 100}
                    if cursor:
                        params['cursor'] = cursor
                    
                    response = requests.get(url, headers=self.headers, params=params, timeout=15)
                    response.raise_for_status()
                    
                    data = response.json()
                    feed = data.get('feed', [])
                    
                    if not feed:
                        break
                    
                    for item in feed:
                        post_data = item.get('post', {})
                        record = post_data.get('record', {})
                        
                        all_posts.append({
                            'text': record.get('text', ''),
                            'created_at': record.get('createdAt', ''),
                            'reply_count': post_data.get('replyCount', 0),
                            'repost_count': post_data.get('repostCount', 0),
                            'like_count': post_data.get('likeCount', 0),
                            'url': f"https://bsky.app/profile/{post_data.get('author', {}).get('handle', '')}/post/{post_data.get('uri', '').split('/')[-1]}"
                        })
                    
                    current = min(len(all_posts), max_posts)
                    self.ui.progress(current, max_posts, "posts")
                    
                    cursor = data.get('cursor')
                    if not cursor:
                        break
                    
                    time.sleep(0.5)
                    
                except requests.RequestException:
                    break
            
            final_count = min(len(all_posts), max_posts)
            all_posts = all_posts[:max_posts]
            
            self.ui.space()
            self.ui.success(f"{final_count} posts retrieved")
            
            return all_posts


# ============================================================================
# MASTODON EXTRACTOR
# ============================================================================

class MastodonExtractor(BaseExtractor):
    """Extract toots from Mastodon instances"""
    
    platform_name = "mastodon"
    platform_icon = Icons.MASTODON
    
    def __init__(self, ui: UI, instance: str = "infosec.exchange"):
        super().__init__(ui)
        self.instance = instance
        self.base_url = f"https://{instance}"
        self.api_url = f"{self.base_url}/api/v1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def run(self, username: str) -> Optional[str]:
        """Extract Mastodon user data"""
        try:
            import requests
            from html import unescape
            import re
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("MASTODON EXTRACTOR", self.platform_icon)
        self.ui.info("Instance", self.instance)
        self.ui.step(f"Target: @{username}@{self.instance}")
        self.ui.space()
        
        # Search account
        account = self._search_account(requests, username)
        if not account:
            return None
        
        # Get statuses
        statuses = self._get_statuses(requests, unescape, re, account['id'])
        
        # Save
        data = {
            'account': account,
            'statuses': statuses,
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success("Data saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _search_account(self, requests, username: str) -> Optional[Dict]:
        """Search for account"""
        self.ui.section("Account Search")
        
        with self.ui.indent():
            try:
                self.ui.spinner(f"Searching for @{username}...")
                
                url = f"{self.api_url}/accounts/lookup"
                response = requests.get(
                    url,
                    headers=self.headers,
                    params={'acct': username},
                    timeout=15
                )
                response.raise_for_status()
                
                account = response.json()
                
                info = {
                    'id': account.get('id', ''),
                    'username': account.get('username', ''),
                    'display_name': account.get('display_name', ''),
                    'url': account.get('url', ''),
                    'followers_count': account.get('followers_count', 0),
                    'following_count': account.get('following_count', 0),
                    'statuses_count': account.get('statuses_count', 0)
                }
                
                self.ui.keyvalue("Display Name", info['display_name'], Icons.USER)
                self.ui.keyvalue("Username", f"@{info['username']}")
                
                self.ui.space()
                self.ui.stat_row({
                    "Toots": f"{info['statuses_count']:,}",
                    "Followers": f"{info['followers_count']:,}",
                    "Following": f"{info['following_count']:,}"
                })
                
                self.ui.space()
                self.ui.success("Account found")
                
                return info
                
            except requests.RequestException as e:
                self.ui.error("Search failed", str(e))
                return None
    
    def _get_statuses(self, requests, unescape, re, account_id: str) -> List[Dict]:
        """Get account statuses"""
        self.ui.section("Toots Extraction")
        
        with self.ui.indent():
            all_statuses = []
            url = f"{self.api_url}/accounts/{account_id}/statuses"
            params = {'limit': 40}
            max_toots = 200
            
            self.ui.info(f"Fetching up to {max_toots} toots...")
            self.ui.space()
            
            while len(all_statuses) < max_toots:
                try:
                    response = requests.get(url, headers=self.headers, params=params, timeout=15)
                    response.raise_for_status()
                    
                    statuses = response.json()
                    if not statuses:
                        break
                    
                    for status in statuses:
                        content = self._clean_html(unescape, re, status.get('content', ''))
                        
                        all_statuses.append({
                            'id': status.get('id', ''),
                            'created_at': status.get('created_at', ''),
                            'content': content,
                            'url': status.get('url', ''),
                            'replies_count': status.get('replies_count', 0),
                            'reblogs_count': status.get('reblogs_count', 0),
                            'favourites_count': status.get('favourites_count', 0)
                        })
                    
                    current = min(len(all_statuses), max_toots)
                    self.ui.progress(current, max_toots, "toots")
                    
                    # Get next page
                    link_header = response.headers.get('Link', '')
                    next_url = self._parse_link_header(link_header, 'next')
                    
                    if not next_url:
                        break
                    
                    url = next_url
                    params = {}
                    
                    time.sleep(0.5)
                    
                except requests.RequestException:
                    break
            
            final_count = min(len(all_statuses), max_toots)
            all_statuses = all_statuses[:max_toots]
            
            self.ui.space()
            self.ui.success(f"{final_count} toots retrieved")
            
            return all_statuses
    
    def _clean_html(self, unescape, re, html_text: str) -> str:
        """Remove HTML tags"""
        clean = html_text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        clean = re.sub('<.*?>', '', clean)
        clean = unescape(clean)
        return clean.strip()
    
    def _parse_link_header(self, link_header: str, rel: str) -> Optional[str]:
        """Parse Link header for pagination"""
        if not link_header:
            return None
        
        links = link_header.split(',')
        for link in links:
            parts = link.split(';')
            if len(parts) == 2:
                url = parts[0].strip()[1:-1]
                rel_part = parts[1].strip()
                if f'rel="{rel}"' in rel_part:
                    return url
        return None


# ============================================================================
# REDDIT EXTRACTOR
# ============================================================================

class RedditExtractor(BaseExtractor):
    """Extract posts and comments from Reddit user profiles"""
    
    platform_name = "reddit"
    platform_icon = Icons.REDDIT
    
    def __init__(self, ui: UI):
        super().__init__(ui)
        self.base_url = "https://www.reddit.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def run(self, username: str) -> Optional[str]:
        """Extract Reddit user data"""
        try:
            import requests
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("REDDIT EXTRACTOR", self.platform_icon)
        self.ui.step(f"Target: u/{username}")
        self.ui.space()
        
        # Get user info
        user_info = self._get_user_info(requests, username)
        if not user_info:
            return None
        
        # Get posts
        posts = self._get_posts(requests, username)
        
        # Get comments
        comments = self._get_comments(requests, username)
        
        # Save
        data = {
            'user_info': user_info,
            'posts': posts,
            'comments': comments,
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success("Data saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _get_user_info(self, requests, username: str) -> Optional[Dict]:
        """Get user information"""
        self.ui.section("User Profile")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching profile...")
                
                url = f"{self.base_url}/user/{username}/about.json"
                response = requests.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                data = response.json()
                
                if 'data' not in data:
                    self.ui.error("User not found")
                    return None
                
                user_data = data['data']
                
                info = {
                    'username': user_data.get('name', ''),
                    'created_utc': user_data.get('created_utc', 0),
                    'account_created': datetime.fromtimestamp(user_data.get('created_utc', 0)).strftime('%Y-%m-%d'),
                    'link_karma': user_data.get('link_karma', 0),
                    'comment_karma': user_data.get('comment_karma', 0),
                    'total_karma': user_data.get('total_karma', 0),
                    'profile_url': f"{self.base_url}/user/{username}"
                }
                
                self.ui.keyvalue("Username", info['username'], Icons.USER)
                self.ui.keyvalue("Created", info['account_created'], Icons.CALENDAR)
                
                self.ui.space()
                self.ui.stat_row({
                    "Total Karma": f"{info['total_karma']:,}",
                    "Post Karma": f"{info['link_karma']:,}",
                    "Comment Karma": f"{info['comment_karma']:,}"
                })
                
                self.ui.space()
                self.ui.success("Profile retrieved")
                
                return info
                
            except requests.RequestException as e:
                self.ui.error("Failed to fetch profile", str(e))
                return None
    
    def _get_posts(self, requests, username: str) -> List[Dict]:
        """Get user posts"""
        self.ui.section("Posts")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching posts...")
                
                url = f"{self.base_url}/user/{username}/submitted.json"
                response = requests.get(
                    url,
                    headers=self.headers,
                    params={'limit': 100, 'sort': 'new'},
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                posts = []
                
                if 'data' in data and 'children' in data['data']:
                    for item in data['data']['children']:
                        post_data = item['data']
                        posts.append({
                            'title': post_data.get('title', ''),
                            'subreddit': post_data.get('subreddit', ''),
                            'url': f"{self.base_url}{post_data.get('permalink', '')}",
                            'score': post_data.get('score', 0),
                            'num_comments': post_data.get('num_comments', 0),
                            'created': datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                self.ui.success(f"{len(posts)} posts retrieved")
                
                return posts
                
            except requests.RequestException as e:
                self.ui.warning("Failed to fetch posts", str(e))
                return []
    
    def _get_comments(self, requests, username: str) -> List[Dict]:
        """Get user comments"""
        self.ui.section("Comments")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Fetching comments...")
                time.sleep(1)  # Rate limiting
                
                url = f"{self.base_url}/user/{username}/comments.json"
                response = requests.get(
                    url,
                    headers=self.headers,
                    params={'limit': 100, 'sort': 'new'},
                    timeout=15
                )
                response.raise_for_status()
                
                data = response.json()
                comments = []
                
                if 'data' in data and 'children' in data['data']:
                    for item in data['data']['children']:
                        comment_data = item['data']
                        comments.append({
                            'body': comment_data.get('body', '')[:500],
                            'subreddit': comment_data.get('subreddit', ''),
                            'url': f"{self.base_url}{comment_data.get('permalink', '')}",
                            'score': comment_data.get('score', 0),
                            'created': datetime.fromtimestamp(comment_data.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                self.ui.success(f"{len(comments)} comments retrieved")
                
                return comments
                
            except requests.RequestException as e:
                self.ui.warning("Failed to fetch comments", str(e))
                return []


# ============================================================================
# MEDIUM EXTRACTOR
# ============================================================================

class MediumExtractor(BaseExtractor):
    """Extract articles from Medium RSS feed"""
    
    platform_name = "medium"
    platform_icon = Icons.MEDIUM
    
    def __init__(self, ui: UI):
        super().__init__(ui)
    
    def run(self, username: str) -> Optional[str]:
        """Extract Medium user data"""
        try:
            import requests
            import xml.etree.ElementTree as ET
        except ImportError:
            self.ui.error("Missing dependency", "pip install requests")
            return None
        
        self.ui.header("MEDIUM EXTRACTOR", self.platform_icon)
        self.ui.step(f"Target: @{username}")
        self.ui.space()
        
        # Fetch articles
        articles = self._fetch_articles(requests, ET, username)
        if not articles:
            return None
        
        # Save
        data = {
            'articles': articles,
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(data, username)
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success("Data saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    def _fetch_articles(self, requests, ET, username: str) -> Optional[List[Dict]]:
        """Fetch articles from RSS"""
        self.ui.section("Article Extraction")
        
        with self.ui.indent():
            rss_url = f"https://medium.com/feed/@{username}"
            self.ui.muted(f"RSS URL: {rss_url}")
            self.ui.space()
            
            try:
                self.ui.spinner("Fetching RSS feed...")
                
                response = requests.get(rss_url, timeout=10)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                articles = []
                
                for item in root.findall('.//item'):
                    article = {
                        'title': item.find('title').text if item.find('title') is not None else 'N/A',
                        'url': item.find('link').text if item.find('link') is not None else 'N/A',
                        'date': item.find('pubDate').text if item.find('pubDate') is not None else 'N/A',
                        'tags': [cat.text for cat in item.findall('category')]
                    }
                    articles.append(article)
                
                self.ui.success(f"{len(articles)} article(s) found")
                
                if articles:
                    self.ui.space()
                    self.ui.subsection("Recent Articles")
                    
                    with self.ui.indent():
                        for i, article in enumerate(articles[:5], 1):
                            title = article['title']
                            if len(title) > 60:
                                title = title[:57] + "..."
                            self.ui.list_item(title, level=0)
                        
                        if len(articles) > 5:
                            self.ui.muted(f"... and {len(articles) - 5} more")
                
                return articles
                
            except requests.RequestException as e:
                self.ui.error("Failed to fetch RSS feed", str(e))
                return None
            except ET.ParseError as e:
                self.ui.error("XML parse error", str(e))
                return None


# ============================================================================
# TELEGRAM EXTRACTOR
# ============================================================================

class TelegramExtractor(BaseExtractor):
    """Extract messages from Telegram channels and groups"""
    
    platform_name = "telegram"
    platform_icon = Icons.TELEGRAM
    
    def __init__(self, ui: UI, api_id: Optional[int] = None, api_hash: Optional[str] = None, 
                 phone: Optional[str] = None, session_name: str = "telegram_session"):
        super().__init__(ui)
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.client = None
    
    def run(self, username: str) -> Optional[str]:
        """Extract Telegram data"""
        if not self.api_id or not self.api_hash:
            self.ui.error("Telegram API credentials required", "Add to config.yaml")
            return None
        
        try:
            from telethon import TelegramClient, errors
            from telethon.tl.types import Channel
            import asyncio
        except ImportError:
            self.ui.error("Missing dependency", "pip install telethon")
            return None
        
        # Run async extraction
        return asyncio.run(self._run_async(TelegramClient, errors, Channel, username))
    
    async def _run_async(self, TelegramClient, errors, Channel, username: str) -> Optional[str]:
        """Async extraction logic"""
        self.ui.header("TELEGRAM EXTRACTOR", self.platform_icon)
        
        # Connect
        if not await self._connect(TelegramClient):
            return None
        
        # Get entity info
        entity_info = await self._get_entity_info(errors, Channel, username)
        if not entity_info:
            await self.client.disconnect()
            return None
        
        # Extract messages
        messages = await self._extract_messages(username)
        
        # Save
        data = {
            'entity_info': entity_info,
            'messages': messages,
            'extraction_date': datetime.now().isoformat()
        }
        
        filename = self._save_json(data, username)
        
        # Disconnect
        await self.client.disconnect()
        self.ui.muted("Disconnected")
        
        self.ui.section("Export")
        with self.ui.indent():
            self.ui.success("Data saved", filename)
        
        self.ui.space()
        self.ui.success("Extraction completed!")
        
        return filename
    
    async def _connect(self, TelegramClient) -> bool:
        """Connect to Telegram"""
        self.ui.section("Connection")
        
        with self.ui.indent():
            try:
                self.ui.spinner("Connecting to Telegram...")
                
                self.client = TelegramClient(
                    self.session_name,
                    self.api_id,
                    self.api_hash
                )
                
                if self.phone:
                    await self.client.start(phone=self.phone)
                else:
                    await self.client.start()
                
                me = await self.client.get_me()
                
                self.ui.success(
                    f"Connected as: {me.first_name}",
                    f"@{me.username}" if me.username else ""
                )
                
                return True
                
            except Exception as e:
                self.ui.error("Connection failed", str(e))
                return False
    
    async def _get_entity_info(self, errors, Channel, username: str) -> Optional[Dict]:
        """Get entity information"""
        self.ui.section("Target Information")
        
        with self.ui.indent():
            try:
                username = username.replace('@', '').strip()
                self.ui.spinner(f"Fetching info for @{username}...")
                
                entity = await self.client.get_entity(username)
                
                info = {
                    'id': entity.id,
                    'username': getattr(entity, 'username', None),
                    'title': getattr(entity, 'title', None) or getattr(entity, 'first_name', None),
                    'type': self._get_entity_type(Channel, entity)
                }
                
                if isinstance(entity, Channel):
                    info['participants_count'] = getattr(entity, 'participants_count', None)
                
                self.ui.keyvalue("Title", info['title'], self.platform_icon)
                self.ui.keyvalue("Username", f"@{info['username']}" if info['username'] else "N/A")
                self.ui.keyvalue("Type", info['type'])
                
                if info.get('participants_count'):
                    self.ui.space()
                    self.ui.metric("Members", f"{info['participants_count']:,}")
                
                self.ui.space()
                self.ui.success("Entity info retrieved")
                
                return info
                
            except errors.UsernameNotOccupiedError:
                self.ui.error(f"@{username} does not exist")
                return None
            except Exception as e:
                self.ui.error("Failed to fetch info", str(e))
                return None
    
    async def _extract_messages(self, username: str) -> List[Dict]:
        """Extract messages"""
        self.ui.section("Message Extraction")
        
        with self.ui.indent():
            max_messages = 800
            
            self.ui.subsection("Extraction Mode")
            with self.ui.indent():
                self.ui.keyvalue("Mode", "AI Analysis")
                self.ui.keyvalue("Messages", f"~{max_messages}")
                self.ui.muted("Optimized for AI sociodynamic analysis")
            
            self.ui.space()
            self.ui.info(f"Fetching {max_messages} messages...")
            self.ui.space()
            
            messages = []
            
            try:
                async for message in self.client.iter_messages(username, limit=max_messages):
                    msg_data = {
                        'id': message.id,
                        'date': message.date.isoformat() if message.date else None,
                        'text': message.text or '',
                        'views': message.views,
                        'forwards': message.forwards,
                        'has_media': bool(message.media)
                    }
                    
                    messages.append(msg_data)
                    
                    if len(messages) % 100 == 0:
                        self.ui.progress(len(messages), max_messages, "messages")
                
                self.ui.progress(len(messages), max_messages, "messages")
                
                self.ui.space()
                self.ui.success(f"{len(messages)} messages retrieved")
                
                return messages
                
            except Exception as e:
                self.ui.error("Failed to extract messages", str(e))
                return []
    
    def _get_entity_type(self, Channel, entity) -> str:
        """Get entity type string"""
        if isinstance(entity, Channel):
            if entity.broadcast:
                return "channel"
            elif entity.megagroup:
                return "supergroup"
            else:
                return "group"
        return "unknown"


# ============================================================================
# ORCHESTRATOR - Main Controller
# ============================================================================

class ExtractorOrchestrator:
    """Main orchestrator for multi-platform extraction"""
    
    PLATFORMS = {
        1: {"name": "stackoverflow", "icon": Icons.STACKOVERFLOW, "class": StackOverflowExtractor},
        2: {"name": "youtube", "icon": Icons.YOUTUBE, "class": YouTubeExtractor},
        3: {"name": "github", "icon": Icons.GITHUB, "class": GitHubExtractor},
        4: {"name": "bluesky", "icon": Icons.BLUESKY, "class": BlueskyExtractor},
        5: {"name": "mastodon", "icon": Icons.MASTODON, "class": MastodonExtractor},
        6: {"name": "reddit", "icon": Icons.REDDIT, "class": RedditExtractor},
        7: {"name": "medium", "icon": Icons.MEDIUM, "class": MediumExtractor},
        8: {"name": "telegram", "icon": Icons.TELEGRAM, "class": TelegramExtractor},
    }
    
    # Reverse mapping pour recherche par nom
    PLATFORMS_BY_NAME = {info["name"]: pid for pid, info in PLATFORMS.items()}
    
    def __init__(self, args=None):
        self.ui = UI()
        self.config = self._load_config()
        self.results = {}
        self.start_time = None
        self.args = args
        
        # Create results directory (at project root)
        self.results_dir = Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
    
    def run(self):
        """Main entry point"""
        # Banner
        self._show_banner()
        
        # Mode CLI ou interactif
        if self.args and (self.args.pattern or self.args.platforms):
            # Mode CLI
            self._run_cli_mode()
        else:
            # Mode interactif
            self._run_interactive_mode()
    
    def _run_cli_mode(self):
        """Run in CLI mode with arguments"""
        # Validate pattern
        if not self.args.pattern:
            self.ui.error("Pattern required", "Use --pattern <username>")
            sys.exit(1)
        
        username = self.args.pattern
        
        # Parse platforms
        if self.args.platforms.lower() == 'all':
            selected = list(self.PLATFORMS.keys())
            self.ui.info("Mode", "All platforms selected")
        else:
            selected = self._parse_platform_arg(self.args.platforms)
            if not selected:
                self.ui.error("Invalid platforms", "Use platform numbers (1-8) or names, separated by commas")
                sys.exit(1)
            
            names = [self.PLATFORMS[i]['name'] for i in selected]
            self.ui.info("Platforms", ', '.join(names))
        
        self.ui.info("Pattern", username)
        self.ui.space()
        
        # Configure usernames (same for all)
        usernames = {pid: username for pid in selected}
        
        # Estimate time
        self._estimate_time(selected)
        
        # Execute extractions
        self.start_time = datetime.now()
        self._run_extractions(selected, usernames)
        
        # Global summary
        self._show_summary()
    
    def _run_interactive_mode(self):
        """Run in interactive mode"""
        # Select platforms
        selected = self._select_platforms()
        
        # Configure usernames
        usernames = self._configure_usernames(selected)
        
        # Estimate time
        self._estimate_time(selected)
        
        # Execute extractions
        self.start_time = datetime.now()
        self._run_extractions(selected, usernames)
        
        # Global summary
        self._show_summary()
    
    def _parse_platform_arg(self, platforms_str: str) -> List[int]:
        """Parse platform argument (can be numbers or names)"""
        selected = []
        parts = [p.strip() for p in platforms_str.split(',')]
        
        for part in parts:
            # Try as number
            if part.isdigit():
                pid = int(part)
                if pid in self.PLATFORMS:
                    selected.append(pid)
            # Try as name
            elif part.lower() in self.PLATFORMS_BY_NAME:
                selected.append(self.PLATFORMS_BY_NAME[part.lower()])
        
        return selected
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML"""
        try:
            import yaml
            with open("config.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _show_banner(self):
        """Display welcome banner"""
        self.ui.header("MOSAIC - MULTI-PLATFORM OSINT EXTRACTOR", Icons.PROCESSING)
        
        with self.ui.indent():
            self.ui.muted("Version 2.0 - CLI Edition")
            self.ui.muted("Unified extraction system for 8 social platforms")
        
        self.ui.space()
    
    def _select_platforms(self) -> List[int]:
        """Platform selection with elegant UI (interactive mode)"""
        self.ui.section("Platform Selection")
        
        # Display platforms
        platform_list = []
        for num, info in sorted(self.PLATFORMS.items()):
            platform_list.append(f"{info['icon']} {info['name'].capitalize()}")
        
        self.ui.choice_list(platform_list)
        
        # Get user input
        with self.ui.indent():
            choice = input(self.ui._colorize(
                "→ Select platforms (e.g., 1,2,3 or Enter for all): ",
                Theme.PRIMARY
            )).strip()
        
        # Parse selection
        if not choice:
            selected = list(self.PLATFORMS.keys())
            self.ui.success("All platforms selected")
        else:
            try:
                selected = [int(x.strip()) for x in choice.split(',') if x.strip()]
                selected = [s for s in selected if s in self.PLATFORMS]
                
                if not selected:
                    self.ui.warning("Invalid selection, using all platforms")
                    selected = list(self.PLATFORMS.keys())
                else:
                    names = [self.PLATFORMS[i]['name'] for i in selected]
                    self.ui.success(f"Selected: {', '.join(names)}")
            except ValueError:
                self.ui.warning("Invalid input, using all platforms")
                selected = list(self.PLATFORMS.keys())
        
        self.ui.space()
        return selected
    
    def _configure_usernames(self, platforms: List[int]) -> Dict[int, str]:
        """Username configuration with elegant UI (interactive mode)"""
        self.ui.section("Username Configuration")
        
        with self.ui.indent():
            use_same = input(self.ui._colorize(
                "→ Use same username for all platforms? (y/n): ",
                Theme.PRIMARY
            )).strip().lower()
        
        usernames = {}
        
        if use_same in ['y', 'yes', 'o', 'oui', '']:
            with self.ui.indent():
                username = input(self.ui._colorize(
                    "→ Enter username: ",
                    Theme.PRIMARY
                )).strip()
            
            for platform_id in platforms:
                usernames[platform_id] = username
            
            self.ui.success(f"Username '{username}' configured for all platforms")
        else:
            self.ui.space()
            with self.ui.indent():
                for platform_id in platforms:
                    platform_name = self.PLATFORMS[platform_id]['name']
                    username = input(self.ui._colorize(
                        f"  → Username for {platform_name}: ",
                        Theme.MUTED
                    )).strip()
                    usernames[platform_id] = username
            
            self.ui.success("Custom usernames configured")
        
        self.ui.space()
        return usernames
    
    def _estimate_time(self, platforms: List[int]):
        """Time estimation"""
        avg_times = {
            "stackoverflow": 10, "youtube": 15, "github": 8,
            "bluesky": 12, "mastodon": 12, "reddit": 8,
            "medium": 5, "telegram": 20
        }
        
        total_seconds = sum(
            avg_times.get(self.PLATFORMS[p]['name'], 10)
            for p in platforms
        )
        
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        with self.ui.indent():
            self.ui.metric(
                "Estimated time",
                f"{minutes}m {seconds}s",
                Icons.TIME
            )
            self.ui.muted(f"For {len(platforms)} platform(s)")
        
        self.ui.space()
    
    def _run_extractions(self, platforms: List[int], usernames: Dict[int, str]):
        """Execute all extractions"""
        self.ui.separator()
        self.ui.space()
        
        total = len(platforms)
        
        for idx, platform_id in enumerate(platforms, 1):
            platform_info = self.PLATFORMS[platform_id]
            platform_name = platform_info['name']
            icon = platform_info['icon']
            extractor_class = platform_info['class']
            username = usernames[platform_id]
            
            # Platform header
            self.ui.header(
                f"{platform_name.upper()} ({idx}/{total})",
                icon
            )
            
            # Create extractor instance
            extractor = self._create_extractor(extractor_class, platform_name)
            
            if extractor:
                # Execute extraction
                try:
                    filename = extractor.run(username)
                    
                    if filename:
                        # Move to results directory
                        dest = self.results_dir / filename
                        shutil.move(filename, dest)
                        
                        self.results[platform_name] = {
                            "username": username,
                            "success": True,
                            "filename": str(dest)
                        }
                    else:
                        self.results[platform_name] = {
                            "username": username,
                            "success": False
                        }
                        
                except Exception as e:
                    self.ui.error("Extraction error", str(e))
                    self.results[platform_name] = {
                        "username": username,
                        "success": False
                    }
            else:
                self.results[platform_name] = {
                    "username": username,
                    "success": False
                }
            
            # Pause between platforms
            if idx < total:
                self.ui.space()
                self.ui.muted("Cooling down...")
                time.sleep(1)
                self.ui.space()
                self.ui.separator()
                self.ui.space()
    
    def _create_extractor(self, extractor_class, platform_name: str):
        """Create extractor instance with proper configuration"""
        try:
            if platform_name == "github":
                token = self.config.get('github', {}).get('token')
                return extractor_class(self.ui, token=token)
            
            elif platform_name == "stackoverflow":
                api_key = self.config.get('stackoverflow', {}).get('api_key')
                return extractor_class(self.ui, api_key=api_key)
            
            elif platform_name == "youtube":
                api_key = self.config.get('youtube', {}).get('api_key')
                return extractor_class(self.ui, api_key=api_key)
            
            elif platform_name == "mastodon":
                instance = self.config.get('mastodon', {}).get('instance', 'infosec.exchange')
                return extractor_class(self.ui, instance=instance)
            
            elif platform_name == "telegram":
                tg_config = self.config.get('telegram', {})
                return extractor_class(
                    self.ui,
                    api_id=tg_config.get('api_id'),
                    api_hash=tg_config.get('api_hash'),
                    phone=tg_config.get('phone'),
                    session_name=tg_config.get('session_name', 'telegram_session')
                )
            
            else:
                return extractor_class(self.ui)
                
        except Exception as e:
            self.ui.error("Failed to create extractor", str(e))
            return None
    
    def _show_summary(self):
        """Display global summary"""
        self.ui.space()
        self.ui.separator()
        self.ui.space()
        
        # Calculate duration
        if self.start_time:
            duration = datetime.now() - self.start_time
            minutes = duration.seconds // 60
            seconds = duration.seconds % 60
        else:
            minutes = seconds = 0
        
        # Header
        self.ui.header("GLOBAL SUMMARY", Icons.STATS)
        
        with self.ui.indent():
            # Duration
            self.ui.metric(
                "Total duration",
                f"{minutes}m {seconds}s",
                Icons.TIME
            )
            self.ui.space()
            
            # Results per platform
            self.ui.subsection("Platforms Processed")
            self.ui.space()
            
            success_count = 0
            for platform, data in self.results.items():
                icon = next(
                    (info['icon'] for info in self.PLATFORMS.values() if info['name'] == platform),
                    Icons.BULLET
                )
                
                platform_display = platform.capitalize()
                
                with self.ui.indent():
                    if data['success']:
                        status = self.ui._colorize("✓", Theme.SUCCESS)
                        success_count += 1
                    else:
                        status = self.ui._colorize("✗", Theme.ERROR)
                    
                    print(f"  {icon} {platform_display} {status}")
                    
                    with self.ui.indent():
                        self.ui.keyvalue("Username", data['username'])
                        if data.get('filename'):
                            self.ui.muted(f"→ {data['filename']}")
                    
                    self.ui.space()
            
            # Final status
            total_count = len(self.results)
            
            if success_count == total_count and total_count > 0:
                self.ui.success(
                    "All extractions completed successfully!",
                    f"{success_count}/{total_count} platforms"
                )
            elif success_count > 0:
                self.ui.warning(
                    "Partial success",
                    f"{success_count}/{total_count} platforms"
                )
            else:
                self.ui.error("All extractions failed")
        
        self.ui.space()
        self.ui.separator()
        self.ui.space()
        
        # Footer
        with self.ui.indent():
            self.ui.muted("All data saved to ./results/")
            self.ui.muted("Thank you for using Mosaic!")


# ============================================================================
# CLI ARGUMENT PARSER
# ============================================================================

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='mosaic',
        description='Mosaic - Multi-platform OSINT extraction tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Platform IDs:
  1. stackoverflow  2. youtube     3. github      4. bluesky
  5. mastodon       6. reddit      7. medium      8. telegram
        '''
    )
    
    parser.add_argument(
        '--pattern',
        type=str,
        help='Target username/pattern to search'
    )
    
    parser.add_argument(
        '--platforms',
        type=str,
        help='Platforms to extract from (comma-separated numbers/names or "all")'
    )
    
    return parser


def list_platforms():
    """Display available platforms"""
    ui = UI()
    ui.header("AVAILABLE PLATFORMS", Icons.INFO)
    ui.space()
    
    platforms = ExtractorOrchestrator.PLATFORMS
    
    with ui.indent():
        for pid, info in sorted(platforms.items()):
            name = info['name']
            icon = info['icon']
            ui.list_item(f"{icon} {pid}. {name}")
    
    ui.space()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        orchestrator = ExtractorOrchestrator(args=args)
        orchestrator.run()
    except KeyboardInterrupt:
        ui = UI()
        ui.space()
        ui.warning("Extraction cancelled by user")
        ui.space()
    except Exception as e:
        ui = UI()
        ui.space()
        ui.error("Fatal error", str(e))
        ui.space()
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
