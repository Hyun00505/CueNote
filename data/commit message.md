# commit message

# feat: add environment management and improve image naming

- Add environment (workspace) management feature
- Create environment router with CRUD API endpoints
- Add environment selector dropdown in sidebar
- Support adding, selecting, and removing environments
- Persist environment settings in JSON config file
- Auto-initialize default environment on first launch
- Update vault router to use dynamic environment paths
- All file operations now use current environment's path
- Files, trash, and images are scoped to selected environment
- Improve image file naming convention
- Include current note name in uploaded image filename
- Add millisecond timestamp to prevent file collisions
- Format: {note_name}_{YYYYMMDD_HHMMSS_ms}.{ext}
- Add custom delete confirmation modal for environments
- Replace browser's native confirm dialog with styled modal
- Display warning icon and environment name
- Add note that actual folder won't be deleted
- Add useEnvironment composable for state management