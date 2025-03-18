from gitingest import ingest
from typing import Optional
import re

class FetchComponentsService:
    def __init__(self,repo_link: Optional[str] = None):
        self.repo_link = repo_link
        if not self.repo_link:
            raise ValueError("GitHub Repository link is required")


    def extract_components(self):
        try:
            summary, tree, content = ingest(self.repo_link)
            sections = re.split(r'={48}', content)
            fetchedComponents = []
            j = 0

            for i in range(1, len(sections), 2):
                path = sections[i].strip().split(': ')[1]
                file_content = sections[i + 1].strip()
                fetchedComponents.append({'file': path.split("/")[-1],'fileContent':file_content,'path':path})
                j = j + 1
            return fetchedComponents
        except Exception as e:
            print("Caught Exception:",e)
        raise


