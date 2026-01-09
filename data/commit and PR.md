# commit and PR

## Summary

This PR fixes several bugs related to file deletion and spell-checking features, and improves the proofreading functionality.

## Changes

### Bug Fixes

#### File Deletion Fix

- **Problem**: File deletion was not working properly in some environments

- **Cause**: DELETE request body was being ignored by certain HTTP clients (Electron/browser)

- **Solution**: Changed to use query parameter `?path=`) instead of request body

#### Trash File List Fix  

- **Problem**: Deleted files appeared in both the file list and trash simultaneously

- **Cause**: `rglob("*.md")` was including files from `.trash` folder

- **Solution**: Added filter to exclude `.trash/` paths from file listing

#### Proofreading Highlight Fix

- **Problem**: Red error highlights remained after closing the proofreading panel

- **Cause**: Position-based highlight removal failed when text positions changed

- **Solution**: Changed to select entire document and remove all highlights at once

### Improvements

#### Proofreading Feature Enhancement

- Text replacement now searches directly in editor content (more reliable than markdown conversion)

- Added position tracking for correction items

- Positions are updated after each correction to maintain accuracy

- Clicking a correction item in the panel scrolls to that location in the editor

- Added visual highlight styles (red wavy underline with pulse animation)

- Support for dark, light, dim, and sepia themes

## Testing

- [x] File deletion moves file to trash correctly

- [x] Deleted files only appear in trash, not in file list

- [x] Proofreading highlights appear on errors

- [x] Individual corrections can be applied

- [x] All highlights are removed when panel closes

- [x] Clicking correction item scrolls to error location

fix: resolve file deletion not working properly

- Change DELETE /vault/file endpoint to use query parameter instead of request body

- Some HTTP clients ignore body in DELETE requests, causing deletion to fail

- Update frontend to send path as query parameter

fix: exclude .trash folder files from vault file list

- Files in .trash folder were appearing in both file list and trash

- Add filter to exclude paths starting with ".trash/" in list_vault_files

fix: proofreading highlight not removed when panel closes

- Change removeAllProofreadHighlights to select entire document and unset all highlights

- Previous position-based removal failed when text positions changed after corrections

feat: improve proofreading text replacement logic

- Find text positions directly in editor instead of markdown conversion

- Add position tracking for each correction item

- Update positions of remaining items after applying a correction

- Add focus-item event to scroll to error location when clicking panel item