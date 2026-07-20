---
name: github-repo-finder
description: Search GitHub for existing repositories with similar concepts to avoid duplication and enable forking or code reuse
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Search, Repository, Fork, Code Reuse, Planning]
    related_skills: [github-auth, github-pr-workflow, github-code-review]
---

# GitHub Repository Finder Skill

This skill helps identify existing GitHub repositories with similar concepts to avoid duplication and enable forking or code reuse. It searches for repositories based on keywords and evaluates whether to fork, reuse, or build from scratch.

## Search and Evaluation Process

### 1. Repository Search
When you need to find existing repositories with a similar concept:
- Use GitHub search API to find repositories
- Filter by keywords, topics, and repository quality metrics
- Check if the repository is actively maintained

### 2. Evaluation Criteria
Evaluate existing repositories based on:
- **Code Quality**: Star count, issue count, commit activity
- **Similarity**: Concept match, code structure, and implementation approach
- **Maintainability**: Documentation quality, contribution guidelines
- **Licensing**: Compatible with your project's license

### 3. Decision Framework
Based on the search results, decide:
- **Fork**: When the repository is close to your needs and actively maintained
- **Reuse**: When the repository has reusable components or modules
- **Build**: When no good match exists or the repository doesn't meet requirements

## Usage Examples

### Search for Repositories
```bash
# Search for repositories related to your concept
gh search repos "your concept keyword" --sort=stars --order=desc --limit=10
```

### Evaluate Repository Quality
```bash
# Check if a repository is actively maintained
gh repo view richardkfm/vibes --json owner,name,stars,issues,commits,updatedAt
```

### Check Repository Contents
```bash
# Inspect a repository's structure to determine reusability
gh repo list richardkfm --limit=5
```

## Implementation Flow

1. **Define Concept**: Clearly articulate what you're looking for
2. **Search**: Use GitHub search with appropriate keywords and filters
3. **Filter**: Narrow results by star count, activity, and topic relevance
4. **Evaluate**: Check repository health and code quality
5. **Decide**: Choose between forking, reusing, or building new

## GitHub Search Best Practices

### Keywords for Search
- Use specific technical terms related to your domain
- Include "language:python", "language:javascript", etc. for language-specific searches
- Use "fork:true" to find forks of popular repositories

### Quality Indicators
- Stars ≥ 100 (for quality baseline)
- Last commit within 6 months
- Open issues < 50 (indicating good maintenance)
- Good README and documentation

## Code Reuse Patterns

### For Modules
If a repository has a reusable module:
```bash
# Clone with shallow copy to get only the module
git clone --depth=1 https://github.com/owner/repo.git --branch=main --single-branch
```

### For Templates
If a repository is a good template:
```bash
# Fork the repository
gh repo fork owner/repo
```

## Advanced Planning Integration

When this skill is used in planning:
- Check existing repositories before designing new features
- Reuse code components when possible to save development time
- Create a repository mapping to track similar projects

## Example Usage
```bash
# Example workflow for finding a similar repository
# 1. Search for a specific concept
gh search repos "machine learning model serving" --sort=stars --limit=5

# 2. Evaluate top results
gh repo view owner/repo --json owner,name,stars,issues,commits,updatedAt

# 3. Decide based on evaluation
# If good match: fork or copy relevant parts
# If no good match: build from scratch
```

## Error Handling

If no repositories are found:
- Consider broader search terms
- Check if your concept is too specific
- Consider related concepts with similar functionality

If repositories are found but not actively maintained:
- Evaluate if the code is still usable
- Consider forking and maintaining it yourself
- Look for alternative approaches in related projects