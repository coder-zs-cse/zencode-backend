from typing import Optional
import re
import requests
import base64

class FetchComponentsService:
    def __init__(self, repo_link: Optional[str] = None, access_token: Optional[str] = None):
        self.repo_link = repo_link
        self.access_token = access_token
        if not self.repo_link:
            raise ValueError("GitHub Repository link is required")
        
        # Extract owner and repo from the link
        parts = self.repo_link.rstrip('/').split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repository link")
        self.owner = parts[-2]
        self.repo = parts[-1]

        # Set up headers with authentication if token is provided
        self.headers = {}
        if self.access_token:
            self.headers['Authorization'] = f'token {self.access_token}'

    def fetch_directory_contents(self, path: str = "") -> list:
        """Recursively fetch contents of a directory."""
        try:
            # GitHub API endpoint for repository contents
            api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            fetchedComponents = []
            
            for item in response.json():
                if item['type'] == 'file':
                    # Get file content
                    content_response = requests.get(item['download_url'], headers=self.headers)
                    content_response.raise_for_status()
                    
                    fetchedComponents.append({
                        'file': item['name'],
                        'fileContent': content_response.text,
                        'path': item['path']
                    })
                elif item['type'] == 'dir':
                    # Recursively fetch contents of subdirectories
                    subdir_contents = self.fetch_directory_contents(item['path'])
                    fetchedComponents.extend(subdir_contents)
            
            return fetchedComponents
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching contents for path {path}:", str(e))
            raise
        except Exception as e:
            print(f"Caught Exception for path {path}:", str(e))
            raise

    def extract_components(self):
        """Main method to extract all components from the repository."""
        try:
            return self.fetch_directory_contents()
        except Exception as e:
            print("Error in extract_components:", str(e))
            raise



