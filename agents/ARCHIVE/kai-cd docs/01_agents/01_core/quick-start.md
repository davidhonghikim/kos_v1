---
title: "Agent Quick Start Guide"
description: "5-minute onboarding guide for new AI agents - essential rules, workflows, and immediate productivity"
type: "guide"
status: "current"
priority: "critical"
last_updated: "2025-01-27"
version: "1.0.0"
related_docs: [
  "01_Agent_Rules.md",
  "02_Agent_System_Prompt.md",
  "15_Documentation_Protocol.md"
]
agent_notes: "NEW AGENT START HERE - Essential information for immediate productivity without overwhelm"
---

# Agent Quick Start Guide ⚡

**🎯 Goal: Get you productive in under 5 minutes**

## Agent Context
**For AI Agents**: This is your fast-track onboarding. Read this first before diving into detailed documentation. Contains the 20% of information you need for 80% of effectiveness.

**Implementation Notes**: Distilled from 20+ detailed documents into essential-only information. Links to full documentation when needed.
**Quality Requirements**: Must follow the three core rules below. Everything else is optional until needed.
**Integration Points**: Gateway to full agent documentation system. Designed for immediate action.

---

## ⚡ **3-Minute Essentials**

### **🚨 Core Rules (30 seconds)**
1. **Two-Edit Rule**: After 1-2 significant code changes, STOP and review your work
2. **Build Verification**: Run `npm run build` after changes to verify stability  
3. **User Confirmation**: Only the user can mark work as "complete" - not you

### **🎯 Immediate Actions (2 minutes)**
```bash
# 1. Check current project status (30 seconds)
cd /Users/danger/CascadeProjects/kai-cd
npm run build  # Verify system is working

# 2. Check for immediate issues (30 seconds)
grep -r "TODO\|FIXME\|BUG" src/ | head -5

# 3. Review current task context (60 seconds)
cat documentation/01_agents/02_planning/current-execution-plan.md | head -20
```

### **🛠️ Your Toolkit (30 seconds)**
- **Build Command**: `npm run build` (always verify)
- **Documentation Root**: `documentation/` (everything organized here)
- **Agent Rules**: `documentation/01_agents/01_core/agent-rules.md` (full workflow)
- **Quality Protocol**: `documentation/01_agents/04_quality/documentation-protocol.md` (standards)

---

## 🚀 **Ready to Work (2 minutes)**

### **For Code Issues**
1. Read user request carefully
2. Check `documentation/02_analysis/` for known issues
3. Make small changes (1-2 files max)
4. **STOP** - Review your changes completely
5. Run `npm run build` to verify
6. Continue or fix issues found

### **For Documentation Work** 
1. Check `documentation/01_agents/04_quality/documentation-protocol.md`
2. Use proper frontmatter format (see examples in any doc)
3. Add Agent Context blocks to new documents
4. **Verify** all file references work before claiming completion

### **For New Features**
1. Review existing architecture in `documentation/04_current/`
2. Check service patterns in `src/connectors/definitions/`
3. Follow established patterns (don't reinvent)
4. Test thoroughly before marking complete

---

## 📋 **When You Need More**

### **🚨 If Things Break**
→ **[01_Agent_Rules.md](./01_Agent_Rules.md)** - Full debugging workflow

### **📝 For Documentation Standards**  
→ **[15_Documentation_Protocol.md](./15_Documentation_Protocol.md)** - Complete quality system

### **🔄 For Project Context**
→ **[03_Execution_Plan.md](./03_Execution_Plan.md)** - Current project status
→ **[16_Foundation_Complete_Summary.md](./16_Foundation_Complete_Summary.md)** - What's been achieved

### **🤝 For Handoffs**
→ **[20_Handoff_Documentation_System_Organization.md](./20_Handoff_Documentation_System_Organization.md)** - Current handoff status

---

## 🎯 **Success Pattern**

### **✅ You're Doing Great If:**
- You stop and review after 1-2 changes
- Build passes after your modifications  
- You ask user to verify final results
- You update documentation when you make changes

### **⚠️ Red Flags to Avoid:**
- Making many changes without verification
- Skipping build checks
- Claiming work is "done" without user confirmation
- Breaking existing functionality

---

## 💡 **Pro Tips**

### **Efficiency Hacks**
- Use parallel tool calls for reading multiple files
- Always check existing patterns before creating new ones
- When stuck, check `documentation/02_analysis/` for known solutions
- Update handoff docs as you work (helps next agent)

### **Quality Shortcuts**
- Copy frontmatter from similar documents (saves time)
- Use `grep -r "pattern" documentation/` to find examples
- Check cross-references: `test -f path/to/file.md`
- Simple verification: `npm run build && echo "✅ Good to go"`

---

## 🎉 **You're Ready!**

**✅ Essential knowledge acquired**  
**✅ Toolkit accessible**  
**✅ Safety protocols understood**  
**✅ Quality standards clear**

### **🚀 Start Working With Confidence**

You now know the 20% that covers 80% of situations. The full documentation system is there when you need depth, but you're ready to be productive immediately.

**Remember**: Stop, review, verify, get user confirmation. Everything else builds on these fundamentals.

---

**Quick Start Complete** ✅ **Time to First Productivity**: Under 5 minutes 🚀 