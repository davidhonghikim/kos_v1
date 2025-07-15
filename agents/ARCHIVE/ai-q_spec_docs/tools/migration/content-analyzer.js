#!/usr/bin/env node

/**
 * AI-Q Content Analyzer
 * 
 * Analyzes existing markdown documentation to extract AKU candidates,
 * identify relationships, and generate completion metrics.
 */

const fs = require('fs').promises;
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');
const yaml = require('js-yaml');
const matter = require('gray-matter');

class ContentAnalyzer {
  constructor() {
    this.analysisResults = {
      totalFiles: 0,
      akus: [],
      relationships: new Map(),
      completion: {
        overall: 0,
        byCategory: new Map(),
        byNode: new Map()
      },
      issues: [],
      recommendations: []
    };
    
    this.akuPatterns = {
      capability: /capability|function|feature|tool/i,
      knowledge: /knowledge|wisdom|understanding|insight/i,
      pattern: /pattern|template|recipe|workflow/i,
      workflow: /workflow|process|procedure|routine/i
    };
    
    this.relationshipPatterns = {
      depends: /depends? on|requires?|needs?/gi,
      composes: /composes?|builds?|creates?/gi,
      enhances: /enhances?|improves?|extends?/gi,
      conflicts: /conflicts?|contradicts?|opposes?/gi
    };
  }

  async analyzeContent(contentPath = '../') {
    const spinner = ora('Analyzing AI-Q content...').start();
    
    try {
      // Resolve path relative to this script
      const fullPath = path.resolve(__dirname, contentPath);
      console.log(chalk.blue(`📁 Analyzing content in: ${fullPath}`));
      
      // Scan directory structure
      const structure = await this.scanDirectory(fullPath);
      spinner.text = 'Scanning directory structure...';
      
      // Analyze each file
      spinner.text = 'Analyzing markdown files...';
      const files = await this.findMarkdownFiles(fullPath);
      this.analysisResults.totalFiles = files.length;
      
      for (const file of files) {
        await this.analyzeFile(file);
      }
      
      // Process relationships
      spinner.text = 'Processing relationships...';
      await this.processRelationships();
      
      // Calculate completion metrics
      spinner.text = 'Calculating completion metrics...';
      await this.calculateCompletion();
      
      // Generate recommendations
      spinner.text = 'Generating recommendations...';
      await this.generateRecommendations();
      
      spinner.succeed('Content analysis complete!');
      
      return this.analysisResults;
      
    } catch (error) {
      spinner.fail('Content analysis failed');
      console.error(chalk.red('Error:', error.message));
      throw error;
    }
  }

  async scanDirectory(dirPath) {
    const structure = {
      directories: [],
      files: [],
      totalSize: 0
    };
    
    try {
      const items = await fs.readdir(dirPath, { withFileTypes: true });
      
      for (const item of items) {
        const fullPath = path.join(dirPath, item.name);
        
        if (item.isDirectory()) {
          structure.directories.push({
            name: item.name,
            path: fullPath,
            type: this.categorizeDirectory(item.name)
          });
          
          // Recursively scan subdirectories
          const subStructure = await this.scanDirectory(fullPath);
          structure.directories.push(...subStructure.directories);
          structure.files.push(...subStructure.files);
          structure.totalSize += subStructure.totalSize;
          
        } else if (item.isFile() && item.name.endsWith('.md')) {
          const stats = await fs.stat(fullPath);
          structure.files.push({
            name: item.name,
            path: fullPath,
            size: stats.size,
            modified: stats.mtime
          });
          structure.totalSize += stats.size;
        }
      }
      
    } catch (error) {
      // Skip directories we can't access
      console.warn(chalk.yellow(`Warning: Cannot access ${dirPath}`));
    }
    
    return structure;
  }

  categorizeDirectory(dirName) {
    const categories = {
      foundation: /foundation|core|base/i,
      protocols: /protocol|communication|network/i,
      nodes: /node|specification|griot|tohunga|ronin/i,
      modules: /module|capability|feature/i,
      implementation: /implementation|code|development/i,
      deployment: /deployment|ops|infrastructure/i,
      quality: /quality|testing|validation/i,
      tools: /tool|utility|script/i
    };
    
    for (const [category, pattern] of Object.entries(categories)) {
      if (pattern.test(dirName)) {
        return category;
      }
    }
    
    return 'other';
  }

  async findMarkdownFiles(dirPath) {
    const files = [];
    
    async function scanRecursive(currentPath) {
      try {
        const items = await fs.readdir(currentPath, { withFileTypes: true });
        
        for (const item of items) {
          const fullPath = path.join(currentPath, item.name);
          
          if (item.isDirectory()) {
            await scanRecursive(fullPath);
          } else if (item.isFile() && item.name.endsWith('.md')) {
            files.push(fullPath);
          }
        }
      } catch (error) {
        // Skip inaccessible directories
      }
    }
    
    await scanRecursive(dirPath);
    return files;
  }

  async analyzeFile(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      const { data: frontmatter, content: body } = matter(content);
      
      // Extract AKU candidate
      const aku = await this.extractAKU(filePath, frontmatter, body);
      
      if (aku) {
        this.analysisResults.akus.push(aku);
      }
      
      // Extract relationships
      const relationships = this.extractRelationships(body, aku?.id);
      for (const [type, targets] of Object.entries(relationships)) {
        if (!this.analysisResults.relationships.has(type)) {
          this.analysisResults.relationships.set(type, []);
        }
        this.analysisResults.relationships.get(type).push(...targets);
      }
      
    } catch (error) {
      this.analysisResults.issues.push({
        file: filePath,
        error: error.message,
        type: 'file_analysis_error'
      });
    }
  }

  async extractAKU(filePath, frontmatter, body) {
    const relativePath = path.relative(path.resolve(__dirname, '../'), filePath);
    const fileName = path.basename(filePath, '.md');
    
    // Determine AKU type based on content and location
    const akuType = this.determineAKUType(filePath, frontmatter, body);
    
    if (!akuType) {
      return null; // Not an AKU candidate
    }
    
    // Generate AKU ID
    const akuId = this.generateAKUId(relativePath, fileName);
    
    // Extract title and description
    const title = frontmatter.title || this.extractTitle(body) || fileName;
    const description = frontmatter.description || this.extractDescription(body);
    
    // Calculate completion
    const completion = this.calculateFileCompletion(frontmatter, body);
    
    // Extract capabilities
    const capabilities = this.extractCapabilities(body);
    
    // Extract dependencies
    const dependencies = this.extractDependencies(body);
    
    return {
      id: akuId,
      type: akuType,
      title: title,
      description: description,
      status: frontmatter.status || 'draft',
      completion: completion,
      dependencies: dependencies,
      capabilities: capabilities,
      implementations: this.extractImplementations(filePath, body),
      relationships: {
        composes: [],
        requires: dependencies,
        enhances: [],
        conflicts: []
      },
      metadata: {
        filePath: relativePath,
        created: frontmatter.created || new Date().toISOString(),
        updated: frontmatter.updated || new Date().toISOString(),
        author: frontmatter.author || 'unknown',
        version: frontmatter.version || '1.0.0'
      }
    };
  }

  determineAKUType(filePath, frontmatter, body) {
    // Check frontmatter first
    if (frontmatter.type && this.akuPatterns[frontmatter.type]) {
      return frontmatter.type;
    }
    
    // Check file path patterns
    const pathLower = filePath.toLowerCase();
    if (pathLower.includes('capability') || pathLower.includes('feature')) {
      return 'capability';
    }
    if (pathLower.includes('knowledge') || pathLower.includes('wisdom')) {
      return 'knowledge';
    }
    if (pathLower.includes('pattern') || pathLower.includes('template')) {
      return 'pattern';
    }
    if (pathLower.includes('workflow') || pathLower.includes('process')) {
      return 'workflow';
    }
    
    // Check content patterns
    const contentLower = body.toLowerCase();
    for (const [type, pattern] of Object.entries(this.akuPatterns)) {
      if (pattern.test(contentLower)) {
        return type;
      }
    }
    
    // Default based on directory structure
    const dirName = path.dirname(filePath).split(path.sep).pop();
    if (dirName === 'modules' || dirName === 'capabilities') {
      return 'capability';
    }
    if (dirName === 'foundation' || dirName === 'principles') {
      return 'knowledge';
    }
    
    return null; // Not an AKU candidate
  }

  generateAKUId(relativePath, fileName) {
    // Convert file path to AKU ID format
    const parts = relativePath.split(path.sep);
    const domain = parts[0] || 'aiq';
    const category = parts[1] || 'general';
    const name = fileName.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase();
    
    return `aku://${domain}/${category}/${name}/v1.0`;
  }

  extractTitle(body) {
    // Look for first heading
    const headingMatch = body.match(/^#\s+(.+)$/m);
    return headingMatch ? headingMatch[1].trim() : null;
  }

  extractDescription(body) {
    // Look for first paragraph after frontmatter
    const paragraphs = body.split('\n\n').filter(p => p.trim());
    for (const paragraph of paragraphs) {
      const clean = paragraph.replace(/^#+\s+/, '').trim();
      if (clean.length > 20 && clean.length < 500) {
        return clean;
      }
    }
    return null;
  }

  calculateFileCompletion(frontmatter, body) {
    let score = 0;
    
    // Check required fields
    if (frontmatter.title) score += 20;
    if (frontmatter.description) score += 20;
    if (frontmatter.status) score += 10;
    if (frontmatter.version) score += 10;
    
    // Check content quality
    if (body.length > 500) score += 20;
    if (body.includes('##')) score += 10; // Has sections
    if (body.includes('```')) score += 10; // Has code examples
    
    return Math.min(score, 100);
  }

  extractCapabilities(body) {
    const capabilities = {
      input: [],
      output: [],
      performance: 'unknown',
      reliability: 0.8
    };
    
    // Look for capability patterns
    const inputMatch = body.match(/input[s]?:\s*([^\n]+)/gi);
    if (inputMatch) {
      capabilities.input = inputMatch.map(m => m.replace(/input[s]?:\s*/i, '').trim());
    }
    
    const outputMatch = body.match(/output[s]?:\s*([^\n]+)/gi);
    if (outputMatch) {
      capabilities.output = outputMatch.map(m => m.replace(/output[s]?:\s*/i, '').trim());
    }
    
    return capabilities;
  }

  extractDependencies(body) {
    const dependencies = [];
    
    // Look for dependency patterns
    const depMatches = body.match(/(?:depends? on|requires?|needs?)\s+([^\n]+)/gi);
    if (depMatches) {
      for (const match of depMatches) {
        const deps = match.replace(/(?:depends? on|requires?|needs?)\s+/i, '').split(',').map(d => d.trim());
        dependencies.push(...deps);
      }
    }
    
    return dependencies;
  }

  extractImplementations(filePath, body) {
    const implementations = [];
    
    // Look for implementation patterns
    const implMatches = body.match(/```(\w+)[\s\S]*?```/g);
    if (implMatches) {
      for (const match of implMatches) {
        const langMatch = match.match(/```(\w+)/);
        if (langMatch) {
          implementations.push({
            language: langMatch[1],
            path: filePath.replace('.md', `.${langMatch[1]}`),
            tests: filePath.replace('.md', `.test.${langMatch[1]}`)
          });
        }
      }
    }
    
    return implementations;
  }

  extractRelationships(body, akuId) {
    const relationships = {
      depends: [],
      composes: [],
      enhances: [],
      conflicts: []
    };
    
    // Look for relationship patterns in content
    for (const [type, pattern] of Object.entries(this.relationshipPatterns)) {
      const matches = body.match(pattern);
      if (matches) {
        // Extract relationship targets (simplified)
        relationships[type] = matches.map(m => m.replace(pattern, '').trim());
      }
    }
    
    return relationships;
  }

  async processRelationships() {
    // Process and validate relationships
    for (const [type, targets] of this.analysisResults.relationships) {
      const validTargets = targets.filter(target => {
        // Check if target AKU exists
        return this.analysisResults.akus.some(aku => 
          aku.id.includes(target) || aku.title.toLowerCase().includes(target.toLowerCase())
        );
      });
      
      this.analysisResults.relationships.set(type, validTargets);
    }
  }

  async calculateCompletion() {
    if (this.analysisResults.akus.length === 0) {
      this.analysisResults.completion.overall = 0;
      return;
    }
    
    // Calculate overall completion
    const totalCompletion = this.analysisResults.akus.reduce((sum, aku) => sum + aku.completion, 0);
    this.analysisResults.completion.overall = Math.round(totalCompletion / this.analysisResults.akus.length);
    
    // Calculate by category
    for (const aku of this.analysisResults.akus) {
      const category = aku.type;
      if (!this.analysisResults.completion.byCategory.has(category)) {
        this.analysisResults.completion.byCategory.set(category, []);
      }
      this.analysisResults.completion.byCategory.get(category).push(aku.completion);
    }
    
    // Calculate averages by category
    for (const [category, completions] of this.analysisResults.completion.byCategory) {
      const avg = completions.reduce((sum, c) => sum + c, 0) / completions.length;
      this.analysisResults.completion.byCategory.set(category, Math.round(avg));
    }
    
    // Calculate by node (extract from AKU ID)
    for (const aku of this.analysisResults.akus) {
      const nodeMatch = aku.id.match(/aku:\/\/([^\/]+)/);
      if (nodeMatch) {
        const node = nodeMatch[1];
        if (!this.analysisResults.completion.byNode.has(node)) {
          this.analysisResults.completion.byNode.set(node, []);
        }
        this.analysisResults.completion.byNode.get(node).push(aku.completion);
      }
    }
    
    // Calculate averages by node
    for (const [node, completions] of this.analysisResults.completion.byNode) {
      const avg = completions.reduce((sum, c) => sum + c, 0) / completions.length;
      this.analysisResults.completion.byNode.set(node, Math.round(avg));
    }
  }

  async generateRecommendations() {
    const recommendations = [];
    
    // Low completion AKUs
    const lowCompletion = this.analysisResults.akus.filter(aku => aku.completion < 50);
    if (lowCompletion.length > 0) {
      recommendations.push({
        type: 'low_completion',
        message: `${lowCompletion.length} AKUs have completion < 50%`,
        items: lowCompletion.map(aku => aku.id)
      });
    }
    
    // Missing relationships
    const noRelationships = this.analysisResults.akus.filter(aku => 
      aku.relationships.requires.length === 0 && 
      aku.relationships.composes.length === 0
    );
    if (noRelationships.length > 0) {
      recommendations.push({
        type: 'missing_relationships',
        message: `${noRelationships.length} AKUs have no relationships defined`,
        items: noRelationships.map(aku => aku.id)
      });
    }
    
    // Missing implementations
    const noImplementations = this.analysisResults.akus.filter(aku => 
      aku.implementations.length === 0
    );
    if (noImplementations.length > 0) {
      recommendations.push({
        type: 'missing_implementations',
        message: `${noImplementations.length} AKUs have no implementations`,
        items: noImplementations.map(aku => aku.id)
      });
    }
    
    this.analysisResults.recommendations = recommendations;
  }

  generateReport() {
    const report = {
      summary: {
        totalFiles: this.analysisResults.totalFiles,
        akusFound: this.analysisResults.akus.length,
        overallCompletion: this.analysisResults.completion.overall,
        issuesFound: this.analysisResults.issues.length,
        recommendations: this.analysisResults.recommendations.length
      },
      akus: this.analysisResults.akus,
      relationships: Object.fromEntries(this.analysisResults.relationships),
      completion: {
        overall: this.analysisResults.completion.overall,
        byCategory: Object.fromEntries(this.analysisResults.completion.byCategory),
        byNode: Object.fromEntries(this.analysisResults.completion.byNode)
      },
      issues: this.analysisResults.issues,
      recommendations: this.analysisResults.recommendations
    };
    
    return report;
  }

  async saveReport(outputPath = './analysis-report.json') {
    const report = this.generateReport();
    await fs.writeFile(outputPath, JSON.stringify(report, null, 2));
    console.log(chalk.green(`📊 Analysis report saved to: ${outputPath}`));
  }
}

// CLI interface
async function main() {
  const analyzer = new ContentAnalyzer();
  
  try {
    // Parse command line arguments
    const args = process.argv.slice(2);
    const contentPath = args[0] || '../';
    const outputPath = args[1] || './analysis-report.json';
    
    console.log(chalk.blue.bold('🔍 AI-Q Content Analyzer'));
    console.log(chalk.gray('Analyzing markdown content for AKU candidates...\n'));
    
    // Run analysis
    await analyzer.analyzeContent(contentPath);
    
    // Generate and save report
    await analyzer.saveReport(outputPath);
    
    // Display summary
    const report = analyzer.generateReport();
    console.log(chalk.green.bold('\n📊 Analysis Summary:'));
    console.log(`  Files analyzed: ${report.summary.totalFiles}`);
    console.log(`  AKUs found: ${report.summary.akusFound}`);
    console.log(`  Overall completion: ${report.summary.overallCompletion}%`);
    console.log(`  Issues found: ${report.summary.issuesFound}`);
    console.log(`  Recommendations: ${report.summary.recommendations}`);
    
    if (report.recommendations.length > 0) {
      console.log(chalk.yellow.bold('\n💡 Key Recommendations:'));
      for (const rec of report.recommendations.slice(0, 3)) {
        console.log(`  • ${rec.message}`);
      }
    }
    
  } catch (error) {
    console.error(chalk.red('Analysis failed:', error.message));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = ContentAnalyzer; 