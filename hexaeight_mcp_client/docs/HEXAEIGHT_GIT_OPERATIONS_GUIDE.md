# HexaEight Git Operations Guide

## Overview
HexaEight YARP Proxy now supports comprehensive Git operations including commit history, diff functionality, and rollback capabilities. This guide provides complete usage instructions for all Git operations.

## Authentication
All Git operations require encrypted authentication using HexaEight agents. Operations are sent as encrypted requests to the Git service endpoints.

## Operation Format
```json
{
  "encryptedAuth": "base64_encrypted_auth_string"
}
```

The encrypted payload contains a `GitOperation` object with the following structure:

```json
{
  "operation": "operation_name",
  "repository": "repository_name",
  "branch": "branch_name",
  "targetCommit": "commit_sha",
  "filePath": "path/to/file",
  "commitMessage": "commit_message_or_params",
  "branchName": "new_branch_name",
  "files": [
    {
      "path": "file/path",
      "content": "file_content"
    }
  ]
}
```

---

## Available Git Operations

### 1. Repository Management

#### Create Repository
**Operation:** `init` or `create`
**Purpose:** Initialize a new Git repository

**Example:**
```json
{
  "operation": "create",
  "repository": "my-project",
  "commitMessage": "Initial repository setup"
}
```

**Response:**
- Success: Repository created with initial commit
- Contains repository path and status

---

### 2. Commit History Operations

#### Get Commit History
**Operation:** `history` or `log`
**Purpose:** Retrieve paginated commit history for a branch

**Parameters:**
- `repository`: Repository name (required)
- `branch`: Branch name (default: "master")
- `commitMessage`: Pagination in format "skip,take" (default: "0,50")

**Example:**
```json
{
  "operation": "history",
  "repository": "my-project",
  "branch": "master",
  "commitMessage": "0,20"
}
```

**Response:**
```json
{
  "isSuccessful": true,
  "commits": [
    {
      "sha": "abc123def456...",
      "message": "Full commit message",
      "messageShort": "Short commit message",
      "author": "John Doe",
      "authorEmail": "john@example.com",
      "date": "2025-01-15T10:30:00Z",
      "parentCount": 1,
      "parentShas": ["parent_commit_sha"]
    }
  ],
  "totalCount": 150,
  "skip": 0,
  "take": 20,
  "branch": "master"
}
```

#### Get File History
**Operation:** `file-history`
**Purpose:** Get commit history for a specific file

**Parameters:**
- `repository`: Repository name (required)
- `filePath`: File path (required)
- `branch`: Branch name (default: "master")

**Example:**
```json
{
  "operation": "file-history",
  "repository": "my-project",
  "filePath": "src/main.py",
  "branch": "master"
}
```

**Response:** Same format as history but filtered to commits that modified the file.

---

### 3. Diff Operations

#### Compare Commits
**Operation:** `diff`
**Purpose:** Compare two commits and show differences

**Parameters:**
- `repository`: Repository name (required)
- `branch`: From commit SHA (required)
- `targetCommit`: To commit SHA (default: "HEAD")

**Example:**
```json
{
  "operation": "diff",
  "repository": "my-project",
  "branch": "abc123def",
  "targetCommit": "def456ghi"
}
```

**Response:**
```json
{
  "isSuccessful": true,
  "diffEntries": [
    {
      "oldPath": "old/file/path.py",
      "newPath": "new/file/path.py",
      "status": "Modified",
      "linesAdded": 15,
      "linesDeleted": 8,
      "patch": "diff --git a/file.py b/file.py\n...",
      "oldOid": "old_blob_sha",
      "newOid": "new_blob_sha"
    }
  ],
  "fromCommit": "abc123def",
  "toCommit": "def456ghi",
  "filesChanged": 3,
  "totalLinesAdded": 42,
  "totalLinesDeleted": 15
}
```

**Status Values:**
- `Modified`: File was changed
- `Added`: New file
- `Deleted`: File removed
- `Renamed`: File moved/renamed

**Note:** The `oldOid` and `newOid` fields use the LibGit2Sharp API's `OldOid.Sha` and `Oid.Sha` respectively.

---

### 4. Commit Details

#### Show Commit Details
**Operation:** `show`
**Purpose:** Show detailed information about a specific commit

**Parameters:**
- `repository`: Repository name (required)
- `targetCommit`: Commit SHA (default: "HEAD")

**Example:**
```json
{
  "operation": "show",
  "repository": "my-project",
  "targetCommit": "abc123def456"
}
```

**Response:**
```json
{
  "isSuccessful": true,
  "commit": {
    "sha": "abc123def456...",
    "message": "Add new feature",
    "messageShort": "Add new feature",
    "author": "Jane Smith",
    "authorEmail": "jane@example.com",
    "date": "2025-01-15T14:20:00Z",
    "parentCount": 1,
    "parentShas": ["parent_sha"]
  },
  "changes": [
    {
      "oldPath": "",
      "newPath": "src/feature.py",
      "status": "Added",
      "linesAdded": 50,
      "linesDeleted": 0,
      "patch": "diff content..."
    }
  ],
  "modifiedFiles": ["src/feature.py", "README.md"]
}
```

---

### 5. File Operations

#### Read File Content
**Operation:** `read`
**Purpose:** Get file content from a specific commit or branch

**Parameters:**
- `repository`: Repository name (required)
- `filePath`: File path (required)
- `branch`: Branch name (default: "master")
- `targetCommit`: Specific commit SHA (optional, overrides branch)

**Example (from branch):**
```json
{
  "operation": "read",
  "repository": "my-project",
  "filePath": "src/config.json",
  "branch": "master"
}
```

**Example (from specific commit):**
```json
{
  "operation": "read",
  "repository": "my-project",
  "filePath": "src/config.json",
  "targetCommit": "abc123def456"
}
```

**Response:**
- Success: File content returned in response
- Content accessible via the response data

---

### 6. Branch Operations

#### Create/Switch Branch
**Operation:** `branch`
**Purpose:** Create a new branch or switch to existing branch

**Example:**
```json
{
  "operation": "branch",
  "repository": "my-project",
  "branchName": "feature/new-feature",
  "commitMessage": "Create feature branch"
}
```

#### Checkout/Switch
**Operation:** `checkout` or `switch`
**Purpose:** Switch to a different branch

**Example:**
```json
{
  "operation": "checkout",
  "repository": "my-project",
  "branch": "feature/new-feature"
}
```

---

### 7. Rollback Operations

#### Revert to Commit
**Operation:** `revert`
**Purpose:** Hard reset repository to a specific commit

**Parameters:**
- `repository`: Repository name (required)
- `targetCommit`: Commit SHA to revert to (required)

**Example:**
```json
{
  "operation": "revert",
  "repository": "my-project",
  "targetCommit": "abc123def456"
}
```

**Response:**
- Success: Repository state reset to target commit
- All changes after target commit are lost (hard reset)

**⚠️ Warning:** This operation is destructive and cannot be undone!

---

### 8. Commit Operations

#### Commit Changes
**Operation:** `commit` or `push`
**Purpose:** Commit files to repository

**Example:**
```json
{
  "operation": "commit",
  "repository": "my-project",
  "branch": "master",
  "commitMessage": "Update configuration files",
  "files": [
    {
      "path": "config/settings.json",
      "content": "{\"debug\": false}"
    },
    {
      "path": "README.md",
      "content": "# Updated README\n..."
    }
  ]
}
```

---

### 9. Merge Operations

#### Merge Branches
**Operation:** `merge`
**Purpose:** Merge one branch into another

**Example:**
```json
{
  "operation": "merge",
  "repository": "my-project",
  "branch": "master",
  "branchName": "feature/new-feature",
  "commitMessage": "Merge feature branch"
}
```

---

## Common Workflows

### 1. View Recent Commits
```json
{
  "operation": "history",
  "repository": "my-project",
  "branch": "master",
  "commitMessage": "0,10"
}
```

### 2. Compare Two Commits
```json
{
  "operation": "diff",
  "repository": "my-project",
  "branch": "old_commit_sha",
  "targetCommit": "new_commit_sha"
}
```

### 3. Examine Specific Commit
```json
{
  "operation": "show",
  "repository": "my-project",
  "targetCommit": "commit_sha"
}
```

### 4. Get File from Previous Commit
```json
{
  "operation": "read",
  "repository": "my-project",
  "filePath": "important_file.txt",
  "targetCommit": "previous_commit_sha"
}
```

### 5. Rollback to Previous State
```json
{
  "operation": "revert",
  "repository": "my-project",
  "targetCommit": "stable_commit_sha"
}
```

### 6. Track File Changes
```json
{
  "operation": "file-history",
  "repository": "my-project",
  "filePath": "src/critical_module.py",
  "branch": "master"
}
```

---

## Error Handling

Common error codes:
- `REPOSITORY_NOT_FOUND`: Repository doesn't exist
- `BRANCH_NOT_FOUND`: Branch doesn't exist
- `COMMIT_NOT_FOUND`: Commit SHA invalid
- `FILE_NOT_FOUND`: File doesn't exist in commit
- `FILEPATH_REQUIRED`: FilePath parameter missing
- `UNSUPPORTED_OPERATION`: Invalid operation name

---

## Endpoints

**Main Git Operations:**
- `POST /git/{clientId}/operation` - Execute Git operation
- `POST /git/{clientId}/upload/{sessionId}/complete` - Complete file upload with operation

**Browse Operations (JWT authenticated):**
- `GET /git/{clientId}/browse/{repository}/{branch}/{path}` - Browse directory
- `GET /git/{clientId}/raw/{repository}/{branch}/{filepath}` - Get raw file
- `GET /git/{clientId}/info/{repository}` - Repository information

---

## Security Notes

1. All operations require encrypted authentication
2. Repository access is scoped per client ID
3. JWT authentication required for browse/raw endpoints
4. Upload operations have 500MB limit
5. History operations limited to 100 commits per request
6. File history limited to 50 commits per request

---

## LibGit2Sharp Features Used

- **Commit traversal**: `repo.Commits.QueryBy()`
- **Diff generation**: `repo.Diff.Compare<Patch>()`
- **Tree navigation**: `commit.Tree[path]`
- **Branch management**: `repo.Branches`
- **Reset operations**: `repo.Reset()`
- **File content**: `blob.GetContentStream()`

This implementation provides comprehensive Git functionality while maintaining security and performance boundaries.