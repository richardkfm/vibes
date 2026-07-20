---
name: qwen3-coder-local-setup
description: Local setup and optimization guide for Qwen 3 Coder model
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [qwen3, coder, local, gguf, optimization]
---

# Qwen 3 Coder Local Setup and Optimization Guide

## Overview
This skill provides guidance for setting up and optimizing Qwen 3 Coder for local inference with limited resources. It focuses on efficient memory usage, proper quantization, and workflow optimization.

## When to Use This Skill
- Setting up Qwen 3 Coder for local inference
- Optimizing performance on resource-constrained hardware
- Managing memory usage with GGUF models
- Working with local LLMs in constrained environments

## Setup Recommendations

### Hardware Considerations
- **CPU**: Minimum 8 cores recommended for decent performance
- **RAM**: 16GB minimum, 32GB preferred for full context windows
- **VRAM**: 8GB minimum for GGUF inference (Q4 quantization)
- **Storage**: SSD recommended for faster model loading

### Model Quantization Guide
For memory-constrained environments, use these quantization levels:

1. **Q4_K_M** - Good balance of quality vs. size (recommended for 8GB VRAM)
2. **Q5_K_M** - Better quality at cost of more memory (recommended for 16GB VRAM)
3. **Q6_K** - Highest quality with more memory requirement
4. **Q8_0** - Full precision (if you have sufficient VRAM)

### Installation Steps

1. **Install llama.cpp**:
```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
make
```

2. **Download Qwen 3 Coder model**:
```bash
# Example for Qwen 3 Coder model
llama-cli -hf Qwen/Qwen3-Coder-3B-Instruct-GGUF:Q4_K_M
```

## Optimization Strategies for Low-Resource Environments

### Memory Management
- Use the lowest quantization that maintains acceptable quality
- Reduce context window size with `--ctx-size` parameter
- Limit parallel threads with `--threads` parameter
- Use GPU offloading selectively (set `--n-gpu-layers` appropriately)

### Command Examples
```bash
# Basic inference with optimized settings
llama-server \
    --hf-repo Qwen/Qwen3-Coder-3B-Instruct-GGUF \
    --hf-file Qwen3-Coder-3B-Instruct-Q4_K_M.gguf \
    --ctx-size 2048 \
    --threads 4 \
    --n-gpu-layers 35

# For very constrained environments
llama-server \
    --hf-repo Qwen/Qwen3-Coder-3B-Instruct-GGUF \
    --hf-file Qwen3-Coder-3B-Instruct-Q4_K_M.gguf \
    --ctx-size 1024 \
    --threads 2 \
    --n-gpu-layers 0
```

### Python Integration
```python
from llama_cpp import Llama

# For low-memory environments
llm = Llama(
    model_path="./Qwen3-Coder-3B-Instruct-Q4_K_M.gguf",
    n_ctx=1024,  # Reduced context
    n_gpu_layers=0,  # CPU only
    n_threads=2,   # Reduced threads
    chat_format="llama-3"
)
```

## Workflow Optimization

### Use Existing Skills Together
1. **checkpoint** - Maintain state during long coding sessions (Hermes built-in)
2. **frugal-context** - Minimize what's loaded into context (via vibes-skills)
3. **radical-compression** - Keep context windows tight (via vibes-skills)
4. **silent-mode** - Reduce overhead from verbose outputs (via vibes-skills)

### Best Practices
- Always test with smaller context windows first
- Monitor memory usage with `htop` or similar tools
- Use `--verbose` flag only when debugging
- Implement proper model caching to avoid repeated loads

## Troubleshooting

### Common Issues
1. **Out of Memory**: Reduce `--ctx-size` and `--threads`
2. **Slow Performance**: Ensure GPU offloading is working properly
3. **Model Not Found**: Verify model path and file extensions
4. **Context Limit Exceeded**: Use `/frugal-context` skill

## Resource Monitoring Commands
```bash
# Monitor memory usage
free -h

# Monitor GPU usage (if applicable)
nvidia-smi

# Monitor system resources
htop
```

## Related Skills
- llama-cpp: For GGUF inference management
- checkpoint: For long session state management
- frugal-context: For efficient context usage
- radical-compression: For tight context windows