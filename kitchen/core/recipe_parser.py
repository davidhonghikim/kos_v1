# kitchen/core/recipe_parser.py
"""
Recipe Parser for the Kitchen Orchestration System.

This module defines the structure of a recipe and provides the functionality
to load, parse, and validate a recipe file from JSON format into a Python object.
It ensures that any recipe passed to the engine conforms to the required schema.
"""

import json
import os
from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field, ValidationError, validator

from .logging import get_logger

# --- Logger ---
logger = get_logger(__name__)

# --- Pydantic Models for Recipe Structure Validation ---

class Step(BaseModel):
    """
    Defines the schema for a single step within a recipe.
    """
    name: str = Field(..., description="A unique, human-readable name for the step.")
    ingredient: str = Field(..., description="The name of the Pantry Ingredient to execute.")
    params: Dict[str, Any] = Field({}, description="Parameters to pass to the ingredient.")
    description: Optional[str] = Field(None, description="An optional description of the step's purpose.")
    on_failure: str = Field('abort', description="Action on failure: 'abort' or 'continue'.")

    @validator('on_failure')
    def validate_on_failure(cls, value):
        if value not in ['abort', 'continue']:
            raise ValueError("on_failure must be either 'abort' or 'continue'")
        return value

class Recipe(BaseModel):
    """
    Defines the overall schema for a recipe file.
    """
    name: str = Field(..., description="The name of the recipe.")
    description: str = Field(..., description="A detailed description of what the recipe accomplishes.")
    version: str = Field("1.0.0", description="The version of the recipe.")
    steps: List[Step] = Field(..., description="An ordered list of steps to be executed.")

# --- Parser Class ---

class RecipeParser:
    """
    Parses and validates a JSON recipe file.
    """
    def __init__(self, recipe_path: str):
        """
        Initializes the parser with the path to the recipe file.

        Args:
            recipe_path: The full path to the JSON recipe file.
        
        Raises:
            FileNotFoundError: If the recipe file does not exist.
        """
        if not os.path.exists(recipe_path):
            logger.error(f"Recipe file not found at path: {recipe_path}")
            raise FileNotFoundError(f"Recipe file not found: {recipe_path}")
        self.recipe_path = recipe_path
        self.recipe: Optional[Recipe] = None

    def parse(self) -> Recipe:
        """
        Loads, validates, and parses the recipe file.

        Returns:
            A validated Recipe object.
        
        Raises:
            ValueError: If the recipe file is not valid JSON or fails schema validation.
        """
        logger.info(f"Attempting to parse recipe: {self.recipe_path}")
        try:
            with open(self.recipe_path, 'r') as f:
                data = json.load(f)
            
            # Validate the data against the Pydantic model
            self.recipe = Recipe(**data)
            logger.info(f"Successfully parsed and validated recipe: '{self.recipe.name}'")
            return self.recipe

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in recipe file {self.recipe_path}: {e}", exc_info=True)
            raise ValueError(f"Invalid JSON format in {self.recipe_path}")
        except ValidationError as e:
            logger.error(f"Recipe validation failed for {self.recipe_path}:\n{e}", exc_info=True)
            raise ValueError(f"Recipe schema validation failed for {self.recipe_path}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while parsing recipe {self.recipe_path}: {e}", exc_info=True)
            raise

# --- Example Usage ---
if __name__ == "__main__":
    # Create a directory for dummy recipes
    dummy_recipe_dir = "temp_recipes"
    os.makedirs(dummy_recipe_dir, exist_ok=True)

    # 1. Create a valid dummy recipe file
    valid_recipe_path = os.path.join(dummy_recipe_dir, "valid_recipe.json")
    valid_recipe_data = {
        "name": "Demo Recipe",
        "description": "A simple recipe for demonstration purposes.",
        "version": "1.0.1",
        "steps": [
            {
                "name": "Step 1: Say Hello",
                "ingredient": "console.print",
                "params": {"message": "Hello, World!"},
                "description": "Prints a greeting to the console."
            },
            {
                "name": "Step 2: List Files",
                "ingredient": "filesystem.list_directory",
                "params": {"path": "."},
                "on_failure": "continue"
            }
        ]
    }
    with open(valid_recipe_path, 'w') as f:
        json.dump(valid_recipe_data, f, indent=4)

    logger.info("--- Testing Valid Recipe ---")
    try:
        parser = RecipeParser(valid_recipe_path)
        recipe = parser.parse()
        logger.info(f"Parsed recipe name: {recipe.name}")
        logger.info(f"Number of steps: {len(recipe.steps)}")
        logger.info(f"First step ingredient: {recipe.steps[0].ingredient}")
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error parsing valid recipe: {e}")

    # 2. Create an invalid (missing required field) dummy recipe file
    invalid_recipe_path = os.path.join(dummy_recipe_dir, "invalid_recipe.json")
    invalid_recipe_data = {
        "name": "Invalid Recipe",
        "steps": [
            {"name": "Step 1", "ingredient": "do_something"} 
            # Missing 'description' for the recipe itself
        ]
    }
    with open(invalid_recipe_path, 'w') as f:
        json.dump(invalid_recipe_data, f, indent=4)

    logger.info("\n--- Testing Invalid Recipe (Schema Error) ---")
    try:
        parser = RecipeParser(invalid_recipe_path)
        parser.parse()
    except ValueError as e:
        logger.warning(f"Successfully caught expected validation error: {e}")

    # 3. Create a malformed JSON file
    malformed_json_path = os.path.join(dummy_recipe_dir, "malformed.json")
    with open(malformed_json_path, 'w') as f:
        f.write('{"name": "Malformed", "steps": [}') # Incomplete JSON

    logger.info("\n--- Testing Malformed JSON ---")
    try:
        parser = RecipeParser(malformed_json_path)
        parser.parse()
    except ValueError as e:
        logger.warning(f"Successfully caught expected JSON error: {e}")

    # 4. Test file not found
    logger.info("\n--- Testing File Not Found ---")
    try:
        parser = RecipeParser("non_existent_recipe.json")
        parser.parse()
    except FileNotFoundError as e:
        logger.warning(f"Successfully caught expected file not found error: {e}")

    # Clean up dummy files and directory
    import shutil
    shutil.rmtree(dummy_recipe_dir)
    logger.info(f"\nCleaned up dummy directory: {dummy_recipe_dir}")
