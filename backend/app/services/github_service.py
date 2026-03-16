import os
import re
import base64
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging
import aiohttp
import time

logger = logging.getLogger(__name__)


@dataclass
class GitHubFile:
    name: str
    path: str
    type: str
    size: int
    download_url: Optional[str] = None
    content: Optional[str] = None


@dataclass
class GitHubRepo:
    owner: str
    name: str
    full_name: str
    default_branch: str
    description: Optional[str] = None


class GitHubAPIError(Exception):
    def __init__(self, status: int, message: str, retry_after: Optional[int] = None):
        self.status = status
        self.message = message
        self.retry_after = retry_after
        super().__init__(f"GitHub API Error {status}: {message}")


class GitHubService:
    MAX_RETRIES = 3
    BASE_RETRY_DELAY = 1.0
    MAX_RETRY_DELAY = 30.0
    RATE_LIMIT_DELAY = 60.0
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "OpenAssetGraph/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        self.timeout = aiohttp.ClientTimeout(total=120, connect=30)
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0
        self._min_request_interval = 0.1

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _rate_limit_wait(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()

    async def _make_request(
        self, 
        session: aiohttp.ClientSession, 
        method: str, 
        url: str, 
        **kwargs
    ) -> tuple[int, Any]:
        await self._rate_limit_wait()
        
        for attempt in range(self.MAX_RETRIES):
            try:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    if response.status == 403:
                        remaining = response.headers.get("X-RateLimit-Remaining", "1")
                        reset_time = response.headers.get("X-RateLimit-Reset")
                        
                        if remaining == "0" and reset_time:
                            wait_time = int(reset_time) - int(time.time()) + 5
                            wait_time = max(wait_time, 10)
                            logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                        
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            wait_time = int(retry_after)
                            logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    if response.status == 404:
                        return 404, None
                    
                    if response.status >= 500:
                        delay = min(self.BASE_RETRY_DELAY * (2 ** attempt), self.MAX_RETRY_DELAY)
                        logger.warning(f"Server error {response.status}. Retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                        await asyncio.sleep(delay)
                        continue
                    
                    try:
                        data = await response.json()
                    except:
                        data = None
                    
                    return response.status, data
                    
            except asyncio.TimeoutError:
                delay = min(self.BASE_RETRY_DELAY * (2 ** attempt), self.MAX_RETRY_DELAY)
                logger.warning(f"Request timeout. Retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                await asyncio.sleep(delay)
                continue
            except aiohttp.ClientError as e:
                delay = min(self.BASE_RETRY_DELAY * (2 ** attempt), self.MAX_RETRY_DELAY)
                logger.warning(f"Client error: {e}. Retrying in {delay}s (attempt {attempt + 1}/{self.MAX_RETRIES})")
                await asyncio.sleep(delay)
                continue
            except Exception as e:
                logger.error(f"Unexpected error during request: {e}")
                raise
        
        raise GitHubAPIError(500, f"Max retries ({self.MAX_RETRIES}) exceeded")

    def parse_repo_url(self, url: str) -> Optional[GitHubRepo]:
        patterns = [
            r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$",
            r"github\.com/([^/]+)/([^/]+)/?.*$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, name = match.groups()
                return GitHubRepo(
                    owner=owner,
                    name=name.rstrip("/"),
                    full_name=f"{owner}/{name.rstrip('/')}",
                    default_branch="main"
                )
        return None

    async def get_repo_info(self, owner: str, name: str) -> Optional[GitHubRepo]:
        url = f"{self.base_url}/repos/{owner}/{name}"
        
        try:
            session = await self._get_session()
            status, data = await self._make_request(session, "GET", url)
            
            if status == 200 and data:
                logger.info(f"Successfully fetched repo info for {owner}/{name}")
                return GitHubRepo(
                    owner=data["owner"]["login"],
                    name=data["name"],
                    full_name=data["full_name"],
                    default_branch=data.get("default_branch", "main"),
                    description=data.get("description")
                )
            elif status == 404:
                logger.error(f"Repository not found: {owner}/{name}")
                return None
            else:
                logger.error(f"GitHub API error: {status}")
                return None
                
        except GitHubAPIError as e:
            logger.error(f"Failed to get repo info: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting repo info: {e}")
            return None

    async def get_tree(
        self, 
        owner: str, 
        name: str, 
        branch: str = "main",
        recursive: bool = True
    ) -> List[GitHubFile]:
        try:
            session = await self._get_session()
            repo_info = await self._get_repo_info_with_session(session, owner, name)
            actual_branch = branch or (repo_info.default_branch if repo_info else "main")
            
            branch_url = f"{self.base_url}/repos/{owner}/{name}/branches/{actual_branch}"
            status, branch_data = await self._make_request(session, "GET", branch_url)
            
            if status != 200:
                fallback_branch = repo_info.default_branch if repo_info else "main"
                if fallback_branch != actual_branch:
                    logger.info(f"Branch {actual_branch} not found, trying {fallback_branch}")
                    branch_url = f"{self.base_url}/repos/{owner}/{name}/branches/{fallback_branch}"
                    status, branch_data = await self._make_request(session, "GET", branch_url)
                    
                if status != 200:
                    logger.error(f"Failed to get branch info for {actual_branch}")
                    return []
            
            if not branch_data:
                logger.error(f"No branch data returned")
                return []
                
            commit_sha = branch_data.get("commit", {}).get("sha", "")
            
            if not commit_sha:
                logger.error(f"No commit SHA found for branch {actual_branch}")
                return []
            
            tree_url = f"{self.base_url}/repos/{owner}/{name}/git/trees/{commit_sha}"
            if recursive:
                tree_url += "?recursive=1"
            
            status, tree_data = await self._make_request(session, "GET", tree_url)
            
            if status == 200 and tree_data:
                files = []
                for item in tree_data.get("tree", []):
                    files.append(GitHubFile(
                        name=item["path"].split("/")[-1],
                        path=item["path"],
                        type=item["type"],
                        size=item.get("size", 0)
                    ))
                logger.info(f"Retrieved {len(files)} files from {owner}/{name}")
                return files
            else:
                logger.error(f"Failed to get tree: {status}")
                return []
                
        except GitHubAPIError as e:
            logger.error(f"API error while getting tree: {e}")
            return []
        except asyncio.TimeoutError:
            logger.error(f"Timeout while getting tree for {owner}/{name}")
            return []
        except Exception as e:
            logger.error(f"Failed to get tree: {e}")
            return []
    
    async def _get_repo_info_with_session(self, session: aiohttp.ClientSession, owner: str, name: str) -> Optional[GitHubRepo]:
        url = f"{self.base_url}/repos/{owner}/{name}"
        try:
            status, data = await self._make_request(session, "GET", url)
            if status == 200 and data:
                return GitHubRepo(
                    owner=data["owner"]["login"],
                    name=data["name"],
                    full_name=data["full_name"],
                    default_branch=data.get("default_branch", "main"),
                    description=data.get("description")
                )
            return None
        except Exception as e:
            logger.error(f"Failed to get repo info: {e}")
            return None

    async def get_file_content(
        self, 
        owner: str, 
        name: str, 
        path: str,
        branch: str = "main"
    ) -> Optional[str]:
        url = f"{self.base_url}/repos/{owner}/{name}/contents/{path}"
        if branch:
            url += f"?ref={branch}"
        
        try:
            session = await self._get_session()
            status, data = await self._make_request(session, "GET", url)
            
            if status == 200 and data:
                if isinstance(data, list):
                    return None
                    
                if data.get("encoding") == "base64":
                    try:
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        return content
                    except Exception as e:
                        logger.warning(f"Failed to decode base64 content for {path}: {e}")
                        return None
                return data.get("content")
            else:
                logger.debug(f"File not found: {path}")
                return None
                
        except GitHubAPIError as e:
            logger.error(f"Failed to get file content: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to get file content for {path}: {e}")
            return None

    async def get_multiple_files(
        self,
        owner: str,
        name: str,
        paths: List[str],
        branch: str = "main",
        batch_size: int = 5
    ) -> Dict[str, str]:
        results = {}
        
        for i in range(0, len(paths), batch_size):
            batch = paths[i:i + batch_size]
            tasks = [
                self.get_file_content(owner, name, path, branch)
                for path in batch
            ]
            
            try:
                contents = await asyncio.gather(*tasks, return_exceptions=True)
                
                for path, content in zip(batch, contents):
                    if isinstance(content, Exception):
                        logger.warning(f"Error fetching {path}: {content}")
                    elif content:
                        results[path] = content
                        
                if i + batch_size < len(paths):
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Error in batch file fetch: {e}")
        
        logger.info(f"Retrieved {len(results)}/{len(paths)} files")
        return results

    def find_key_files(self, files: List[GitHubFile]) -> Dict[str, List[str]]:
        key_files = {
            "dependencies": [],
            "infrastructure": [],
            "source": [],
            "config": [],
        }
        
        dependency_patterns = [
            "package.json", "requirements.txt", "pyproject.toml", "setup.py",
            "pom.xml", "build.gradle", "build.gradle.kts", "go.mod",
            "Cargo.toml", "composer.json", "Gemfile"
        ]
        
        infra_patterns = [
            "docker-compose.yml", "docker-compose.yaml", "Dockerfile",
            "Chart.yaml", "values.yaml", ".gitlab-ci.yml",
            "Jenkinsfile"
        ]
        
        config_patterns = [
            ".env.example", "config.yaml", "config.yml", "settings.py",
            "application.yml", "application.properties"
        ]
        
        for f in files:
            if f.type != "blob":
                continue
            
            for pattern in dependency_patterns:
                if pattern.startswith("*"):
                    if f.name.endswith(pattern[1:]):
                        key_files["dependencies"].append(f.path)
                        break
                elif f.name == pattern:
                    key_files["dependencies"].append(f.path)
                    break
            
            for pattern in infra_patterns:
                if pattern.startswith("*"):
                    if f.name.endswith(pattern[1:]):
                        key_files["infrastructure"].append(f.path)
                        break
                elif f.name == pattern or f.path.endswith(pattern):
                    key_files["infrastructure"].append(f.path)
                    break
            
            for pattern in config_patterns:
                if f.name == pattern or f.path.endswith(pattern):
                    key_files["config"].append(f.path)
                    break
            
            if f.path.startswith(".github/workflows/") and f.name.endswith(".yml"):
                key_files["infrastructure"].append(f.path)
            
            if f.name.endswith((".py", ".js", ".ts", ".java", ".go", ".rs", ".php", ".rb", ".cs", ".f90", ".F90", ".f95", ".F95", ".f03", ".F03", ".f08", ".F08")):
                key_files["source"].append(f.path)
        
        return key_files
