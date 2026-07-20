---
name: qwen3-performance-optimization
description: Performance optimization techniques for Qwen 3 Coder 30B with reduced context and speed
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [qwen3, coder, performance, optimization, speed, context-reduction]
---

# Qwen 3 Coder 30B Performance Optimization

## Overview
This skill provides specific techniques for optimizing the performance of Qwen 3 Coder 30B when running locally with reduced context windows and speed constraints. It focuses on memory efficiency, reduced computational overhead, and optimized inference parameters.

## When to Use This Skill
- Running Qwen 3 Coder 30B on hardware with limited VRAM (8GB or less)
- Working with tight context windows (1024 tokens or less)
- Needing faster inference response times
- Operating in constrained environments with limited CPU resources
- Developing with minimal system overhead

## Core Optimization Strategies

### 1. Quantization Optimization
For maximum performance on constrained hardware:
- **Q4_K_M**: Best balance of speed and quality for 8GB VRAM systems
- **Q5_K_M**: Better quality for 16GB VRAM systems with minimal performance impact
- **Q6_K**: Highest quality but slower inference
- **Q8_0**: Full precision (not recommended for constrained hardware)

### 2. Context Window Reduction
Reduce context size to improve performance:
- **1024 tokens**: Minimal context for fastest response
- **2048 tokens**: Balanced size for most use cases
- **4096 tokens**: Maximum context when resources allow

### 3. Thread Management
Optimize CPU thread usage:
- **2-4 threads**: For constrained systems
- **6-8 threads**: For balanced performance
- **12+ threads**: For high-end systems

### 4. GPU Offloading
Balance GPU usage for optimal performance:
- **0 layers**: CPU inference only (lowest memory usage)
- **5-10 layers**: Moderate GPU offloading
- **20+ layers**: Heavy GPU offloading (requires more VRAM)

## Command Line Optimization Examples

### Basic Performance Settings
```bash
# For maximum speed on constrained hardware
llama-server \
    --hf-repo Qwen/Qwen3-Coder-30B-Instruct-GGUF \
    --hf-file Qwen3-Coder-30B-Instruct-Q4_K_M.gguf \
    --ctx-size 1024 \
    --threads 4 \
    --n-gpu-layers 0 \
    --temp 0.2 \
    --top-p 0.9 \
    --frequency-penalty 0.5
```

### Memory-Efficient Settings
```bash
# For minimum VRAM usage
llama-server \
    --hf-repo Qwen/Qwen3-Coder-30B-Instruct-GGUF \
    --hf-file Qwen3-Coder-30B-Instruct-Q4_K_M.gguf \
    --ctx-size 512 \
    --threads 2 \
    --n-gpu-layers 0 \
    --temp 0.1 \
    --top-p 0.8 \
    --frequency-penalty 0.3
```

### Balanced Performance Settings
```bash
# For balanced performance and quality
llama-server \
    --hf-repo Qwen/Qwen3-Coder-30B-Instruct-GGUF \
    --hf-file Qwen3-Coder-30B-Instruct-Q4_K_M.gguf \
    --ctx-size 2048 \
    --threads 6 \
    --n-gpu-layers 15 \
    --temp 0.3 \
    --top-p 0.95 \
    --frequency-penalty 0.7
```

## Python Integration Optimization

### Optimized Python Configuration
```python
from llama_cpp import Llama

# Optimized for speed and memory efficiency
llm = Llama(
    model_path="./Qwen3-Coder-30B-Instruct-Q4_K_M.gguf",
    n_ctx=1024,           # Reduced context window
    n_gpu_layers=0,       # CPU only for maximum compatibility
    n_threads=4,          # Balanced threading
    chat_format="llama-3",
    temp=0.2,             # Lower temperature for deterministic responses
    top_p=0.9,            # Top-p sampling
    frequency_penalty=0.5 # Penalty for repetition
)
```

### Memory-Conscious Python Configuration
```python
from llama_cpp import Llama

# Optimized for minimal memory usage
llm = Llama(
    model_path="./Qwen3-Coder-30B-Instruct-Q4_K_M.gguf",
    n_ctx=512,            # Very small context
    n_gpu_layers=0,       # CPU inference
    n_threads=2,          # Minimal threading
    chat_format="llama-3",
    temp=0.1,             # Very low temperature
    top_p=0.8,            # Lower top-p
    frequency_penalty=0.3 # Minimal penalty
)
```

## Advanced Performance Techniques

### 1. Response Caching
Implement response caching to avoid repeated inference for identical prompts:
```bash
# Use cache directory to store previous responses
llama-server \
    --hf-repo Qwen/Qwen3-Coder-30B-Instruct-GGUF \
    --hf-file Qwen3-Coder-30B-Instruct-Q4_K_M.gguf \
    --cache-dir /tmp/llama-cache \
    --ctx-size 1024 \
    --threads 4
```

### 2. Prompt Optimization
Structure prompts to be more efficient:
- Use explicit instruction formatting
- Reduce redundant information
- Break complex tasks into smaller subtasks
- Include only essential context

### 3. Session Management
Use checkpointing to maintain progress:
```bash
# Save session state
/checkpoint save

# Restore session state
/checkpoint restore
```

## Resource Monitoring During Inference

### Memory Usage Monitoring
```bash
# Monitor system memory
free -h

# Monitor GPU usage (if applicable)
nvidia-smi

# Monitor overall system resources
htop
```

### Performance Metrics
Track these metrics during operation:
- Inference time per token
- Memory usage (RSS)
- GPU utilization (if applicable)
- Context window utilization

## Environment Variable Optimization

Set these environment variables for better performance:

```bash
export LLM_THREADS=4
export LLM_CONTEXT_SIZE=1024
export LLM_QUANTIZATION=Q4_K_M
export LLM_GPU_LAYERS=0
export LLM_TEMP=0.2
export LLM_TOP_P=0.9
```

## Workflow Integration

### With Existing Skills
This skill integrates with several existing skills for optimal workflow:

1. **/checkpoint**: Maintain state during long sessions
2. **/frugal-context**: Read code efficiently without loading unnecessary files
3. **/radical-compression**: Keep context windows tight
4. **/silent-mode**: Minimize overhead from verbose outputs

### Recommended Workflow
1. **Setup**: Initialize with optimal parameters for your hardware
2. **Context**: Use `/frugal-context` to efficiently read codebase
3. **Execution**: Run with optimized settings for performance
4. **Compression**: Use `/radical-compression` to maintain tight context
5. **Checkpointing**: Use `/checkpoint` to preserve session state
6. **Monitoring**: Watch resource usage during long sessions

## Troubleshooting

### Common Performance Issues

1. **Slow Response Times**
   - Reduce context size
   - Lower thread count
   - Use CPU inference only
   - Apply Q6_K or Q8_0 quantization for higher quality

2. **Memory Issues**
   - Set `n_gpu_layers=0` for CPU inference
   - Reduce context window to 512 or 1024
   - Use Q4_K_M quantization

3. **Repetitive Output**
   - Increase frequency penalty
   - Lower temperature
   - Reduce top-p value

### Performance Tuning Checklist
- [ ] Set appropriate quantization level
- [ ] Reduce context window to minimum needed
- [ ] Limit parallel threads
- [ ] Use CPU inference if GPU is constrained
- [ ] Apply response caching where possible
- [ ] Monitor resource usage during operation
- [ ] Implement checkpointing for long sessions

## Related Skills
- qwen3-coder-local-setup: For initial setup of Qwen 3 Coder models
- llama-cpp: For GGUF inference management
- checkpoint: For long session state management
- frugal-context: For efficient codebase exploration
- radical-compression: For tight context windows
- silent-mode: For efficient interactions