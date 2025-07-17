# kitchen/core/pantry_manager.py
"""
Pantry Manager for the Kitchen Orchestration System.

This module discovers, registers, and provides access to "ingredients" - the
executable Python functions that a recipe can call. It scans a designated
directory (`pantry/operations`), imports the modules, and builds a registry
of available functions that the StepExecutor can then invoke.
"""
import os
import importlib
import inspect
from typing import Callable, Dict, Any, Optional

from .logging import get_logger

# --- Logger ---
logger = get_logger(__name__)

# --- PantryManager Class ---

class PantryManager:
    """
    Manages the discovery and registration of executable ingredients.
    """
    def __init__(self, pantry_path: str):
        """
        Initializes the PantryManager.

        Args:
            pantry_path: The absolute path to the pantry directory containing
                         operation modules.
        """
        if not os.path.isdir(pantry_path):
            logger.error(f"Pantry path does not exist or is not a directory: {pantry_path}")
            raise FileNotFoundError(f"Pantry directory not found: {pantry_path}")
        self.pantry_path = pantry_path
        self._registry: Dict[str, Callable[..., Any]] = {}
        logger.info(f"PantryManager initialized for path: {self.pantry_path}")

    def discover_ingredients(self):
        """
        Scans the pantry path, imports modules, and registers ingredients.

        An ingredient is a Python function within a module in the pantry.
        The registered name is derived from the file and function name,
        e.g., a function `print_message` in `console_utils.py` would be
        registered as `console_utils.print_message`.
        """
        logger.info("Starting ingredient discovery...")
        if self._registry:
            logger.info("Registry already populated. Clearing for re-discovery.")
            self._registry.clear()

        for root, _, files in os.walk(self.pantry_path):
            for filename in files:
                if filename.endswith(".py") and not filename.startswith("__"):
                    module_path = os.path.join(root, filename)
                    self._load_and_register_from_module(module_path)
        
        logger.info(f"Ingredient discovery complete. Found {len(self._registry)} ingredients.")
        if not self._registry:
            logger.warning("Pantry discovery finished, but no ingredients were found.")

    def _load_and_register_from_module(self, module_path: str):
        """
        Loads a module and registers all public functions as ingredients.
        """
        # Create a module spec from the file path
        relative_path = os.path.relpath(module_path, os.getcwd())
        module_name = os.path.splitext(relative_path.replace(os.sep, '.'))[0]
        
        try:
            module = importlib.import_module(module_name)
            logger.debug(f"Successfully imported module: {module_name}")

            # Find all functions in the module
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith("_"):  # Register public functions
                    # The ingredient name is `module_filename.function_name`
                    ingredient_key = f"{os.path.splitext(os.path.basename(module_path))[0]}.{name}"
                    self._registry[ingredient_key] = func
                    logger.debug(f"Registered ingredient: '{ingredient_key}'")

        except ImportError as e:
            logger.error(f"Failed to import module {module_name} from {module_path}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred loading module {module_name}: {e}", exc_info=True)


    def get_ingredient(self, name: str) -> Optional[Callable[..., Any]]:
        """
        Retrieves a registered ingredient by its name.

        Args:
            name: The name of the ingredient (e.g., 'filesystem.list_directory').

        Returns:
            The callable function if found, otherwise None.
        """
        ingredient = self._registry.get(name)
        if not ingredient:
            logger.error(f"Ingredient '{name}' not found in the pantry registry.")
        return ingredient

    @property
    def inventory(self) -> Dict[str, Callable[..., Any]]:
        """
        Returns a copy of the current ingredient registry.
        """
        return self._registry.copy()

# --- Example Usage ---
if __name__ == "__main__":
    # Create dummy pantry structure for demonstration
    dummy_pantry_dir = "temp_pantry/operations"
    os.makedirs(dummy_pantry_dir, exist_ok=True)

    # Dummy ingredient file 1
    with open(os.path.join(dummy_pantry_dir, "demo_tasks.py"), "w") as f:
        f.write(
"""
def task_one(param1, param2="default"):
    '''A simple demo task.'''
    print(f"Executing task_one with {param1} and {param2}")
    return True

def task_two():
    '''Another demo task.'''
    print("Executing task_two")
    return "Complete"

def _internal_helper():
    '''This should not be registered.'''
    pass
"""
        )

    # Dummy ingredient file 2
    with open(os.path.join(dummy_pantry_dir, "file_ops.py"), "w") as f:
        f.write(
"""
def read_file(path):
    '''Reads a file.'''
    print(f"Reading file from {path}")
    return "file content"
"""
        )

    # Initialize and run discovery
    logger.info("--- Testing PantryManager ---")
    try:
        # Note: We pass the root of the temp pantry, not the 'operations' subdir
        pantry_manager = PantryManager(os.path.abspath("temp_pantry"))
        pantry_manager.discover_ingredients()

        # Print the inventory
        inventory = pantry_manager.inventory
        logger.info(f"\nDiscovered Inventory ({len(inventory)} items):")
        for name, func in inventory.items():
            logger.info(f" - {name}: {func.__doc__}")

        # Retrieve and test an ingredient
        logger.info("\n--- Testing Ingredient Retrieval ---")
        task_one_func = pantry_manager.get_ingredient("demo_tasks.task_one")
        if task_one_func:
            logger.info("Retrieved 'demo_tasks.task_one'. Executing...")
            task_one_func(param1="Test")
        else:
            logger.error("Could not retrieve 'demo_tasks.task_one'")

        # Test retrieval of a n