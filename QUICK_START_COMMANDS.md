# Quick Start Commands Reference

## 🚀 Immediate Setup (5 minutes)

```bash
# Navigate to project
cd /Users/abivarma/Personal_projects/RLM

# Configure Git
git config user.name "Abivarma"
git config user.email "your-email@example.com"  # Replace with your email

# Verify configuration
git config --list | grep user
```

## 📦 GitHub Repository Creation (10 minutes)

### Option 1: GitHub Web Interface

1. Go to: https://github.com/new
2. Repository name: `rlm-fraud-detection`
3. Description: `Reduce LLM API costs by 70% with Recursive Language Models`
4. Public repository
5. Don't initialize with README, .gitignore, or license (we have these)
6. Click "Create repository"

Then run:
```bash
git remote add origin https://github.com/Abivarma/rlm-fraud-detection.git
git branch -M main
git push -u origin main
```

### Option 2: GitHub CLI (Faster)

```bash
# Install GitHub CLI if needed
brew install gh  # macOS
# or download from: https://cli.github.com/

# Login
gh auth login

# Create and push
gh repo create Abivarma/rlm-fraud-detection \
  --public \
  --source=. \
  --description="Reduce LLM API costs by 70% with Recursive Language Models" \
  --remote=origin

git push -u origin main
```

## ✅ Verify Setup

```bash
# Check repository status
git status

# View recent commits
git log -1 --format='%an %ae %s'

# List files to be pushed
git ls-files

# Check remote
git remote -v
```

## 🧪 Test System Locally

```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Run tests
pytest tests/ -v

# Run demo
python3 demo_rlm_workflow.py

# Start dashboard
streamlit run app/ui/streamlit_dashboard.py
# Open: http://localhost:8501
```

## 📝 Update Personal Information

Edit these files to add your details:

```bash
# Update README.md
# Replace placeholders:
# - [Add your LinkedIn]
# - [Add your Medium profile]  
# - [Add your email]

# Update with your actual URLs
sed -i '' 's/\[Add your LinkedIn\]/https:\/\/linkedin.com\/in\/yourprofile/g' README.md
sed -i '' 's/\[Add your Medium profile\]/https:\/\/medium.com\/@yourusername/g' README.md
sed -i '' 's/\[Add your email\]/your.email@example.com/g' README.md

# Commit changes
git add README.md
git commit -m "Update personal contact information"
git push
```

## 🎨 Generate Cover Images

Use the prompts in BLOG_SERIES_PLAN.md with:
- DALL-E 3: https://labs.openai.com/
- Midjourney: https://midjourney.com/
- Leonardo AI: https://leonardo.ai/

Save images as:
- `blogs/images/cover-part1.png`
- `blogs/images/cover-part2.png`
- `blogs/images/cover-part3.png`
- `blogs/images/cover-part4.png`

## 📊 Extract Real Data

```bash
# View test results
cat TEST_REPORT.md

# Extract key metrics (already documented):
# - Token usage: Naive 5,066, RAG 1,356, RLM 1,495
# - Cost: Naive $0.0164, RAG $0.0114, RLM $0.0049
# - Token savings: RAG 73.2%, RLM 70.5%
# - Annual savings: $41,975 at 10K analyses/day
```

## 📚 Write Blog Posts

For each part, follow this structure:

```bash
# Create blog directory
mkdir -p blogs/part1

# Write blog post
# Use outline from BLOG_SERIES_PLAN.md
# Use navigation template from blogs/blog_template_with_links.md

# Structure:
# 1. Header (author, series info)
# 2. Navigation (series position, links)
# 3. Article content (3,500-4,200 words)
# 4. Footer (GitHub link, previous/next articles, author bio)
```

## 🚀 Publishing Workflow

### Week 1: Publish Part 1
```bash
# 1. Write Part 1 (3,800 words)
# 2. Generate cover image
# 3. Publish on Medium
# 4. Get Medium URL

# 5. Update navigation links in README
# Replace: blogs/part1/ 
# With: https://medium.com/@yourusername/actual-url-part1

git add README.md
git commit -m "Add Part 1 Medium link"
git push

# 6. Share on social media
```

### Week 2: Publish Part 2
```bash
# Same process for Part 2
# Update Part 1 to link to Part 2
# Update README with Part 2 link
```

### Week 3: Publish Part 3
```bash
# Same process for Part 3
# Update previous articles to link to Part 3
```

### Week 4: Publish Part 4
```bash
# Same process for Part 4
# Update all navigation links
# Series complete!
```

## 📈 Track Metrics

### GitHub Repository
```bash
# View stars and forks
gh repo view Abivarma/rlm-fraud-detection

# View traffic (on GitHub website)
# https://github.com/Abivarma/rlm-fraud-detection/graphs/traffic
```

### Medium Articles
- Views, read ratio, claps
- Member reading time (paywall earnings)
- Referrers (where traffic comes from)
- Story stats dashboard

## 🔧 Maintenance Commands

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/new-feature

# Make changes, then:
git add .
git commit -m "Description of changes

Author: Abivarma"
git push origin feature/new-feature

# Create PR
gh pr create --title "Feature: Description" --body "Details"

# Merge after review
gh pr merge <pr-number>
```

## 📞 Community Engagement

### Respond to Issues
```bash
# List open issues
gh issue list

# View issue
gh issue view <issue-number>

# Comment on issue
gh issue comment <issue-number> --body "Thanks for reporting..."

# Close issue
gh issue close <issue-number>
```

### Manage Discussions
```bash
# On GitHub website:
# https://github.com/Abivarma/rlm-fraud-detection/discussions
```

## 🎯 Success Checklist

### Day 1
- [ ] Git configured
- [ ] GitHub repository created
- [ ] Code pushed
- [ ] Topics added
- [ ] About section configured

### Week 1
- [ ] Part 1 blog written
- [ ] Cover image generated
- [ ] Published on Medium
- [ ] Shared on social media

### Week 2-4
- [ ] Parts 2-4 published
- [ ] All navigation links updated
- [ ] Responding to comments
- [ ] Tracking metrics

### Ongoing
- [ ] Monitor GitHub stars/forks
- [ ] Respond to issues/discussions
- [ ] Update code based on feedback
- [ ] Share success stories

---

**Quick Reference**: SETUP_COMPLETE_SUMMARY.md
**Detailed Guide**: GITHUB_SETUP_GUIDE.md
**Blog Strategy**: BLOG_SERIES_PLAN.md

**Repository**: https://github.com/Abivarma/rlm-fraud-detection
**Author**: Abivarma
