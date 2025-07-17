# kitchen/core/kitchen_engine.py
"""
The main Kitchen Engine for the kOS Orchestration System.

This module contains the KitchenEngine class, which is the central orchestrator.
It loads a recipe, discovers available ingredients from the pantry, and executes
the recipe's steps in order, managing the overall state and context.
"""
import argparse
import os
from typing import Dict, Any

from .config import KitchenConfig, load_config
from .logging import get_logger, set_log_level
from .pantry_manager import PantryManager
from .recipe_parser import Recipe, RecipeParser
from .step_executor import StepExecutor, StepResult

# --- Logger ---
logger = get_logger(__name__)

# --- KitchenEngine Class ---

class KitchenEngine:
    """
    The main orchestrator for executing recipes.
    """
    def __init__(self, config: KitchenConfig):
        """
        Initializes the Kitchen Engine.

        Args:
            config: A KitchenConfig object with system settings.
        """
        self.config = config
        set_log_level(self.config.log_level)  # Set log level from config
        
        self.pantry_manager = PantryManager(self.config.pantry_path)
        self.step_executor = StepExecutor(self.pantry_manager)
        self.execution_context: Dict[str, Any] = {}
        
        logger.info("KitchenEngine initialized.")
        logger.info(f"Pantry Path: {self.config.pantry_path}")
        logger.info(f"Recipes Path: {self.config.recipes_path}")

    def cook(self, recipe_path: str) -> bool:
        """
        Loads and executes a recipe from the given path.

        Args:
            recipe_path: The path to the JSON recipe file.

        Returns:
            True if the recipe completes successfully, False otherwise.
        """
        try:
            # 1. Load and parse the recipe
            full_recipe_path = os.path.join(self.config.recipes_path, recipe_path)
            recipe_parser = RecipeParser(full_recipe_path)
            recipe = recipe_parser.parse()
            logger.info(f"Starting to cook recipe: '{recipe.name}' (v{recipe.version})")

            # 2. Discover available ingredients
            self.pantry_manager.discover_ingredients()

            # 3. Execute steps sequentially
            for step in recipe.steps:
                result = self.step_executor.execute_step(step, self.execution_context)
                
                # Update context with the step's output
                self.execution_context[f"steps.{step.name}.output"] = result.output
                self.execution_context[f"steps.{step.name}.success"] = result.success

                if not result.success:
                    logger.error(f"Step '{step.name}' failed.")
                    if step.on_failure == 'abort':
                        logger.critical("Recipe aborted due to step failure.")
                        return False
                    else:
                        logger.warning(f"Continuing recipe execution as per 'on_failure: continue' policy.")
            
            logger.info(f"Successfully finished cooking recipe: '{recipe.name}'")
            return True

        except FileNotFoundError as e:
            logger.critical(f"Recipe file not found: {e}", exc_info=True)
            return False
        except ValueError as e:
            logger.critical(f"Invalid recipe or configuration: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.critical(f"An unexpected error occurred in the Kitchen Engine: {e}", exc_info=True)
            return False

# --- Main Execution Block ---

def main():
    """
    Main entry point for running the Kitchen Engine from the command line.
    """
    parser = argparse.ArgumentParser(description="kOS Kitchen Orchestration Engine.")
    parser.add_argument(
        "--recipe",
        required=True,
        help="Path to the recipe file to execute, relative to the recipes directory."
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to the kitchen_config.json file. Defaults to root directory."
    )
    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize and run the engine
        engine = KitchenEngine(config)
        success = engine.cook(args.recipe)
        
        if success:
            print("\nRecipe execution completed successfully.")
            exit(0)
        else:
            print("\nRecipe execution failed.")
            exit(1)

    except Exception as e:
        logger.critical(f"A fatal error occurred: {e}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    main()
