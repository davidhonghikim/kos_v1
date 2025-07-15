#!/usr/bin/env node

/**
 * AI-Q Theme Manager
 * 
 * Allows dynamic switching between different metaphor themes
 * and building custom themes for the knowledge system.
 */

const fs = require('fs').promises;
const path = require('path');
const chalk = require('chalk');
const inquirer = require('inquirer');

class ThemeManager {
  constructor() {
    this.configPath = './config/metaphor-config.json';
    this.themesPath = './themes/';
    this.currentTheme = null;
    this.config = null;
  }

  async initialize() {
    try {
      await this.loadConfig();
      await this.ensureThemesDirectory();
      console.log(chalk.green('🎨 Theme Manager initialized'));
    } catch (error) {
      console.error(chalk.red('Failed to initialize theme manager:', error.message));
      throw error;
    }
  }

  async loadConfig() {
    const configData = await fs.readFile(this.configPath, 'utf8');
    this.config = JSON.parse(configData);
    this.currentTheme = this.config.active_metaphor;
  }

  async saveConfig() {
    await fs.writeFile(this.configPath, JSON.stringify(this.config, null, 2));
  }

  async ensureThemesDirectory() {
    try {
      await fs.access(this.themesPath);
    } catch {
      await fs.mkdir(this.themesPath, { recursive: true });
    }
  }

  async listThemes() {
    console.log(chalk.blue.bold('\n🎨 Available Themes:'));
    
    for (const [themeId, theme] of Object.entries(this.config.metaphors)) {
      const status = themeId === this.currentTheme ? chalk.green('● ACTIVE') : chalk.gray('○');
      console.log(`  ${status} ${chalk.cyan(themeId)}: ${theme.name}`);
      console.log(`     ${chalk.gray(theme.description)}`);
    }
  }

  async switchTheme(themeId) {
    if (!this.config.metaphors[themeId]) {
      throw new Error(`Theme '${themeId}' not found`);
    }

    console.log(chalk.yellow(`🔄 Switching from '${this.currentTheme}' to '${themeId}'...`));
    
    // Update config
    this.config.active_metaphor = themeId;
    this.currentTheme = themeId;
    
    // Save config
    await this.saveConfig();
    
    // Apply theme changes
    await this.applyTheme(themeId);
    
    console.log(chalk.green(`✅ Theme switched to '${themeId}'`));
  }

  async applyTheme(themeId) {
    const theme = this.config.metaphors[themeId];
    const terminology = this.config.terminology[theme.levels.infrastructure];
    
    console.log(chalk.blue(`🎨 Applying theme: ${theme.name}`));
    console.log(chalk.gray(`   Infrastructure: ${theme.levels.infrastructure}`));
    console.log(chalk.gray(`   Interaction: ${theme.levels.interaction}`));
    
    // Update terminology throughout the system
    await this.updateTerminology(terminology);
    
    // Update UI components
    await this.updateUIComponents(theme);
    
    // Update documentation
    await this.updateDocumentation(theme);
  }

  async updateTerminology(terminology) {
    console.log(chalk.blue('📝 Updating terminology...'));
    
    // Update AKU schema
    await this.updateAKUSchema(terminology);
    
    // Update API endpoints
    await this.updateAPIEndpoints(terminology);
    
    // Update database schemas
    await this.updateDatabaseSchemas(terminology);
  }

  async updateUIComponents(theme) {
    console.log(chalk.blue('🎨 Updating UI components...'));
    
    // Update React components
    await this.updateReactComponents(theme);
    
    // Update CSS variables
    await this.updateCSSVariables(theme);
    
    // Update icons and graphics
    await this.updateGraphics(theme);
  }

  async updateDocumentation(theme) {
    console.log(chalk.blue('📚 Updating documentation...'));
    
    // Update README files
    await this.updateREADME(theme);
    
    // Update API documentation
    await this.updateAPIDocs(theme);
    
    // Update user guides
    await this.updateUserGuides(theme);
  }

  async createCustomTheme() {
    console.log(chalk.blue.bold('\n🎨 Custom Theme Builder'));
    
    const answers = await inquirer.prompt([
      {
        type: 'input',
        name: 'themeId',
        message: 'Theme ID (e.g., cyberpunk_kitchen):',
        validate: (input) => {
          if (!input.match(/^[a-z_]+$/)) {
            return 'Theme ID must be lowercase with underscores only';
          }
          return true;
        }
      },
      {
        type: 'input',
        name: 'name',
        message: 'Theme Name:',
        default: (answers) => answers.themeId.split('_').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ')
      },
      {
        type: 'input',
        name: 'description',
        message: 'Theme Description:'
      },
      {
        type: 'list',
        name: 'infrastructure',
        message: 'Infrastructure Metaphor:',
        choices: Object.keys(this.config.terminology)
      },
      {
        type: 'list',
        name: 'interaction',
        message: 'Interaction Metaphor:',
        choices: Object.keys(this.config.terminology)
      }
    ]);

    // Create custom terminology
    const customTerminology = await this.buildCustomTerminology(answers);
    
    // Create theme configuration
    const customTheme = {
      name: answers.name,
      description: answers.description,
      levels: {
        infrastructure: answers.infrastructure,
        interaction: answers.interaction
      },
      custom_terminology: customTerminology
    };

    // Add to config
    this.config.metaphors[answers.themeId] = customTheme;
    this.config.terminology[`custom_${answers.themeId}`] = customTerminology;
    
    // Save theme file
    const themePath = path.join(this.themesPath, `${answers.themeId}.json`);
    await fs.writeFile(themePath, JSON.stringify(customTheme, null, 2));
    
    // Save config
    await this.saveConfig();
    
    console.log(chalk.green(`✅ Custom theme '${answers.themeId}' created!`));
    console.log(chalk.blue(`   Theme file: ${themePath}`));
    
    return answers.themeId;
  }

  async buildCustomTerminology(themeAnswers) {
    console.log(chalk.blue('\n🔧 Building custom terminology...'));
    
    const terminology = {};
    const baseTerms = [
      'atomic_unit', 'network', 'connection', 'growth', 'mature', 
      'system', 'domain', 'platform', 'data', 'capability', 
      'connector', 'workflow', 'process', 'result', 'quality'
    ];
    
    for (const term of baseTerms) {
      const answer = await inquirer.prompt([
        {
          type: 'input',
          name: 'value',
          message: `Term for '${term}':`,
          default: this.suggestTerm(term, themeAnswers)
        }
      ]);
      terminology[term] = answer.value;
    }
    
    return terminology;
  }

  suggestTerm(term, themeAnswers) {
    // Generate suggestions based on theme
    const suggestions = {
      'atomic_unit': ['spore', 'seed', 'particle', 'atom', 'cell'],
      'network': ['mycelium', 'web', 'network', 'grid', 'mesh'],
      'connection': ['hyphae', 'link', 'bridge', 'path', 'wire'],
      'growth': ['germination', 'sprouting', 'evolution', 'development', 'emergence'],
      'mature': ['fruiting_body', 'tree', 'adult', 'complete', 'mature'],
      'system': ['tree', 'organism', 'machine', 'structure', 'entity'],
      'domain': ['forest', 'ecosystem', 'realm', 'territory', 'zone'],
      'platform': ['ecosystem', 'universe', 'world', 'platform', 'environment'],
      'data': ['ingredient', 'material', 'resource', 'data', 'information'],
      'capability': ['skill', 'ability', 'power', 'function', 'talent'],
      'connector': ['adaptor', 'bridge', 'link', 'connector', 'interface'],
      'workflow': ['recipe', 'process', 'procedure', 'workflow', 'routine'],
      'process': ['cooking', 'processing', 'transformation', 'work', 'operation'],
      'result': ['dish', 'output', 'product', 'result', 'outcome'],
      'quality': ['taste', 'quality', 'standard', 'measure', 'grade']
    };
    
    return suggestions[term] ? suggestions[term][0] : term;
  }

  async previewTheme(themeId) {
    const theme = this.config.metaphors[themeId];
    const terminology = this.config.terminology[theme.levels.infrastructure];
    
    console.log(chalk.blue.bold(`\n🎨 Theme Preview: ${theme.name}`));
    console.log(chalk.gray(theme.description));
    console.log('');
    
    console.log(chalk.cyan('Infrastructure Level:'));
    console.log(`  Atomic Unit: ${terminology.atomic_unit}`);
    console.log(`  Network: ${terminology.network}`);
    console.log(`  Connection: ${terminology.connection}`);
    console.log(`  Growth: ${terminology.growth}`);
    console.log(`  Mature: ${terminology.mature}`);
    console.log(`  System: ${terminology.system}`);
    console.log(`  Domain: ${terminology.domain}`);
    console.log(`  Platform: ${terminology.platform}`);
    
    console.log(chalk.cyan('\nInteraction Level:'));
    console.log(`  Data: ${terminology.data}`);
    console.log(`  Capability: ${terminology.capability}`);
    console.log(`  Connector: ${terminology.connector}`);
    console.log(`  Workflow: ${terminology.workflow}`);
    console.log(`  Process: ${terminology.process}`);
    console.log(`  Result: ${terminology.result}`);
    console.log(`  Quality: ${terminology.quality}`);
    console.log(`  System: ${terminology.system}`);
  }

  // Placeholder methods for theme application
  async updateAKUSchema(terminology) {
    console.log(chalk.gray('   Updating AKU schema...'));
  }

  async updateAPIEndpoints(terminology) {
    console.log(chalk.gray('   Updating API endpoints...'));
  }

  async updateDatabaseSchemas(terminology) {
    console.log(chalk.gray('   Updating database schemas...'));
  }

  async updateReactComponents(theme) {
    console.log(chalk.gray('   Updating React components...'));
  }

  async updateCSSVariables(theme) {
    console.log(chalk.gray('   Updating CSS variables...'));
  }

  async updateGraphics(theme) {
    console.log(chalk.gray('   Updating graphics...'));
  }

  async updateREADME(theme) {
    console.log(chalk.gray('   Updating README...'));
  }

  async updateAPIDocs(theme) {
    console.log(chalk.gray('   Updating API docs...'));
  }

  async updateUserGuides(theme) {
    console.log(chalk.gray('   Updating user guides...'));
  }
}

// CLI interface
async function main() {
  const manager = new ThemeManager();
  
  try {
    await manager.initialize();
    
    const { action } = await inquirer.prompt([
      {
        type: 'list',
        name: 'action',
        message: 'What would you like to do?',
        choices: [
          { name: 'List themes', value: 'list' },
          { name: 'Switch theme', value: 'switch' },
          { name: 'Create custom theme', value: 'create' },
          { name: 'Preview theme', value: 'preview' },
          { name: 'Exit', value: 'exit' }
        ]
      }
    ]);
    
    switch (action) {
      case 'list':
        await manager.listThemes();
        break;
      case 'switch':
        const { themeId } = await inquirer.prompt([
          {
            type: 'list',
            name: 'themeId',
            message: 'Select theme to switch to:',
            choices: Object.keys(manager.config.metaphors)
          }
        ]);
        await manager.switchTheme(themeId);
        break;
      case 'create':
        await manager.createCustomTheme();
        break;
      case 'preview':
        const { previewThemeId } = await inquirer.prompt([
          {
            type: 'list',
            name: 'previewThemeId',
            message: 'Select theme to preview:',
            choices: Object.keys(manager.config.metaphors)
          }
        ]);
        await manager.previewTheme(previewThemeId);
        break;
      case 'exit':
        console.log(chalk.blue('👋 Goodbye!'));
        process.exit(0);
    }
    
  } catch (error) {
    console.error(chalk.red('Theme manager error:', error.message));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = ThemeManager; 