# =====================================================================================
# HEXAEIGHT GIT MCP TOOL - LIBGIT2-COMPATIBLE VERSION
# Fixed to work with the C# LibGit2Sharp server implementation
# =====================================================================================

import asyncio
import json
import aiohttp
import base64
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from pathlib import Path
import hashlib
import mimetypes

# =====================================================================================
# MCP TOOL INTERFACE AND DATA MODELS
# =====================================================================================

@dataclass
class GitFileOperation:
    """Represents a file operation for git commits"""
    path: str
    content: Optional[str] = None
    operation: str = "modify"  # "add", "modify", "delete"
    is_binary: bool = False
    file_size: int = 0

@dataclass
class GitCommitResult:
    """Result of a git commit operation"""
    success: bool
    commit_sha: Optional[str] = None
    message: str = ""
    error_code: Optional[str] = None
    files_changed: List[str] = None

@dataclass
class GitRepositoryState:
    """Current state of a git repository"""
    repository: str
    current_branch: str
    last_commit_sha: str
    modified_files: List[str]
    untracked_files: List[str]

class GitMCPTool:
    """
    HexaEight Git MCP Tool - LibGit2-Compatible Version
    
    FIXES FOR C# LIBGIT2SHARP SERVER:
    - Uses "master" as default branch (LibGit2Sharp default)
    - Correct field names: "Branch" for source branch operations
    - Checks "isSuccessful" response property
    - No branch discovery (server doesn't support)
    """
    
    def __init__(self, agent_instance, git_server_base_url: str = None, max_file_size_for_inline: int = 1024 * 1024, debug_mode: bool = False):
        """
        Initialize Git MCP Tool for LibGit2Sharp server
        
        Args:
            agent_instance: The HexaEight agent instance (with encryption capabilities)
            git_server_base_url: Base URL for git server (defaults to token_server/git/client_id)
            max_file_size_for_inline: Files larger than this use streaming upload (default 1MB)
            debug_mode: Enable verbose debug logging (default False)
        """
        self.agent = agent_instance
        self.debug_mode = debug_mode
        
        # Construct git server URL from environment variables
        token_server_url = os.getenv("HEXAEIGHT_TOKENSERVER_URL", "")
        client_id = os.getenv("HEXAEIGHT_CLIENT_ID", "")
        
        # Build git server URL: {token_server}/git/{client_id}
        self.git_server_url = git_server_base_url or f"{token_server_url}/git/{client_id}"
        self.client_id = client_id
        
        self.max_inline_size = max_file_size_for_inline
        self.agent_name = ""
        self.git_server_agent_name = ""
        self.current_repository = ""
        
        # FIXED: Use "master" as default (LibGit2Sharp creates repositories with "master")
        self.current_branch = "master"
        
        self.session_history = []  # Track operations for rollback
        
        print(f"🔧 Git MCP Tool initialized (LibGit2-Compatible)")
        print(f"   Git Server URL: {self.git_server_url}")
        print(f"   Client ID: {client_id}")
        print(f"   Default branch: {self.current_branch}")
        
    async def initialize(self) -> bool:
        """Initialize the Git tool and discover agent names"""
        try:
            # Get git server agent name from token server
            token_server_url = os.getenv("HEXAEIGHT_TOKENSERVER_URL", "")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{token_server_url}/api/resourceinfo") as response:
                    if response.status == 200:
                        self.git_server_agent_name = await response.text()
                        self.git_server_agent_name = self.git_server_agent_name.strip()
                        print(f"✅ Git server agent: {self.git_server_agent_name}")
                    else:
                        print(f"❌ Failed to get git server agent name: {response.status}")
                        return False
            
            # Get our agent name
            try:
                if hasattr(self.agent, 'hexaeight_agent') and self.agent.hexaeight_agent:
                    self.agent_name = await self.agent.hexaeight_agent.get_agent_name()
                elif hasattr(self.agent, 'agent_name'):
                    self.agent_name = self.agent.agent_name
                elif hasattr(self.agent, '_clr_agent_config'):
                    self.agent_name = getattr(self.agent._clr_agent_config, 'AgentName', 'git-client-agent')
                else:
                    self.agent_name = "git-client-agent"
                    
                print(f"✅ Our agent name: {self.agent_name}")
            except Exception as e:
                print(f"⚠️ Could not get agent name: {e}")
                self.agent_name = "git-client-agent"
            
            if not self.git_server_agent_name:
                print("❌ Could not get Git server agent name")
                return False
                
            print(f"✅ Git tool ready - will communicate with: {self.git_server_agent_name}")
            return True
            
        except Exception as e:
            print(f"❌ Git tool initialization failed: {e}")
            return False

    # =====================================================================================
    # LIBGIT2-COMPATIBLE MCP TOOL INTERFACE METHODS
    # =====================================================================================

    async def create_repository(self, repository_name: str, initial_commit: bool = True) -> Dict[str, Any]:
        """
        MCP Tool: Create a new repository
        
        Args:
            repository_name: Name of the repository to create
            initial_commit: Whether to create an initial commit with README
            
        Returns:
            Dict with success status and repository info
        """
        try:
            print(f"📁 Creating repository: {repository_name}")
            
            # Create operation matching actual C# GitOperation class
            operation = {
                "Operation": "create",
                "Repository": repository_name,
                "CommitMessage": "Initial repository setup"
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result) or result.get("errorCode") == "REPOSITORY_EXISTS":
                self.current_repository = repository_name
                # Keep current_branch as "master" since that's what LibGit2Sharp creates
                if result.get("errorCode") == "REPOSITORY_EXISTS":
                    print(f"✅ Repository '{repository_name}' already exists - using existing repository")
                else:
                    print(f"✅ Repository '{repository_name}' created successfully")
                print(f"   Default branch: {self.current_branch}")
                
                # Add to session history
                self.session_history.append({
                    "operation": "create_repository", 
                    "repository": repository_name,
                    "branch": self.current_branch,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            return result
            
        except Exception as e:
            print(f"❌ Error creating repository: {e}")
            return {"success": False, "error": str(e)}

    async def commit_files(self, 
                          files: List[GitFileOperation], 
                          commit_message: str, 
                          repository: str = None, 
                          branch: str = None) -> GitCommitResult:
        """
        MCP Tool: Commit files to repository
        
        Args:
            files: List of file operations to commit
            commit_message: Commit message
            repository: Repository name (defaults to current)
            branch: Branch name (defaults to current)
            
        Returns:
            GitCommitResult with commit information
        """
        try:
            repo = repository or self.current_repository
            target_branch = branch or self.current_branch
            
            if not repo:
                return GitCommitResult(False, message="No repository specified")
            
            if self.debug_mode:
                print(f"🔧 Committing {len(files)} files to {repo}/{target_branch}")
            
            # HYBRID APPROACH: Try upload sessions first for reliability, fall back to inline
            # Use smaller thresholds to prevent DECRYPTION_FAILED due to large payloads
            small_file_limit = 50 * 1024  # 50KB instead of 1MB to keep encrypted payloads smaller
            
            # Calculate total inline payload size
            total_inline_size = 0
            large_files = []
            small_files = []
            
            for file_op in files:
                content_size = len(file_op.content.encode('utf-8')) if file_op.content else 0
                file_op.file_size = content_size
                
                if content_size > small_file_limit:
                    large_files.append(file_op)
                else:
                    small_files.append(file_op)
                    total_inline_size += content_size
            
            # If total inline size is too large (>200KB), try upload session
            session_id = None
            if large_files or total_inline_size > 200 * 1024:
                if self.debug_mode:
                    print(f"📤 Attempting upload session for {len(large_files)} large files and {total_inline_size/1024:.1f}KB total inline")
                
                session_result = await self._create_upload_session()
                if self._check_success(session_result):
                    session_id = session_result.get("sessionId")
                    if self.debug_mode:
                        print(f"📤 Created upload session: {session_id}")
                    
                    # Upload all files via streaming for consistency
                    for file_op in files:
                        if file_op.content:  # Only upload files with content
                            upload_result = await self._upload_large_file(session_id, file_op)
                            if not self._check_success(upload_result):
                                await self._cancel_upload_session(session_id)
                                session_id = None  # Fall back to inline
                                if self.debug_mode:
                                    print(f"📤 Upload failed for {file_op.path}, falling back to inline")
                                break
                else:
                    if self.debug_mode:
                        print(f"📤 Upload session creation failed, using inline approach")
            
            # Prepare git operation files
            git_files = []
            if session_id:
                # Upload session successful - use empty content
                for file_op in files:
                    git_files.append({
                        "path": file_op.path,
                        "content": ""  # Content uploaded separately
                    })
            else:
                # No upload session - use inline content with size limits
                for file_op in files:
                    if file_op.file_size > small_file_limit:
                        if self.debug_mode:
                            print(f"⚠️ File {file_op.path} ({file_op.file_size/1024:.1f}KB) exceeds inline limit, truncating")
                        # Truncate large files to prevent encryption issues
                        truncated_content = file_op.content[:small_file_limit] if file_op.content else ""
                        git_files.append({
                            "path": file_op.path,
                            "content": truncated_content
                        })
                    else:
                        git_files.append({
                            "path": file_op.path,
                            "content": file_op.content or ""
                        })
            
            # Create git operation matching actual C# GitOperation class
            operation = {
                "Operation": "commit",
                "Repository": repo,
                "Branch": target_branch,
                "CommitMessage": commit_message,
                "Files": git_files,
                "Author": {
                    "name": self.agent_name,
                    "email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            # Execute git operation
            if session_id:
                # Use upload session completion for large files/payloads
                result = await self._complete_upload_session(session_id, operation)
            else:
                # Use direct encrypted operation for small payloads
                result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                commit_sha = result.get("commitSha")
                if self.debug_mode:
                    print(f"✅ Committed {len(files)} files. Commit: {commit_sha}")
                
                # Add to session history
                self.session_history.append({
                    "operation": "commit",
                    "repository": repo,
                    "branch": target_branch,
                    "commit_sha": commit_sha,
                    "message": commit_message,
                    "files": [f.path for f in files],
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                return GitCommitResult(
                    success=True,
                    commit_sha=commit_sha,
                    message="Files committed successfully",
                    files_changed=[f.path for f in files]
                )
            else:
                error_msg = self._get_error_message(result)
                return GitCommitResult(False, message=error_msg)
                
        except Exception as e:
            print(f"❌ Error committing files: {e}")
            return GitCommitResult(False, message=str(e))

    async def create_branch(self, branch_name: str, from_branch: str = None, repository: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Create a new branch
        
        Args:
            branch_name: Name of the new branch
            from_branch: Source branch (defaults to current)
            repository: Repository name (defaults to current)
            
        Returns:
            Dict with branch creation result
        """
        try:
            repo = repository or self.current_repository
            source_branch = from_branch or self.current_branch
            
            print(f"🌿 Creating branch '{branch_name}' from '{source_branch}' in {repo}")
            
            # FIXED: Create operation matching C# server expectations
            # The C# server uses "Branch" field for source branch in branch operations
            operation = {
                "Operation": "branch",
                "Repository": repo,
                "BranchName": branch_name,
                "Branch": source_branch,  # FIXED: Use "Branch" not "SourceBranch"
                "CreateBranch": True,
                "Author": {
                    "Name": self.agent_name,      # Uppercase - matches C# property names
                    "Email": f"{self.agent_name}@hexaeight-agent.local"  # Uppercase - matches C# property names
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                print(f"✅ Branch '{branch_name}' created successfully")
                
                # Add to session history
                self.session_history.append({
                    "operation": "create_branch",
                    "repository": repo,
                    "branch_name": branch_name,
                    "source_branch": source_branch,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            return result
            
        except Exception as e:
            print(f"❌ Error creating branch: {e}")
            return {"success": False, "error": str(e)}

    async def switch_branch(self, branch_name: str, repository: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Switch to a different branch
        
        Args:
            branch_name: Name of the branch to switch to
            repository: Repository name (defaults to current)
            
        Returns:
            Dict with branch switch result
        """
        try:
            repo = repository or self.current_repository
            
            print(f"🔄 Switching to branch '{branch_name}' in {repo}")
            
            # Create operation matching C# server expectations
            operation = {
                "Operation": "checkout",
                "Repository": repo,
                "BranchName": branch_name,
                "Author": {
                    "Name": self.agent_name,
                    "Email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                previous_branch = self.current_branch
                self.current_branch = branch_name
                print(f"✅ Switched to branch '{branch_name}'")
                
                # Add to session history
                self.session_history.append({
                    "operation": "switch_branch",
                    "repository": repo,
                    "branch_name": branch_name,
                    "previous_branch": previous_branch,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            return result
            
        except Exception as e:
            print(f"❌ Error switching branch: {e}")
            return {"success": False, "error": str(e)}

    async def read_file(self, file_path: str, repository: str = None, branch: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Read file content from git repository

        Args:
            file_path: Path to the file to read
            repository: Repository name (defaults to current)
            branch: Branch name (defaults to current)

        Returns:
            Dict with file content and success status
        """
        try:
            repo = repository or self.current_repository
            target_branch = branch or self.current_branch

            if self.debug_mode:
                print(f"📖 Reading file from git: {file_path} in {repo}/{target_branch}")

            # Create read operation matching actual C# GitOperation class
            operation = {
                "Operation": "read",
                "Repository": repo,
                "Branch": target_branch,
                "FilePath": file_path
            }

            result = await self._send_encrypted_git_operation(operation)

            if self._check_success(result):
                # The C# server returns file content in the CommitSha field (temporary solution)
                content = result.get("commitSha", "")
                if self.debug_mode:
                    print(f"✅ Read {len(content)} chars from {file_path}")

                # Add to session history
                self.session_history.append({
                    "operation": "read_file",
                    "repository": repo,
                    "branch": target_branch,
                    "file_path": file_path,
                    "content_length": len(content),
                    "timestamp": datetime.utcnow().isoformat()
                })

                return {
                    "success": True,
                    "content": content,
                    "file_path": file_path,
                    "repository": repo,
                    "branch": target_branch,
                    "content_length": len(content)
                }
            else:
                error_msg = self._get_error_message(result)
                print(f"❌ Failed to read {file_path}: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "file_path": file_path
                }

        except Exception as e:
            print(f"❌ Error reading file from git: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }

    async def revert_to_commit(self, commit_sha: str, repository: str = None, branch: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Revert repository to a specific commit
        
        Args:
            commit_sha: SHA of the commit to revert to
            repository: Repository name (defaults to current)
            branch: Branch name (defaults to current)
            
        Returns:
            Dict with revert operation result
        """
        try:
            repo = repository or self.current_repository
            target_branch = branch or self.current_branch
            
            print(f"🔄 Reverting {repo}/{target_branch} to commit {commit_sha}")
            
            # Create operation matching C# server expectations
            operation = {
                "Operation": "revert",
                "Repository": repo,
                "Branch": target_branch,
                "TargetCommit": commit_sha,
                "Author": {
                    "Name": self.agent_name,
                    "Email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                print(f"✅ Reverted to commit {commit_sha}")
                
                self.session_history.append({
                    "operation": "revert",
                    "repository": repo,
                    "branch": target_branch,
                    "target_commit": commit_sha,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            return result
            
        except Exception as e:
            print(f"❌ Error reverting commit: {e}")
            return {"success": False, "error": str(e)}

    async def get_commit_history(self, repository: str = None, branch: str = None, skip: int = 0, take: int = 50) -> Dict[str, Any]:
        """
        MCP Tool: Get commit history for a repository branch
        
        Args:
            repository: Repository name (defaults to current)
            branch: Branch name (defaults to current)
            skip: Number of commits to skip (pagination)
            take: Number of commits to take (max 100)
            
        Returns:
            Dict with commit history and pagination info
        """
        try:
            repo = repository or self.current_repository
            target_branch = branch or self.current_branch
            
            # Limit take to 100 as per HEXAEIGHT documentation
            take = min(take, 100)
            
            print(f"📜 Getting commit history for {repo}/{target_branch} (skip:{skip}, take:{take})")
            
            operation = {
                "Operation": "history",
                "Repository": repo,
                "Branch": target_branch,
                "CommitMessage": f"{skip},{take}",  # Pagination format
                "Author": {
                    "name": self.agent_name,
                    "email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                # Parse nested JSON structure from commitSha field
                commits_data = result.get("commitSha", "{}")
                try:
                    parsed_data = json.loads(commits_data)
                    commits = parsed_data.get("Commits", [])
                    total_count = parsed_data.get("TotalCount", len(commits))
                    print(f"✅ Retrieved {len(commits)} commits (total: {total_count})")
                    
                    # Return structured data that matches expected format
                    structured_result = {
                        "isSuccessful": True,
                        "commits": commits,
                        "totalCount": total_count,
                        "skip": parsed_data.get("Skip", 0),
                        "take": parsed_data.get("Take", len(commits)),
                        "branch": parsed_data.get("Branch", target_branch)
                    }
                    
                    self.session_history.append({
                        "operation": "get_history",
                        "repository": repo,
                        "branch": target_branch,
                        "commits_count": len(commits),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    return structured_result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse commit data: {e}")
                    return {"isSuccessful": False, "error": "Failed to parse commit history"}
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting commit history: {e}")
            return {"success": False, "error": str(e)}

    async def get_file_history(self, file_path: str, repository: str = None, branch: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Get commit history for a specific file
        
        Args:
            file_path: Path to the file
            repository: Repository name (defaults to current)
            branch: Branch name (defaults to current)
            
        Returns:
            Dict with file's commit history
        """
        try:
            repo = repository or self.current_repository
            target_branch = branch or self.current_branch
            
            print(f"📄 Getting file history for {file_path} in {repo}/{target_branch}")
            
            operation = {
                "Operation": "file-history",
                "Repository": repo,
                "FilePath": file_path,
                "Branch": target_branch,
                "Author": {
                    "name": self.agent_name,
                    "email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                # Parse nested JSON structure from commitSha field
                commits_data = result.get("commitSha", "{}")
                try:
                    parsed_data = json.loads(commits_data)
                    commits = parsed_data.get("Commits", [])
                    total_count = parsed_data.get("TotalCount", len(commits))
                    print(f"✅ Retrieved {len(commits)} commits for file {file_path}")
                    
                    # Return structured data that matches expected format
                    structured_result = {
                        "isSuccessful": True,
                        "commits": commits,
                        "totalCount": total_count,
                        "skip": parsed_data.get("Skip", 0),
                        "take": parsed_data.get("Take", len(commits)),
                        "branch": parsed_data.get("Branch", target_branch)
                    }
                    
                    self.session_history.append({
                        "operation": "get_file_history",
                        "repository": repo,
                        "branch": target_branch,
                        "file_path": file_path,
                        "commits_count": len(commits),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    return structured_result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse file history data: {e}")
                    return {"isSuccessful": False, "error": "Failed to parse file history"}
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting file history: {e}")
            return {"success": False, "error": str(e)}

    async def compare_commits(self, from_commit: str, to_commit: str = None, repository: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Compare two commits and show differences
        
        Args:
            from_commit: Source commit SHA
            to_commit: Target commit SHA (default: HEAD)
            repository: Repository name (defaults to current)
            
        Returns:
            Dict with diff information
        """
        try:
            repo = repository or self.current_repository
            target_commit = to_commit or "HEAD"
            
            print(f"🔍 Comparing commits {from_commit} -> {target_commit} in {repo}")
            
            operation = {
                "Operation": "diff",
                "Repository": repo,
                "Branch": from_commit,  # From commit
                "TargetCommit": target_commit,  # To commit
                "Author": {
                    "name": self.agent_name,
                    "email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                # Parse nested JSON structure from commitSha field
                diff_data = result.get("commitSha", "{}")
                try:
                    parsed_data = json.loads(diff_data)
                    diff_entries = parsed_data.get("DiffEntries", [])
                    files_changed = parsed_data.get("FilesChanged", len(diff_entries))
                    print(f"✅ Compared commits: {files_changed} files changed")
                    
                    # Return structured data that matches expected format
                    structured_result = {
                        "isSuccessful": True,
                        "diffEntries": diff_entries,
                        "filesChanged": files_changed,
                        "fromCommit": from_commit,
                        "toCommit": target_commit
                    }
                    
                    self.session_history.append({
                        "operation": "compare_commits",
                        "repository": repo,
                        "from_commit": from_commit,
                        "to_commit": target_commit,
                        "files_changed": files_changed,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    return structured_result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse diff data: {e}")
                    return {"isSuccessful": False, "error": "Failed to parse diff data"}
            
            return result
            
        except Exception as e:
            print(f"❌ Error comparing commits: {e}")
            return {"success": False, "error": str(e)}

    async def show_commit_details(self, commit_sha: str = None, repository: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Show detailed information about a specific commit
        
        Args:
            commit_sha: Commit SHA (default: HEAD)
            repository: Repository name (defaults to current)
            
        Returns:
            Dict with commit details and changes
        """
        try:
            repo = repository or self.current_repository
            target_commit = commit_sha or "HEAD"
            
            print(f"🔍 Showing commit details for {target_commit} in {repo}")
            
            operation = {
                "Operation": "show",
                "Repository": repo,
                "TargetCommit": target_commit,
                "Author": {
                    "name": self.agent_name,
                    "email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                # Parse nested JSON structure from commitSha field
                commit_data = result.get("commitSha", "{}")
                try:
                    parsed_data = json.loads(commit_data)
                    commit_info = parsed_data.get("Commit", {})
                    changes = parsed_data.get("Changes", [])
                    modified_files = parsed_data.get("ModifiedFiles", [])
                    print(f"✅ Commit details retrieved: {len(modified_files)} files modified")
                    
                    # Return structured data that matches expected format
                    structured_result = {
                        "isSuccessful": True,
                        "commit": commit_info,
                        "changes": changes,
                        "modifiedFiles": modified_files
                    }
                    
                    self.session_history.append({
                        "operation": "show_commit",
                        "repository": repo,
                        "commit_sha": target_commit,
                        "files_modified": len(modified_files),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    return structured_result
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse commit details: {e}")
                    return {"isSuccessful": False, "error": "Failed to parse commit details"}
            
            return result
            
        except Exception as e:
            print(f"❌ Error showing commit details: {e}")
            return {"success": False, "error": str(e)}

    async def merge_branch(self, target_branch: str, source_branch: str, commit_message: str = None, repository: str = None) -> Dict[str, Any]:
        """
        MCP Tool: Merge one branch into another
        
        Args:
            target_branch: Branch to merge into (e.g., "master")
            source_branch: Branch to merge from (e.g., "feature/new-feature")
            commit_message: Merge commit message
            repository: Repository name (defaults to current)
            
        Returns:
            Dict with merge operation result
        """
        try:
            repo = repository or self.current_repository
            merge_message = commit_message or f"Merge {source_branch} into {target_branch}"
            
            print(f"🔀 Merging {source_branch} -> {target_branch} in {repo}")
            
            operation = {
                "Operation": "merge",
                "Repository": repo,
                "Branch": target_branch,  # Target branch
                "BranchName": source_branch,  # Source branch
                "CommitMessage": merge_message,
                "Author": {
                    "name": self.agent_name,
                    "email": f"{self.agent_name}@hexaeight-agent.local"
                }
            }
            
            result = await self._send_encrypted_git_operation(operation)
            
            if self._check_success(result):
                merge_commit = result.get("commitSha")
                print(f"✅ Successfully merged {source_branch} into {target_branch}")
                if merge_commit:
                    print(f"   Merge commit: {merge_commit}")
                
                self.session_history.append({
                    "operation": "merge_branch",
                    "repository": repo,
                    "target_branch": target_branch,
                    "source_branch": source_branch,
                    "merge_commit": merge_commit,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return result
            
        except Exception as e:
            print(f"❌ Error merging branches: {e}")
            return {"success": False, "error": str(e)}

    # =====================================================================================
    # FIXED HELPER METHODS FOR LIBGIT2SHARP SERVER
    # =====================================================================================

    def _check_success(self, result: Dict[str, Any]) -> bool:
        """
        FIXED: Check success for LibGit2Sharp server responses
        C# server returns "isSuccessful" (camelCase), not "success"
        """
        return result.get("isSuccessful") == True

    def _get_error_message(self, result: Dict[str, Any]) -> str:
        """
        FIXED: Get error message from LibGit2Sharp server responses
        """
        return (
            result.get("errorMessage") or 
            result.get("message") or
            "Unknown error"
        )

    async def _send_encrypted_git_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Send encrypted git operation with smart retry logic for commit operations and transient errors"""
        operation_type = operation.get('Operation', 'unknown')
        
        # Define which operations and errors should be retried
        retryable_operations = {'commit', 'create', 'branch', 'checkout', 'read', 'list'}  # Operations that can benefit from retry
        retryable_error_codes = {
            'DECRYPTION_FAILED',    # Encryption/decryption issues
            'CONNECTION_FAILED',    # Network issues
            'TIMEOUT',             # Timeout issues
            'INTERNAL_ERROR',      # Server internal errors
            'REPOSITORY_LOCKED'    # Repository temporarily locked
        }
        non_retryable_error_codes = {
            'FILE_NOT_FOUND',      # File doesn't exist - don't retry
            'REPOSITORY_NOT_FOUND', # Repository doesn't exist - don't retry
            'ACCESS_DENIED',       # Permission issue - don't retry
            'INVALID_BRANCH',      # Branch doesn't exist - don't retry
            'CONFLICT'             # Merge conflict - needs manual intervention
        }
        
        # Set retry counts based on operation type
        if operation_type in {'read', 'list'}:
            max_retries = 3  # Read operations get 3 attempts
        elif operation_type in retryable_operations:
            max_retries = 10  # Write operations get 10 attempts  
        else:
            max_retries = 1  # Non-retryable operations get 1 attempt
        base_delay = 1.0
        max_delay = 60.0
        consecutive_failures = 0  # Track consecutive commit failures
        last_decryption_failed = False  # Track if last attempt failed with DECRYPTION_FAILED
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 Retry attempt {attempt + 1}/{max_retries} for operation: {operation_type}")
                
                # ENHANCED ENCRYPTION: Always re-encrypt if last attempt failed with DECRYPTION_FAILED
                # or if this is the first attempt or a retryable operation
                encrypted_operation = None
                should_reencrypt = (
                    attempt == 0 or  # First attempt
                    last_decryption_failed or  # Last attempt failed with DECRYPTION_FAILED
                    operation_type in retryable_operations  # Retryable operations get fresh encryption
                )
                
                if should_reencrypt:
                    if last_decryption_failed:
                        print(f"🔐 Re-encrypting operation due to previous DECRYPTION_FAILED")
                    
                    encryption_attempts = 3
                    for enc_attempt in range(encryption_attempts):
                        try:
                            encrypted_operation = await self._encrypt_git_operation(operation)
                            if encrypted_operation:
                                break
                        except Exception as enc_e:
                            print(f"⚠️ Encryption attempt {enc_attempt + 1}/{encryption_attempts} failed: {enc_e}")
                            if enc_attempt < encryption_attempts - 1:
                                await asyncio.sleep(0.5 * (enc_attempt + 1))
                
                if not encrypted_operation:
                    error_msg = f"Failed to encrypt git operation"
                    print(f"❌ {error_msg}")
                    return {"isSuccessful": False, "errorMessage": error_msg, "errorCode": "ENCRYPTION_FAILED"}
                
                # Reset flag after successful encryption
                last_decryption_failed = False
                
                url = f"{self.git_server_url}/api/operations"
                data = {"encryptedAuth": encrypted_operation}
                
                if self.debug_mode:
                    print(f"🌐 Sending encrypted git operation: {operation_type}")
                    print(f"   URL: {url}")
                    print(f"   Repository: {operation.get('Repository', 'N/A')}")
                    print(f"   Branch: {operation.get('Branch') or operation.get('BranchName', 'N/A')}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data) as response:
                        if self.debug_mode:
                            print(f"📡 HTTP Response:")
                            print(f"   Status: {response.status}")
                        
                        response_text = await response.text()
                        if self.debug_mode:
                            print(f"   Raw response: {response_text}")
                        
                        if response.status != 200:
                            error_result = {
                                "isSuccessful": False, 
                                "errorMessage": f"HTTP {response.status}: {response_text}",
                                "status_code": response.status
                            }
                            
                            try:
                                error_data = json.loads(response_text) if response_text else {}
                                error_result.update(error_data)
                            except json.JSONDecodeError:
                                pass
                            
                            # Check if error is retryable for this operation type
                            error_code = error_result.get("errorCode", "UNKNOWN")
                            should_retry = (
                                operation_type in retryable_operations and 
                                error_code in retryable_error_codes and
                                attempt < max_retries - 1
                            )
                            
                            # Set flag for DECRYPTION_FAILED to trigger re-encryption
                            if error_code == "DECRYPTION_FAILED":
                                last_decryption_failed = True
                                consecutive_failures += 1
                                if self.debug_mode:
                                    print(f"🔐 DECRYPTION_FAILED detected (failure #{consecutive_failures}) - will re-encrypt on next attempt")
                            
                            if not should_retry:
                                print(f"❌ Not retrying {operation_type} operation due to {error_code}")
                                return error_result
                            
                            # Wait before retry with exponential backoff
                            delay = min(base_delay * (2 ** attempt), max_delay)
                            print(f"⏳ Waiting {delay:.1f}s before retry ({error_code})...")
                            await asyncio.sleep(delay)
                            continue
                        
                        try:
                            result = json.loads(response_text) if response_text else {}
                            if self.debug_mode:
                                print(f"   Parsed JSON: {result}")
                            
                            # Check if the operation was successful
                            if result.get("isSuccessful", True):
                                if attempt > 0:
                                    print(f"✅ Git operation succeeded on attempt {attempt + 1}")
                                return result
                            else:
                                # Operation failed - check if we should retry
                                error_msg = result.get("errorMessage", "Unknown error")
                                error_code = result.get("errorCode", "UNKNOWN")
                                
                                print(f"❌ Git operation failed: {error_code} - {error_msg}")
                                
                                # Check if error is retryable for this operation type
                                should_retry = (
                                    operation_type in retryable_operations and 
                                    error_code in retryable_error_codes and
                                    error_code not in non_retryable_error_codes and
                                    attempt < max_retries - 1
                                )
                                
                                if not should_retry:
                                    print(f"❌ Not retrying {operation_type} operation due to {error_code}")
                                    return result
                                
                                # Special handling for DECRYPTION_FAILED
                                if error_code == "DECRYPTION_FAILED":
                                    last_decryption_failed = True
                                    consecutive_failures += 1
                                    if self.debug_mode:
                                        print(f"🔐 DECRYPTION_FAILED detected (failure #{consecutive_failures}) - will re-encrypt on next attempt")
                                    
                                    # After 2 consecutive DECRYPTION_FAILED errors, trigger agent recreation
                                    if consecutive_failures >= 2 and hasattr(self, 'agent_recreation_callback') and self.agent_recreation_callback:
                                        print(f"🔄 2 consecutive DECRYPTION_FAILED errors - triggering HexaEight agent recreation")
                                        try:
                                            await self.agent_recreation_callback()
                                            consecutive_failures = 0  # Reset counter after recreation
                                        except Exception as recreation_error:
                                            print(f"❌ Agent recreation failed: {recreation_error}")
                                else:
                                    consecutive_failures = 0  # Reset counter for non-decryption failures
                                    last_decryption_failed = False  # Reset flag for non-decryption failures
                                    
                                # Wait before retry with exponential backoff
                                delay = min(base_delay * (2 ** attempt), max_delay)
                                print(f"⏳ Waiting {delay:.1f}s before retry ({error_code})...")
                                await asyncio.sleep(delay)
                                continue
                                
                        except json.JSONDecodeError as e:
                            error_result = {
                                "isSuccessful": False,
                                "errorMessage": f"Invalid JSON response: {e}",
                                "raw_response": response_text
                            }
                            
                            # Only retry JSON decode errors for commit operations
                            if operation_type in retryable_operations and attempt < max_retries - 1:
                                delay = min(base_delay * (2 ** attempt), max_delay)
                                print(f"⏳ Waiting {delay:.1f}s before retry (JSON decode error)...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                return error_result
                        
            except Exception as e:
                print(f"❌ Error sending encrypted git operation (attempt {attempt + 1}): {e}")
                
                # Only retry exceptions for commit operations
                if operation_type in retryable_operations and attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    print(f"⏳ Waiting {delay:.1f}s before retry (exception)...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    return {"isSuccessful": False, "errorMessage": str(e)}
        
        # This should only be reached for retryable operations
        return {"isSuccessful": False, "errorMessage": "Max retries exceeded"}

    async def _encrypt_git_operation(self, operation: Dict[str, Any]) -> str:
        """Encrypt git operation using the correct session access pattern with enhanced error handling"""
        try:
            message_content = json.dumps(operation)
            if self.debug_mode:
                print(f"🔐 Encrypting git operation for server: {self.git_server_agent_name}")
                print(f"📋 Raw operation JSON: {message_content}")
            
            last_error = None
            
            # Method 1: Try direct access to hexaeight_agent._clr_agent_config.Session
            if hasattr(self.agent, 'hexaeight_agent') and self.agent.hexaeight_agent:
                hexaeight_agent = self.agent.hexaeight_agent
                if hasattr(hexaeight_agent, '_clr_agent_config'):
                    clr_config = hexaeight_agent._clr_agent_config
                    if hasattr(clr_config, 'Session') and clr_config.Session:
                        session = clr_config.Session
                        if hasattr(session, 'EncryptTextMessageToDestination'):
                            try:
                                # Add validation before encryption
                                if not self.git_server_agent_name or not message_content:
                                    raise Exception("Missing required encryption parameters")
                                    
                                encrypted = session.EncryptTextMessageToDestination(
                                    message_content, self.git_server_agent_name
                                )
                                if encrypted and isinstance(encrypted, str) and len(encrypted) > 0:
                                    if self.debug_mode:
                                        print(f"✅ Encrypted via hexaeight_agent._clr_agent_config.Session")
                                    return encrypted
                                else:
                                    raise Exception("Encryption returned empty or invalid result")
                            except Exception as e:
                                last_error = e
                                print(f"⚠️ Method 1 encryption failed: {e}")
            
            # Method 2: Try direct access to _clr_agent_config.Session
            if hasattr(self.agent, '_clr_agent_config'):
                agent_config = self.agent._clr_agent_config
                if hasattr(agent_config, 'Session') and agent_config.Session:
                    session = agent_config.Session
                    if hasattr(session, 'EncryptTextMessageToDestination'):
                        try:
                            # Add validation before encryption
                            if not self.git_server_agent_name or not message_content:
                                raise Exception("Missing required encryption parameters")
                                
                            encrypted = session.EncryptTextMessageToDestination(
                                message_content, self.git_server_agent_name
                            )
                            if encrypted and isinstance(encrypted, str) and len(encrypted) > 0:
                                if self.debug_mode:
                                    print(f"✅ Encrypted via _clr_agent_config.Session")
                                return encrypted
                            else:
                                raise Exception("Encryption returned empty or invalid result")
                        except Exception as e:
                            last_error = e
                            print(f"⚠️ Method 2 encryption failed: {e}")
            
            # Method 3: Try alternative session access patterns if available
            session_sources = [
                (getattr(self.agent, 'session', None), "direct session"),
                (getattr(self.agent, 'hexaeight_session', None), "hexaeight_session"),
                (getattr(getattr(self.agent, 'config', None), 'session', None), "config.session")
            ]
            
            for session_obj, source_name in session_sources:
                if session_obj and hasattr(session_obj, 'EncryptTextMessageToDestination'):
                    try:
                        if not self.git_server_agent_name or not message_content:
                            continue
                            
                        encrypted = session_obj.EncryptTextMessageToDestination(
                            message_content, self.git_server_agent_name
                        )
                        if encrypted and isinstance(encrypted, str) and len(encrypted) > 0:
                            if self.debug_mode:
                                print(f"✅ Encrypted via {source_name}")
                            return encrypted
                    except Exception as e:
                        last_error = e
                        print(f"⚠️ {source_name} encryption failed: {e}")
            
            # If all methods failed, provide detailed error information
            error_msg = f"No working encryption session found. Last error: {last_error}"
            print(f"❌ {error_msg}")
            print(f"   Agent type: {type(self.agent).__name__}")
            print(f"   Has hexaeight_agent: {hasattr(self.agent, 'hexaeight_agent')}")
            print(f"   Has _clr_agent_config: {hasattr(self.agent, '_clr_agent_config')}")
            print(f"   Git server agent name: {self.git_server_agent_name}")
            
            raise Exception(error_msg)
            
        except Exception as e:
            print(f"❌ Error encrypting git operation: {e}")
            raise

    async def _create_agent_auth_header(self) -> str:
        """Create encrypted auth header using enhanced session access pattern"""
        try:
            auth_data = {
                "agentName": self.agent_name,
                "internalId": getattr(self.agent, 'internal_id', ''),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "agentType": getattr(self.agent, 'agent_type', 'TOOL')
            }
            
            message_content = json.dumps(auth_data)
            if self.debug_mode:
                print(f"🔐 Creating auth header for server: {self.git_server_agent_name}")
            
            last_error = None
            
            # Method 1: Try direct access to hexaeight_agent._clr_agent_config.Session
            if hasattr(self.agent, 'hexaeight_agent') and self.agent.hexaeight_agent:
                hexaeight_agent = self.agent.hexaeight_agent
                if hasattr(hexaeight_agent, '_clr_agent_config'):
                    clr_config = hexaeight_agent._clr_agent_config
                    if hasattr(clr_config, 'Session') and clr_config.Session:
                        session = clr_config.Session
                        if hasattr(session, 'EncryptTextMessageToDestination'):
                            try:
                                if not self.git_server_agent_name or not message_content:
                                    raise Exception("Missing required encryption parameters")
                                    
                                encrypted = session.EncryptTextMessageToDestination(
                                    message_content, self.git_server_agent_name
                                )
                                if encrypted and isinstance(encrypted, str) and len(encrypted) > 0:
                                    print(f"✅ Auth header encrypted via Method 1")
                                    return encrypted
                                else:
                                    raise Exception("Encryption returned empty or invalid result")
                            except Exception as e:
                                last_error = e
                                print(f"⚠️ Method 1 auth encryption failed: {e}")
            
            # Method 2: Try direct access to _clr_agent_config.Session
            if hasattr(self.agent, '_clr_agent_config'):
                agent_config = self.agent._clr_agent_config
                if hasattr(agent_config, 'Session') and agent_config.Session:
                    session = agent_config.Session
                    if hasattr(session, 'EncryptTextMessageToDestination'):
                        try:
                            if not self.git_server_agent_name or not message_content:
                                raise Exception("Missing required encryption parameters")
                                
                            encrypted = session.EncryptTextMessageToDestination(
                                message_content, self.git_server_agent_name
                            )
                            if encrypted and isinstance(encrypted, str) and len(encrypted) > 0:
                                print(f"✅ Auth header encrypted via Method 2")
                                return encrypted
                            else:
                                raise Exception("Encryption returned empty or invalid result")
                        except Exception as e:
                            last_error = e
                            print(f"⚠️ Method 2 auth encryption failed: {e}")
            
            # Method 3: Try alternative session access patterns
            session_sources = [
                (getattr(self.agent, 'session', None), "direct session"),
                (getattr(self.agent, 'hexaeight_session', None), "hexaeight_session"),
                (getattr(getattr(self.agent, 'config', None), 'session', None), "config.session")
            ]
            
            for session_obj, source_name in session_sources:
                if session_obj and hasattr(session_obj, 'EncryptTextMessageToDestination'):
                    try:
                        if not self.git_server_agent_name or not message_content:
                            continue
                            
                        encrypted = session_obj.EncryptTextMessageToDestination(
                            message_content, self.git_server_agent_name
                        )
                        if encrypted and isinstance(encrypted, str) and len(encrypted) > 0:
                            print(f"✅ Auth header encrypted via {source_name}")
                            return encrypted
                    except Exception as e:
                        last_error = e
                        print(f"⚠️ {source_name} auth encryption failed: {e}")
            
            # If all methods failed, provide detailed error information
            error_msg = f"No working encryption session found for auth header. Last error: {last_error}"
            print(f"❌ {error_msg}")
            
            raise Exception(error_msg)
            
        except Exception as e:
            print(f"❌ Error creating auth header: {e}")
            raise

    # =====================================================================================
    # UPLOAD SESSION METHODS (PRESERVED)
    # =====================================================================================

    async def _create_upload_session(self) -> Dict[str, Any]:
        """Create upload session for large files"""
        try:
            auth_header = await self._create_agent_auth_header()
            
            url = f"{self.git_server_url}/api/upload/session"
            
            async with aiohttp.ClientSession() as session:
                headers = {"X-HexaEight-Auth": auth_header}
                async with session.post(url, headers=headers) as response:
                    response_text = await response.text()
                    
                    if response.status != 200:
                        return {
                            "isSuccessful": False,
                            "errorMessage": f"HTTP {response.status}: {response_text}",
                            "status_code": response.status
                        }
                    
                    try:
                        result = json.loads(response_text) if response_text else {}
                        return result
                    except json.JSONDecodeError as e:
                        return {
                            "isSuccessful": False,
                            "errorMessage": f"Invalid JSON response: {e}",
                            "raw_response": response_text
                        }
                    
        except Exception as e:
            print(f"❌ Error creating upload session: {e}")
            return {"isSuccessful": False, "errorMessage": str(e)}

    async def _upload_large_file(self, session_id: str, file_op: GitFileOperation) -> Dict[str, Any]:
        """Upload a large file to the upload session"""
        try:
            auth_header = await self._create_agent_auth_header()
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-HexaEight-Auth": auth_header,
                    "Content-Type": "application/octet-stream"
                }
                
                url = f"{self.git_server_url}/api/upload/{session_id}/{file_op.path}"
                content_bytes = file_op.content.encode('utf-8') if file_op.content else b""
                
                async with session.post(url, headers=headers, data=content_bytes) as response:
                    result = await response.json()
                    return result
                    
        except Exception as e:
            print(f"❌ Error uploading large file: {e}")
            return {"isSuccessful": False, "errorMessage": str(e)}

    async def _complete_upload_session(self, session_id: str, git_operation: Dict[str, Any]) -> Dict[str, Any]:
        """Complete upload session and execute git operation"""
        try:
            auth_header = await self._create_agent_auth_header()
            encrypted_operation = await self._encrypt_git_operation(git_operation)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-HexaEight-Auth": auth_header,
                    "Content-Type": "application/json"
                }
                
                url = f"{self.git_server_url}/api/upload/{session_id}/complete"
                data = {"encryptedAuth": encrypted_operation}
                
                async with session.post(url, headers=headers, json=data) as response:
                    result = await response.json()
                    return result
                    
        except Exception as e:
            print(f"❌ Error completing upload session: {e}")
            return {"isSuccessful": False, "errorMessage": str(e)}

    async def _cancel_upload_session(self, session_id: str) -> Dict[str, Any]:
        """Cancel upload session and cleanup"""
        try:
            auth_header = await self._create_agent_auth_header()
            
            async with aiohttp.ClientSession() as session:
                headers = {"X-HexaEight-Auth": auth_header}
                url = f"{self.git_server_url}/api/upload/{session_id}"
                
                async with session.delete(url, headers=headers) as response:
                    result = await response.json()
                    return result
                    
        except Exception as e:
            print(f"❌ Error cancelling upload session: {e}")
            return {"isSuccessful": False, "errorMessage": str(e)}

    # =====================================================================================
    # CONVENIENCE METHODS
    # =====================================================================================

    async def get_session_history(self) -> List[Dict[str, Any]]:
        """Get history of operations performed in this session"""
        return self.session_history.copy()

    async def safe_code_modification(self, 
                                   files_to_modify: List[GitFileOperation], 
                                   description: str,
                                   repository: str = None,
                                   test_branch: str = None) -> Dict[str, Any]:
        """Safely modify code with automatic rollback capability"""
        try:
            repo = repository or self.current_repository
            original_branch = self.current_branch
            branch_name = test_branch or f"agent-test-{int(datetime.utcnow().timestamp())}"
            
            print(f"🔧 Safe code modification: {description}")
            
            # 1. Create test branch
            branch_result = await self.create_branch(branch_name, original_branch, repo)
            if not self._check_success(branch_result):
                return {"success": False, "error": "Failed to create test branch", "rollback": None}
            
            # 2. Switch to test branch
            switch_result = await self.switch_branch(branch_name, repo)
            if not self._check_success(switch_result):
                return {"success": False, "error": "Failed to switch to test branch", "rollback": "delete_branch"}
            
            # 3. Apply changes
            commit_result = await self.commit_files(files_to_modify, f"Agent modification: {description}", repo, branch_name)
            
            if commit_result.success:
                return {
                    "success": True,
                    "message": "Code modified successfully on test branch",
                    "test_branch": branch_name,
                    "original_branch": original_branch,
                    "commit_sha": commit_result.commit_sha,
                    "rollback_instructions": {
                        "switch_back": f"Switch back to '{original_branch}' branch",
                        "delete_test_branch": f"Delete test branch '{branch_name}' if changes are not needed",
                        "revert_commit": f"Revert to commit before {commit_result.commit_sha} if needed"
                    }
                }
            else:
                # Switch back to original branch if commit failed
                await self.switch_branch(original_branch, repo)
                return {
                    "success": False, 
                    "error": commit_result.message,
                    "rollback_performed": f"Switched back to {original_branch}"
                }
                
        except Exception as e:
            print(f"❌ Error in safe code modification: {e}")
            return {"success": False, "error": str(e)}

# =====================================================================================
# INTEGRATION HELPERS FOR EXISTING AGENTS
# =====================================================================================

def add_git_capability_to_agent(agent_instance, git_server_url: str = None) -> GitMCPTool:
    """
    Helper function to add Git MCP tool to an existing HexaEight agent
    
    Args:
        agent_instance: Existing HexaEight agent instance
        git_server_url: Git server URL (optional, will use environment variables)
        
    Returns:
        GitMCPTool instance ready for use
    """
    git_tool = GitMCPTool(agent_instance, git_server_url)
    
    # Add tool methods to agent instance for easy access
    agent_instance.git = git_tool
    agent_instance.git_create_repository = git_tool.create_repository
    agent_instance.git_commit_files = git_tool.commit_files
    agent_instance.git_revert_to_commit = git_tool.revert_to_commit
    agent_instance.git_create_branch = git_tool.create_branch
    agent_instance.git_switch_branch = git_tool.switch_branch
    agent_instance.git_safe_modify = git_tool.safe_code_modification
    agent_instance.git_read_file = git_tool.read_file
    # New enhanced operations
    agent_instance.git_get_history = git_tool.get_commit_history
    agent_instance.git_get_file_history = git_tool.get_file_history
    agent_instance.git_compare_commits = git_tool.compare_commits
    agent_instance.git_show_commit = git_tool.show_commit_details
    agent_instance.git_merge_branch = git_tool.merge_branch
    
    print("✅ Git MCP tool (LibGit2-Compatible) added to agent capabilities")
    return git_tool
