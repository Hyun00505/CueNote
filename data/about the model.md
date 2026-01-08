# **HuggingFaceTB/SmolLM2-1.7B-Instruct**

HuggingFaceTB/SmolLM2-1.7B-Instruct는 Hugging Face에서 공개한 약 17억 파라미터 규모의 소형(instruct 튜닝) 언어 모델 계열인 SmolLM2 패밀리 중 대형 버전의 지시문 특화 변형이다. 경량이지만 수학, 코드, 일반 대화 등 다양한 작업에서 경쟁력 있는 성능을 내도록 데이터 중심(data-centric) 방식으로 학습된 것이 특징이다. [Hugging Face+1](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct?utm_source=chatgpt.com)

### **핵심 정보**

- **소속/레포지토리:** HuggingFaceTB / `HuggingFaceTB/SmolLM2-1.7B-Instruct` [Hugging Face](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct?utm_source=chatgpt.com)
- **모델 계열:** SmolLM2 (135M, 360M, 1.7B 파라미터) 중 1.7B instruct 버전 [Hugging Face+1](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct?utm_source=chatgpt.com)
- **파라미터 규모:** 약 1.7B (Llama 계열 아키텍처) [Ollama+1](https://ollama.com/library/smollm2%3A1.7b-instruct-q4_1?utm_source=chatgpt.com)
- **라이선스:** Apache-2.0 (오픈 가중치, 상업적 활용 가능) [Hugging Face+1](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct-GGUF?utm_source=chatgpt.com)
- **주요 용도:** 지시문 기반 대화, 요약, 코드·수학 추론, 온디바이스·경량 배포 [Skywork+1](https://skywork.ai/blog/models/huggingfacetb-smollm2-1-7b-instruct-free-chat-online-skywork-ai/?utm_source=chatgpt.com)

### **배경 및 학습 특징**

SmolLM2는 “작지만 많이 훈련된” 소형 LLM을 지향한다. 약 11조 토큰 규모의 데이터로 단계적 커리큘럼을 구성하고, 웹 텍스트뿐 아니라 수학(FineMath), 코드(Stack-Edu), 대화(SmolTalk)와 같은 특수 데이터셋을 혼합해 성능을 끌어올렸다. 이 과정에서 데이터 믹싱 비율을 여러 번 실험·수정하는 데이터 중심 전략을 사용해, 비슷한 크기의 다른 소형 LLM들(Qwen2.5-1.5B, Llama-3.2-1B 등) 대비 벤치마크 우위를 달성했다. [arXiv+1](https://arxiv.org/abs/2502.02737?utm_source=chatgpt.com)

### **아키텍처와 기능**

모델은 Llama 계열 트랜스포머 아키텍처를 기반으로 한 causal LM이며, 지시문 튜닝을 통해 사용자 프롬프트를 따르는 대화형 응답에 최적화되어 있다. 일부 배포체에서는 “think / no_think”와 같이 자세한 추론을 할지, 빠른 응답을 할지를 선택하는 듀얼 모드도 제공한다. 또한 Q4_K_M 등 4-bit 양자화를 포함한 다양한 양자화 구성이 준비되어 있어, 4GB급 GPU나 엣지 디바이스에서도 실행 가능한 것이 장점이다. [Skywork+1](https://skywork.ai/blog/models/huggingfacetb-smollm2-1-7b-instruct-free-chat-online-skywork-ai/?utm_source=chatgpt.com)

###**DeploymentandEcosystem**HuggingFaceTB/SmolLM2-1.7B-InstructisavailabledirectlyonHuggingFaceHubwiththeTransformerslibraryandprovidesone-clickdeploymentoptionsacrossvariousinfrastructuressuchasllama.cpp-basedGGUFformat,Ollama,Koyeb,RunPod,etc.Thisenablesthepracticalorganizationalvalueofeasilysettingupa"smallinstructLLMorganization/service"intheformofanOpenAIAPI-compatibleendpoint,evenforsmallservicesorpersonalprojects.