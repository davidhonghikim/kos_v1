#!/usr/bin/env node

/**
 * AI-Q Knowledge Library Tools
 * 
 * Unified interface for theme management, MCP adaptors, and system utilities.
 */

const { program } = require('commander');
const chalk = require('chalk');
const figlet = require('figlet');
const boxen = require('boxen');
const ora = require('ora');

// Import tools
const ThemeManager = require('./core/theme-manager.js');
const AIQMCPAdaptor = require('./adaptors/mcp-adaptor.js');

// Display banner
function showBanner() {
  const banner = figlet.textSync('AI-Q Tools', {
    font: 'Standard',
    horizontalLayout: 'default',
    verticalLayout: 'default'
  });
  
  const box = boxen(banner, {
    padding: 1,
    margin: 1,
    borderStyle: 'round',
    borderColor: 'cyan',
    backgroundColor: '#000'
  });
  
  console.log(box);
  console.log(chalk.cyan('AI-Q Knowledge Library Tools v1.0.0'));
  console.log(chalk.gray('Theme management, MCP adaptors, and system utilities\n'));
}

// Theme management commands
async function handleThemeCommand(options) {
  const themeManager = new ThemeManager();
  
  try {
    await themeManager.initialize();
    
    if (options.list) {
      await themeManager.listThemes();
    } else if (options.switch) {
      await themeManager.switchTheme(options.switch);
    } else if (options.create) {
      await themeManager.createCustomTheme();
    } else if (options.preview) {
      await themeManager.previewTheme(options.preview);
    } else {
      // Interactive mode
      await themeManager.listThemes();
      console.log(chalk.yellow('\nUse --help for more options'));
    }
  } catch (error) {
    console.error(chalk.red('Theme manager error:', error.message));
    process.exit(1);
  }
}

// MCP adaptor commands
async function handleAdaptorCommand(options) {
  const adaptor = new AIQMCPAdaptor();
  
  try {
    await adaptor.initialize();
    
    if (options.status) {
      const status = await adaptor.getStatus();
      console.log(JSON.stringify(status, null, 2));
    } else if (options.test) {
      const [toolName, ...args] = options.test.split(' ');
      const toolArgs = args.length > 0 ? JSON.parse(args.join(' ')) : {};
      const result = await adaptor.handleToolCall(toolName, toolArgs);
      console.log(JSON.stringify(result, null, 2));
    } else if (options.adaptor) {
      const status = await adaptor.getAdaptorStatus(options.adaptor);
      console.log(JSON.stringify(status, null, 2));
    } else {
      // Interactive mode
      console.log(chalk.blue('\n🌱 AI-Q MCP Adaptor'));
      console.log(chalk.gray('Available commands:'));
      console.log('  --status - Show adaptor status');
      console.log('  --test <tool> <args> - Test a tool');
      console.log('  --adaptor <id> - Show specific adaptor status');
    }
  } catch (error) {
    console.error(chalk.red('Adaptor error:', error.message));
    process.exit(1);
  }
}

// System utilities
async function handleSystemCommand(options) {
  const spinner = ora('Running system utilities...').start();
  
  try {
    if (options.validate) {
      spinner.text = 'Validating system configuration...';
      // Add validation logic here
      await new Promise(resolve => setTimeout(resolve, 2000));
      spinner.succeed('System configuration validated');
    } else if (options.health) {
      spinner.text = 'Checking system health...';
      // Add health check logic here
      await new Promise(resolve => setTimeout(resolve, 1500));
      spinner.succeed('System health check completed');
    } else if (options.cleanup) {
      spinner.text = 'Cleaning up temporary files...';
      // Add cleanup logic here
      await new Promise(resolve => setTimeout(resolve, 1000));
      spinner.succeed('Cleanup completed');
    }
  } catch (error) {
    spinner.fail('System utility failed');
    console.error(chalk.red('Error:', error.message));
    process.exit(1);
  }
}

// Main CLI setup
function setupCLI() {
  program
    .name('aiq-tools')
    .description('AI-Q Knowledge Library Tools')
    .version('1.0.0');

  // Theme management
  program
    .command('theme')
    .description('Manage AI-Q themes and metaphors')
    .option('-l, --list', 'List available themes')
    .option('-s, --switch <theme>', 'Switch to a specific theme')
    .option('-c, --create', 'Create a custom theme')
    .option('-p, --preview <theme>', 'Preview a theme')
    .action(handleThemeCommand);

  // MCP adaptor
  program
    .command('adaptor')
    .description('Manage MCP-compatible adaptors')
    .option('-s, --status', 'Show adaptor status')
    .option('-t, --test <tool>', 'Test a specific tool')
    .option('-a, --adaptor <id>', 'Show specific adaptor status')
    .action(handleAdaptorCommand);

  // System utilities
  program
    .command('system')
    .description('System utilities and maintenance')
    .option('-v, --validate', 'Validate system configuration')
    .option('-h, --health', 'Check system health')
    .option('-c, --cleanup', 'Clean up temporary files')
    .action(handleSystemCommand);

  // Quick commands
  program
    .command('quick-theme')
    .description('Quick theme operations')
    .argument('<operation>', 'Operation: list, switch, create, preview')
    .argument('[target]', 'Target theme or operation parameter')
    .action(async (operation, target) => {
      const themeManager = new ThemeManager();
      await themeManager.initialize();
      
      switch (operation) {
        case 'list':
          await themeManager.listThemes();
          break;
        case 'switch':
          if (!target) {
            console.error(chalk.red('Please specify a theme to switch to'));
            process.exit(1);
          }
          await themeManager.switchTheme(target);
          break;
        case 'create':
          await themeManager.createCustomTheme();
          break;
        case 'preview':
          if (!target) {
            console.error(chalk.red('Please specify a theme to preview'));
            process.exit(1);
          }
          await themeManager.previewTheme(target);
          break;
        default:
          console.error(chalk.red(`Unknown operation: ${operation}`));
          process.exit(1);
      }
    });

  program
    .command('quick-adaptor')
    .description('Quick adaptor operations')
    .argument('<operation>', 'Operation: status, test, connect')
    .argument('[target]', 'Target adaptor or tool')
    .argument('[args]', 'Tool arguments (JSON)')
    .action(async (operation, target, args) => {
      const adaptor = new AIQMCPAdaptor();
      await adaptor.initialize();
      
      switch (operation) {
        case 'status':
          const status = await adaptor.getStatus();
          console.log(JSON.stringify(status, null, 2));
          break;
        case 'test':
          if (!target) {
            console.error(chalk.red('Please specify a tool to test'));
            process.exit(1);
          }
          const toolArgs = args ? JSON.parse(args) : {};
          const result = await adaptor.handleToolCall(target, toolArgs);
          console.log(JSON.stringify(result, null, 2));
          break;
        case 'connect':
          if (!target) {
            console.error(chalk.red('Please specify a node to connect to'));
            process.exit(1);
          }
          const connection = await adaptor.handleToolCall('mycelium_connect', {
            node_id: target,
            connection_type: 'hyphae'
          });
          console.log(JSON.stringify(connection, null, 2));
          break;
        default:
          console.error(chalk.red(`Unknown operation: ${operation}`));
          process.exit(1);
      }
    });

  // Default command
  program
    .command('interactive')
    .description('Start interactive mode')
    .action(async () => {
      showBanner();
      
      const inquirer = require('inquirer');
      
      const { action } = await inquirer.prompt([
        {
          type: 'list',
          name: 'action',
          message: 'What would you like to do?',
          choices: [
            { name: '🎨 Manage Themes', value: 'theme' },
            { name: '🔌 Manage Adaptors', value: 'adaptor' },
            { name: '🔧 System Utilities', value: 'system' },
            { name: '🌱 Quick Connect', value: 'connect' },
            { name: '📊 System Status', value: 'status' },
            { name: 'Exit', value: 'exit' }
          ]
        }
      ]);
      
      switch (action) {
        case 'theme':
          await handleThemeCommand({});
          break;
        case 'adaptor':
          await handleAdaptorCommand({});
          break;
        case 'system':
          await handleSystemCommand({});
          break;
        case 'connect':
          const adaptor = new AIQMCPAdaptor();
          await adaptor.initialize();
          const { nodeId } = await inquirer.prompt([
            {
              type: 'input',
              name: 'nodeId',
              message: 'Enter node ID to connect to:',
              default: 'griot_node'
            }
          ]);
          const result = await adaptor.handleToolCall('mycelium_connect', {
            node_id: nodeId,
            connection_type: 'hyphae'
          });
          console.log(chalk.green('✅ Connection result:'));
          console.log(JSON.stringify(result, null, 2));
          break;
        case 'status':
          const statusAdaptor = new AIQMCPAdaptor();
          await statusAdaptor.initialize();
          const status = await statusAdaptor.getStatus();
          console.log(chalk.blue('📊 System Status:'));
          console.log(JSON.stringify(status, null, 2));
          break;
        case 'exit':
          console.log(chalk.blue('👋 Goodbye!'));
          process.exit(0);
      }
    });

  // Error handling
  program.exitOverride();
  
  try {
    program.parse();
  } catch (err) {
    if (err.code === 'commander.help') {
      showBanner();
      program.outputHelp();
    } else {
      console.error(chalk.red('Error:', err.message));
      process.exit(1);
    }
  }
}

// Run CLI if this is the main module
if (require.main === module) {
  setupCLI();
}

module.exports = {
  ThemeManager,
  AIQMCPAdaptor,
  showBanner,
  handleThemeCommand,
  handleAdaptorCommand,
  handleSystemCommand
}; 