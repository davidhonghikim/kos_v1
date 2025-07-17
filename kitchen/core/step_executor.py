# kitchen/core/step_executor.py
"""
Step Executor for the Kitchen Orchestration System.

This module is responsible for executing a single step of a recipe. It takes a
validated Step object, retrieves the corresponding ingredient from the Pantry,
and executes it with the specified parameters. It also handles context
management, allowing the output of one step to be used as input for subsequent steps.
"""
import inspect
from typing import Any, Dict

from .logging import get_logger
from .pantry_manager import PantryManager
from .recipe_parser import Step

# --- Logger ---
logger = get_logger(__name__)

# --- StepResult Data Class ---

class StepResult:
    """
    A simple data class to encapsulate the result of a step execution.
    """
    def __init__(self, success: bool, message: str, output: Any = None):
        self.success = success
        self.message = message
        self.output = output

    def __repr__(self) -> str:
        return f"<StepResult success={self.success} message='{self.message}'>"

# --- StepExecutor Class ---

class StepExecutor:
    """
    Executes a single recipe step, handling context and errors.
    """
    def __init__(self, pantry_manager: PantryManager):
        """
        Initializes the StepExecutor.

        Args:
            pantry_manager: An instance of PantryManager to retrieve ingredients from.
        """
        self.pantry_manager = pantry_manager
        logger.info("StepExecutor initialized.")

    def execute_step(self, step: Step, context: Dict[str, Any]) -> StepResult:
        """
        Executes a given step using the provided context.

        Args:
            step: The Step object to execute.
            context: A dictionary representing the current execution context,
                     which may contain outputs from previous steps.

        Returns:
            A StepResult object indicating the outcome of the execution.
        """
        logger.info(f"--- Executing Step: '{step.name}' ---")
        logger.info(f"Description: {step.description or 'No description provided.'}")
        logger.info(f"Ingredient: {step.ingredient}")

        # 1. Retrieve the ingredient from the pantry
        ingredient_func = self.pantry_manager.get_ingredient(step.ingredient)
        if not ingredient_func:
            msg = f"Ingredient '{step.ingredient}' not found. Cannot execute step '{step.name}'."
            logger.error(msg)
            return StepResult(success=False, message=msg)

        # 2. Prepare parameters, resolving any context references
        try:
            resolved_params = self._resolve_params(step.params, context)
            logger.debug(f"Resolved parameters for '{step.name}': {resolved_params}")
        except KeyError as e:
            msg = f"Failed to resolve context key in params for step '{step.name}': {e}"
            logger.error(msg, exc_info=True)
            return StepResult(success=False, message=msg)

        # 3. Execute the ingredient
        try:
            # Inspect the function signature to pass only the expected arguments
            sig = inspect.signature(ingredient_func)
            valid_params = {
                key: value for key, value in resolved_params.items()
                if key in sig.parameters
            }
            
            logger.info(f"Executing ingredient '{step.ingredient}' with params: {valid_params}")
            result_output = ingredient_func(**valid_params)
            
            msg = f"Step '{step.name}' executed successfully."
            logger.info(msg)
            return StepResult(success=True, message=msg, output=result_output)

        except Exception as e:
            msg = f"An error occurred during execution of step '{step.name}': {e}"
            logger.error(msg, exc_info=True)
            return StepResult(success=False, message=msg)

    def _resolve_params(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves parameter values that reference the execution context.

        A parameter value like '{{steps.previous_step.output}}' will be replaced
        by the actual output from the 'previous_step'.

        Args:
            params: The dictionary of parameters for the step.
            context: The current execution context.

        Returns:
            A new dictionary with context references resolved.
        
        Raises:
            KeyError: If a context reference cannot be found.
        """
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                context_key = value.strip('{} ')
                # Basic key lookup for now. Can be expanded for nested lookups.
                # e.g., 'steps.step_name.output'
                if context_key not in context:
                    raise KeyError(f"Context key '{context_key}' not found.")
                resolved[key] = context[context_key]
            else:
                resolved[key] = value
        return resolved

# --- Example Usage ---
if __name__ == "__main__":
    from .config import load_config
    
    # Setup dummy environment for demonstration
    dummy_pantry_dir = "temp_pantry_executor/operations"
    os.makedirs(dummy_pantry_dir, exist_ok=True)
    with open(os.path.join(dummy_pantry_dir, "test_tasks.py"), "w") as f:
        f.write(
"""
def add(a, b):
    return a + b
    
def fail_task():
    raise ValueError("This task is designed to fail.")
"""
        )

    logger.info("--- Testing StepExecutor ---")
    
    # 1. Initialize dependencies
    config = load_config()
    pantry_manager = PantryManager(os.path.abspath("temp_pantry_executor"))
    pantry_manager.discover_ingredients()
    executor = StepExecutor(pantry_manager)

    # 2. Test a successful step
    logger.info("\n--- Test 1: Successful Execution ---")
    success_step = Step(
        name="add_numbers",
        ingredient="test_tasks.add",
        params={"a": 5, "b": 10}
    )
    context = {}
    result = executor.execute_step(success_step, context)
    logger.info(f"Execution Result: {result}")
    logger.info(f"Result Output: {result.output}")
    assert result.success and result.output == 15

    # 3. Test a failing step
    logger.info("\n--- Test 2: Failing Execution ---")
    fail_step = Step(
        name="failing_step",
        ingredient="test_tasks.fail_task",
        params={}
    )
    result = executor.execute_step(fail_step, context)
    logger.info(f"Execution Result: {result}")
    assert not result.success

    # 4. Test context resolution
    logger.info("\n--- Test 3: Context Resolution ---")
    context = {"previous_output": 20}
    context_step = Step(
        name="add_with_context",
        ingredient="test_tasks.add",
        params={"a": "{{previous_output}}", "b": 7}
    )
    result = executor.execute_step(context_step, context)
    logger.info(f"Execution Result: {result}")
    logger.info(f"Result Output: {result.output}")
    assert result.success and result.output == 27

    # Clean up
    import shutil
    shutil.rmtree("temp_pantry_executor")
