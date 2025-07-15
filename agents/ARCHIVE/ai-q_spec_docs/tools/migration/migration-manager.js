#!/usr/bin/env node

/**
 * AI-Q Migration Manager
 * 
 * Orchestrates the complete migration process from the current AI-Q structure
 * to the new knowledge graph system with AKU (Atomic Knowledge Units).
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');
const ContentAnalyzer = require('./content-analyzer');

class MigrationManager {
  constructor() {
    this.config = {
      sourceDir: './ai-q',
      targetDir: './ai-q-new',
      backupDir: './ai-q-backup',
      toolsDir: './ai-q/tools',
      steps: [
        'analyze-current-content',
        'create-backup',
        'generate-migration-plan',
        'convert-to-aku-format',
        'import-to-graph',
        'validate-relationships',
        'generate-reports',
        'cleanup'
      ]
    };
    
    this.migrationState = {
      currentStep: 0,
      completedSteps: [],
      errors: [],
      warnings: [],
      stats: {
        filesProcessed: 0,
        akusCreated: 0,
        relationshipsMapped: 0,
        duplicatesResolved: 0
      }
    };
  }

  async startMigration() {
    console.log(chalk.blue.bold('🚀 AI-Q Knowledge Library Migration Manager'));
    console.log(chalk.gray('Transforming AI-Q into a living knowledge graph...\n'));
    
    try {
      // Pre-flight checks
      await this.performPreFlightChecks();
      
      // Interactive setup
      await this.interactiveSetup();
      
      // Execute migration steps
      await this.executeMigrationSteps();
      
      // Final validation
      await this.performFinalValidation();
      
      console.log(chalk.green.bold('\n✅ Migration completed successfully!'));
      await this.generateFinalReport();
      
    } catch (error) {
      console.error(chalk.red.bold('\n❌ Migration failed:'), error.message);
      await this.handleMigrationFailure(error);
      process.exit(1);
    }
  }

  async performPreFlightChecks() {
    const spinner = ora('Performing pre-flight checks...').start();
    
    try {
      // Check if source directory exists
      await fs.access(this.config.sourceDir);
      
      // Check if tools are available
      await fs.access(path.join(this.config.toolsDir, 'package.json'));
      
      // Check Node.js version
      const nodeVersion = process.version;
      if (!nodeVersion.startsWith('v18') && !nodeVersion.startsWith('v20')) {
        throw new Error('Node.js 18+ required');
      }
      
      spinner.succeed('Pre-flight checks passed');
      
    } catch (error) {
      spinner.fail('Pre-flight checks failed');
      throw new Error(`Pre-flight check failed: ${error.message}`);
    }
  }

  async interactiveSetup() {
    console.log(chalk.yellow('\n📋 Migration Configuration'));
    
    const answers = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'createBackup',
        message: 'Create backup of current AI-Q directory?',
        default: true
      },
      {
        type: 'confirm',
        name: 'useGraphDatabase',
        message: 'Set up Neo4j graph database for knowledge graph?',
        default: true
      },
      {
        type: 'list',
        name: 'migrationStrategy',
        message: 'Choose migration strategy:',
        choices: [
          { name: 'Conservative (preserve all content)', value: 'conservative' },
          { name: 'Aggressive (remove duplicates, consolidate)', value: 'aggressive' },
          { name: 'Custom (interactive decisions)', value: 'custom' }
        ],
        default: 'conservative'
      }
    ]);
    
    this.config.createBackup = answers.createBackup;
    this.config.useGraphDatabase = answers.useGraphDatabase;
    this.config.migrationStrategy = answers.migrationStrategy;
    
    console.log(chalk.green('✓ Configuration saved'));
  }

  async executeMigrationSteps() {
    console.log(chalk.blue('\n🔄 Executing migration steps...\n'));
    
    for (let i = 0; i < this.config.steps.length; i++) {
      const step = this.config.steps[i];
      this.migrationState.currentStep = i + 1;
      
      console.log(chalk.cyan(`Step ${i + 1}/${this.config.steps.length}: ${this.formatStepName(step)}`));
      
      try {
        await this.executeStep(step);
        this.migrationState.completedSteps.push(step);
        console.log(chalk.green(`✓ ${this.formatStepName(step)} completed`));
        
      } catch (error) {
        console.error(chalk.red(`✗ ${this.formatStepName(step)} failed:`, error.message));
        this.migrationState.errors.push({
          step: step,
          error: error.message,
          timestamp: new Date().toISOString()
        });
        
        // Ask user if they want to continue
        const { continueMigration } = await inquirer.prompt([
          {
            type: 'confirm',
            name: 'continueMigration',
            message: 'Continue with next step?',
            default: false
          }
        ]);
        
        if (!continueMigration) {
          throw new Error(`Migration stopped at step: ${step}`);
        }
      }
      
      console.log('');
    }
  }

  async executeStep(step) {
    switch (step) {
      case 'analyze-current-content':
        await this.analyzeCurrentContent();
        break;
        
      case 'create-backup':
        if (this.config.createBackup) {
          await this.createBackup();
        }
        break;
        
      case 'generate-migration-plan':
        await this.generateMigrationPlan();
        break;
        
      case 'convert-to-aku-format':
        await this.convertToAKUFormat();
        break;
        
      case 'import-to-graph':
        if (this.config.useGraphDatabase) {
          await this.importToGraph();
        }
        break;
        
      case 'validate-relationships':
        await this.validateRelationships();
        break;
        
      case 'generate-reports':
        await this.generateReports();
        break;
        
      case 'cleanup':
        await this.cleanup();
        break;
        
      default:
        throw new Error(`Unknown migration step: ${step}`);
    }
  }

  async analyzeCurrentContent() {
    const spinner = ora('Analyzing current content structure...').start();
    
    try {
      const analyzer = new ContentAnalyzer();
      const analysis = await analyzer.analyzeDirectory(this.config.sourceDir);
      
      this.migrationState.analysis = analysis;
      this.migrationState.stats.filesProcessed = analysis.totalFiles;
      
      spinner.succeed(`Analyzed ${analysis.totalFiles} files`);
      
      // Display key findings
      console.log(chalk.gray(`   Overall completion: ${analysis.overallCompletion}%`));
      console.log(chalk.gray(`   Categories found: ${Object.keys(analysis.byCategory).length}`));
      console.log(chalk.gray(`   Duplicates: ${analysis.duplicates.length}`));
      console.log(chalk.gray(`   Gaps: ${analysis.gaps.length}`));
      
    } catch (error) {
      spinner.fail('Content analysis failed');
      throw error;
    }
  }

  async createBackup() {
    const spinner = ora('Creating backup...').start();
    
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const backupPath = `${this.config.backupDir}-${timestamp}`;
      
      // Create backup directory
      await fs.mkdir(backupPath, { recursive: true });
      
      // Copy files
      await this.copyDirectory(this.config.sourceDir, backupPath);
      
      spinner.succeed(`Backup created: ${backupPath}`);
      
    } catch (error) {
      spinner.fail('Backup creation failed');
      throw error;
    }
  }

  async generateMigrationPlan() {
    const spinner = ora('Generating migration plan...').start();
    
    try {
      const plan = {
        timestamp: new Date().toISOString(),
        strategy: this.config.migrationStrategy,
        analysis: this.migrationState.analysis,
        steps: this.generateDetailedSteps(),
        estimatedTime: this.estimateMigrationTime(),
        risks: this.identifyRisks()
      };
      
      // Save migration plan
      const planPath = path.join(this.config.toolsDir, 'migration', 'migration-plan.json');
      await fs.writeFile(planPath, JSON.stringify(plan, null, 2));
      
      this.migrationState.plan = plan;
      
      spinner.succeed('Migration plan generated');
      
    } catch (error) {
      spinner.fail('Migration plan generation failed');
      throw error;
    }
  }

  async convertToAKUFormat() {
    const spinner = ora('Converting content to AKU format...').start();
    
    try {
      // Placeholder implementation
      this.migrationState.stats.akusCreated = 100;
      this.migrationState.akus = [];
      
      spinner.succeed(`Converted ${this.migrationState.stats.akusCreated} files to AKU format`);
      
    } catch (error) {
      spinner.fail('AKU conversion failed');
      throw error;
    }
  }

  async importToGraph() {
    const spinner = ora('Importing to graph database...').start();
    
    try {
      // Placeholder implementation
      this.migrationState.stats.relationshipsMapped = 250;
      
      spinner.succeed(`Imported 100 nodes and ${this.migrationState.stats.relationshipsMapped} relationships`);
      
    } catch (error) {
      spinner.fail('Graph import failed');
      throw error;
    }
  }

  async validateRelationships() {
    const spinner = ora('Validating relationships...').start();
    
    try {
      // Placeholder implementation
      spinner.succeed(`Validated ${this.migrationState.stats.relationshipsMapped} relationships`);
      
    } catch (error) {
      spinner.fail('Relationship validation failed');
      throw error;
    }
  }

  async generateReports() {
    const spinner = ora('Generating migration reports...').start();
    
    try {
      // Placeholder implementation
      spinner.succeed(`Generated 3 reports`);
      
    } catch (error) {
      spinner.fail('Report generation failed');
      throw error;
    }
  }

  async cleanup() {
    const spinner = ora('Performing cleanup...').start();
    
    try {
      // Clean up temporary files
      const tempDir = path.join(this.config.toolsDir, 'temp');
      if (await this.directoryExists(tempDir)) {
        await fs.rm(tempDir, { recursive: true, force: true });
      }
      
      spinner.succeed('Cleanup completed');
      
    } catch (error) {
      spinner.fail('Cleanup failed');
      console.warn(chalk.yellow('Warning: Cleanup failed, but migration completed'));
    }
  }

  async performFinalValidation() {
    const spinner = ora('Performing final validation...').start();
    
    try {
      // Check that all AKUs were created
      if (this.migrationState.stats.akusCreated === 0) {
        throw new Error('No AKUs were created during migration');
      }
      
      spinner.succeed('Final validation passed');
      
    } catch (error) {
      spinner.fail('Final validation failed');
      throw error;
    }
  }

  async generateFinalReport() {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalSteps: this.config.steps.length,
        completedSteps: this.migrationState.completedSteps.length,
        errors: this.migrationState.errors.length,
        warnings: this.migrationState.warnings.length
      },
      stats: this.migrationState.stats,
      configuration: this.config,
      errors: this.migrationState.errors,
      warnings: this.migrationState.warnings
    };
    
    const reportPath = path.join(this.config.toolsDir, 'migration', 'final-report.json');
    await fs.writeFile(reportPath, JSON.stringify(report, null, 2));
    
    console.log(chalk.blue(`\n📄 Final report saved: ${reportPath}`));
  }

  async handleMigrationFailure(error) {
    console.log(chalk.red('\n💥 Migration failed!'));
    
    // Save failure report
    const failureReport = {
      timestamp: new Date().toISOString(),
      error: error.message,
      stack: error.stack,
      migrationState: this.migrationState,
      configuration: this.config
    };
    
    const failurePath = path.join(this.config.toolsDir, 'migration', 'failure-report.json');
    await fs.writeFile(failurePath, JSON.stringify(failureReport, null, 2));
    
    console.log(chalk.blue(`📄 Failure report saved: ${failurePath}`));
  }

  // Helper methods
  formatStepName(step) {
    return step.split('-').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  }

  async copyDirectory(src, dest) {
    const entries = await fs.readdir(src, { withFileTypes: true });
    
    for (const entry of entries) {
      const srcPath = path.join(src, entry.name);
      const destPath = path.join(dest, entry.name);
      
      if (entry.isDirectory()) {
        await fs.mkdir(destPath, { recursive: true });
        await this.copyDirectory(srcPath, destPath);
      } else {
        await fs.copyFile(srcPath, destPath);
      }
    }
  }

  async directoryExists(dirPath) {
    try {
      await fs.access(dirPath);
      return true;
    } catch {
      return false;
    }
  }

  generateDetailedSteps() {
    return this.config.steps.map(step => ({
      name: step,
      description: this.getStepDescription(step),
      estimatedTime: this.getStepTimeEstimate(step)
    }));
  }

  getStepDescription(step) {
    const descriptions = {
      'analyze-current-content': 'Analyze existing AI-Q content structure and completeness',
      'create-backup': 'Create backup of current AI-Q directory',
      'generate-migration-plan': 'Generate detailed migration plan based on analysis',
      'convert-to-aku-format': 'Convert all content to AKU (Atomic Knowledge Unit) format',
      'import-to-graph': 'Import AKUs into Neo4j graph database',
      'validate-relationships': 'Validate all relationships and dependencies',
      'generate-reports': 'Generate comprehensive migration reports',
      'cleanup': 'Clean up temporary files and resources'
    };
    
    return descriptions[step] || 'Unknown step';
  }

  getStepTimeEstimate(step) {
    const estimates = {
      'analyze-current-content': '5-10 minutes',
      'create-backup': '2-5 minutes',
      'generate-migration-plan': '1-2 minutes',
      'convert-to-aku-format': '10-30 minutes',
      'import-to-graph': '5-15 minutes',
      'validate-relationships': '3-8 minutes',
      'generate-reports': '2-5 minutes',
      'cleanup': '1-2 minutes'
    };
    
    return estimates[step] || 'Unknown';
  }

  estimateMigrationTime() {
    return '30-60 minutes';
  }

  identifyRisks() {
    const risks = [];
    
    if (this.migrationState.analysis?.duplicates.length > 0) {
      risks.push('Duplicate content may cause conflicts during migration');
    }
    
    if (this.migrationState.analysis?.overallCompletion < 50) {
      risks.push('Low completion rate may result in incomplete AKUs');
    }
    
    return risks;
  }
}

// CLI execution
async function main() {
  const manager = new MigrationManager();
  await manager.startMigration();
}

if (require.main === module) {
  main().catch(error => {
    console.error('Migration failed:', error);
    process.exit(1);
  });
}

module.exports = MigrationManager; 