from huggingface_hub import snapshot_download
import os

BASE_DIR = os.path.join(os.getcwd(), "data")

models = {
    "SmolLM2-1.7B-Instruct": "HuggingFaceTB/SmolLM2-1.7B-Instruct",
    "Phi-3.5-mini-instruct": "microsoft/Phi-3.5-mini-instruct",
}

for local_name, repo_id in models.items():
    local_dir = os.path.join(BASE_DIR, local_name)

    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        local_dir_use_symlinks=False,  # 실제 파일 복사 (GGUF/배포용에 안전)
        resume_download=True
    )

    print(f"✅ Downloaded {repo_id} → {local_dir}")
