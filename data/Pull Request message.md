# Pull Request message

## Summary

This PR introduces a workspace environment management system and improves the image upload naming convention to prevent file collisions.

## Features

### 🗂️ Environment Management

Users can now manage multiple workspace environments (vaults) within the application:

- **Add environments**: Click the "+" button in the sidebar to add a new workspace folder
- **Switch environments**: Use the dropdown to switch between different workspaces
- **Remove environments**: Remove workspaces from the list (actual folders are preserved)
- **Persistent settings**: Environment configuration is saved and restored on app restart

![Environment Selector]

### 🖼️ Improved Image Naming

Uploaded images now include the current note name and timestamp in their filename:

- **Before**: `img_20260108_143052_abc123.png`
- **After**: `welcome_20260108_143052_123456.png`

This prevents file collisions when uploading images across different notes.

### 🎨 Custom Delete Confirmation Modal

Replaced the browser's native `confirm()` dialog with a styled modal when removing environments:

- Warning icon with visual feedback
- Displays the environment name being removed
- Clear messaging that actual files won't be deleted
- Styled cancel and delete buttons

## Technical Changes

### Backend

- `apps/core/app/routers/environment.py` - New router for environment CRUD operations
- `apps/core/app/routers/vault.py` - Updated to use dynamic environment paths
- `apps/core/app/schemas.py` - Added `note_name` field to `ImageUploadPayload`

### Frontend

- `apps/desktop/renderer/src/composables/useEnvironment.ts` - New composable for environment state
- `apps/desktop/renderer/src/components/AppSidebar.vue` - Environment selector UI and modals
- `apps/desktop/renderer/src/components/EditorView.vue` - Pass note name on image upload

## API Endpoints

| Method

 | Endpoint

 | Description

 |
| --- | --- | --- |

| GET

 | `/environment/list`

 | List all environments

 |
| --- | --- | --- |

| POST

 | `/environment/add`

 | Add new environment

 |
| --- | --- | --- |

| POST

 | `/environment/set-current`

 | Set current environment

 |
| --- | --- | --- |

| DELETE

 | `/environment/remove`

 | Remove environment from list

 |
| --- | --- | --- |

| GET

 | `/environment/current`

 | Get current environment

 |
| --- | --- | --- |

| POST

 | `/environment/init-default`

 | Initialize default environment

 |
| --- | --- | --- |

## Testing

- [x] Add new environment via folder picker

- [x] Switch between environments

- [x] Remove environment (verify folder not deleted)

- [x] Upload image and verify filename includes note name

- [x] Verify file operations use correct environment path