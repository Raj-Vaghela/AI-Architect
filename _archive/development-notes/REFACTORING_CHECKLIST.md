# Refactoring Checklist

Quick checklist for implementing code quality improvements from the review.

## Priority 1: High Impact, Easy Wins

### 1. Standardize Docstrings ⬜
- [ ] Add Args/Returns to all functions in `db.py`
- [ ] Update `main.py` endpoint docstrings
- [ ] Standardize on Google-style format

**Files to update:**
- `backend/app/db.py` - Missing Args in several functions
- `backend/app/main.py` - Minimal endpoint docs
- `backend/app/tools/*.py` - Check consistency

### 2. Extract Magic Numbers to Constants ⬜
- [ ] Create constants for title generation config
- [ ] Move hardcoded limits to config.py
- [ ] Document why each value was chosen

**Code to refactor:**
```python
# backend/app/main.py lines 93-104
temperature=0.7  # → TitleConfig.TEMPERATURE
max_tokens=20    # → TitleConfig.MAX_TOKENS
if len(title) > 60  # → TitleConfig.MAX_TITLE_LENGTH
```

### 3. Create Auth Utils (Frontend) ⬜
- [ ] Create `frontend/src/lib/auth-utils.ts`
- [ ] Add `getAuthToken()` function
- [ ] Add `getAuthHeaders()` function
- [ ] Update all files using duplicate auth logic

**Files to update:**
- `frontend/src/lib/backend.ts`
- `frontend/src/hooks/useConversations.ts`

### 4. Add Database Connection Pooling ⬜
- [ ] Import `psycopg_pool`
- [ ] Create pool at module level in `db.py`
- [ ] Update `get_db_connection()` to use pool
- [ ] Test performance improvement

**File:** `backend/app/db.py`

### 5. Reorganize Documentation Folder ⬜
- [ ] Create `docs/` subfolders (architecture, features, setup, api)
- [ ] Move files to appropriate folders
- [ ] Update `README.md` with new structure
- [ ] Update any hardcoded doc links

**Structure to create:**
```
backend/docs/
├── architecture/
├── features/
├── setup/
└── api/
```

---

## Priority 2: Medium Impact

### 6. Create API Reference Documentation ⬜
- [ ] Create `backend/docs/api/API_REFERENCE.md`
- [ ] Document all `/api/v1/chat/*` endpoints
- [ ] Include request/response examples
- [ ] Add authentication requirements
- [ ] Link from main README

### 7. Add Conversation Access Dependency ⬜
- [ ] Create `verify_conversation_access()` in `auth.py`
- [ ] Update `get_history()` to use dependency
- [ ] Update `chat_message()` to use dependency
- [ ] Update `delete_chat()` to use dependency

**Benefit:** DRY - 8 lines of duplicate code → 1 dependency

### 8. Add Unit Tests ⬜
- [ ] Create `backend/tests/` directory
- [ ] Add `tests/__init__.py`
- [ ] Write tests for `db.py` functions
- [ ] Write tests for `auth.py` functions
- [ ] Add pytest to requirements-dev.txt

**Files to create:**
- `backend/tests/test_db.py`
- `backend/tests/test_auth.py`
- `backend/tests/test_title_generation.py`

### 9. Remove Redundant Comments ⬜
- [ ] Review all `# Comment that just restates code`
- [ ] Remove or improve to explain WHY not WHAT
- [ ] Add explanatory comments to complex logic

**Files to review:**
- `backend/app/main.py`
- `backend/app/auth.py`

### 10. Fix `any` Types in Frontend ⬜
- [ ] Create `ConversationListResponse` interface
- [ ] Update `backend.ts` line 129-130
- [ ] Check for other `any` types
- [ ] Run TypeScript strict mode check

**File:** `frontend/src/lib/backend.ts`

---

## Priority 3: Nice to Have

### 11. Add TODO Comments ⬜
- [ ] Review code for known issues
- [ ] Add TODO comments with context
- [ ] Link to issues/tickets if available

**Format:**
```python
# TODO: Add rate limiting to prevent abuse
# TODO: Support different languages (currently English-only)
```

### 12. Reorganize Scripts Folder ⬜
- [ ] Create `backend/tests/` for test scripts
- [ ] Create `backend/scripts/dev/` for dev utilities
- [ ] Move files to appropriate locations
- [ ] Update any hardcoded paths

### 13. Add Type Checking to CI ⬜
- [ ] Add `mypy` to requirements-dev.txt
- [ ] Configure `mypy.ini` or `pyproject.toml`
- [ ] Add type checking to CI pipeline
- [ ] Fix any type errors discovered

### 14. Create Barrel Exports (Frontend) ⬜
- [ ] Create `frontend/src/lib/index.ts`
- [ ] Export all from subdirectories
- [ ] Update imports in components
- [ ] Verify no circular dependencies

---

## Tracking Progress

**Started:** _______________

**Completed:** _______________

**Notes:**
- Focus on Priority 1 first
- Test after each change
- Commit frequently with clear messages
- Update this checklist as you go

---

## Quick Reference

### Good Docstring Template

```python
def function_name(arg1: str, arg2: int = 10) -> bool:
    """
    One-line summary of what the function does.
    
    More detailed explanation if needed. Can be multiple
    paragraphs explaining behavior, edge cases, etc.
    
    Args:
        arg1: Description of first argument
        arg2: Description of second argument (defaults to 10)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg1 is empty
        HTTPException: When validation fails
        
    Example:
        >>> function_name("hello", 5)
        True
    """
```

### Extracting Constants

**Before:**
```python
if len(title) > 60:
    title = title[:57] + "..."
```

**After:**
```python
# config.py
MAX_TITLE_LENGTH = 60
ELLIPSIS = "..."
TRUNCATE_AT = MAX_TITLE_LENGTH - len(ELLIPSIS)

# main.py
if len(title) > MAX_TITLE_LENGTH:
    title = title[:TRUNCATE_AT] + ELLIPSIS
```

### Connection Pooling

**Before:**
```python
def get_db_connection():
    conn = psycopg.connect(url)
    yield conn
```

**After:**
```python
from psycopg_pool import ConnectionPool

_pool = ConnectionPool(url, min_size=2, max_size=10)

def get_db_connection():
    with _pool.connection() as conn:
        yield conn
```

---

## Questions to Ask While Refactoring

1. **Docstrings:**
   - Does this docstring explain WHAT the function does?
   - Are all parameters documented?
   - Is the return value clear?
   - Are exceptions listed?

2. **Constants:**
   - Is this number used multiple times?
   - Would changing this number require code updates?
   - Does this number have special meaning?
   - → If yes to any, extract to constant!

3. **Redundancy:**
   - Have I written this code before?
   - Could this be a shared function/utility?
   - Are there 3+ similar code blocks?
   - → If yes, consolidate!

4. **Comments:**
   - Does this comment add information?
   - Could I improve the code instead of commenting?
   - Is this explaining WHY or just WHAT?
   - → Remove redundant, improve necessary!

---

## Testing Your Changes

After each refactoring:

```bash
# Backend
cd backend
.\venv\Scripts\Activate.ps1

# Run integration tests
python scripts/test_auth_chat.py
python scripts/test_delete_chat.py
python scripts/test_title_generation.py

# Start server and test manually
python -m app.main

# Frontend
cd frontend
npm run dev

# Test in browser:
# - Login
# - Create chat
# - Delete chat
# - Check timestamps
```

---

## When Complete

- [ ] Update `README.md` with new structure
- [ ] Review `CODE_REVIEW_REPORT.md` to ensure all items addressed
- [ ] Run full test suite
- [ ] Commit with message: "Refactor: Improve code quality and documentation"
- [ ] Create PR if using version control
- [ ] Celebrate! 🎉

---

**Remember:** The goal isn't perfection, it's **continuous improvement**!

Make small changes, test frequently, and don't break existing functionality.


