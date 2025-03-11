from cerebrum.llm.apis import llm_chat


class CodeToNarrativeTranslator:
    """
    {
        "name": "Code-to-Narrative Translator",
        "function": "Converts software codebases into technical documentation and user-facing feature descriptions.",
        "input_example": "Python script for image processing.",
        "output_example": "API documentation + non-technical user guide in parallel outputs."
    }
    """
    def __init__(self, agent_name="Code-to-Narrative Translator"):
        self.agent_name = agent_name
        self.messages = []
        self.code_structure = {}
        self.supported_languages = ["python", "javascript", "java", "c++", "typescript", "go"]

    def run(self, task_input):
        """
        Main entry point for the agent.

        Args:
            task_input: Code to be analyzed and documented

        Returns:
            Dictionary containing both technical documentation and user guide
        """
        # Reset state for new task
        self.code_structure = {}
        self.messages = []

        # Initial message to set context
        self.messages.append({
            "role": "system",
            "content": "You are a specialized Code-to-Narrative Translator that converts technical code into clear documentation for both developers and end-users."
        })
        self.messages.append({"role": "user", "content": task_input})

        # Phase 1: Language Detection
        language = self._detect_language(task_input)

        # Phase 2: Code Analysis
        code_analysis = self._analyze_code(task_input, language)

        # Phase 3: Extract Code Structure
        self._extract_code_structure(code_analysis)

        # Phase 4: Generate Technical Documentation
        technical_docs = self._generate_technical_docs()

        # Phase 5: Generate User Guide
        user_guide = self._generate_user_guide()

        # Phase 6: Create visualization diagrams if applicable
        diagrams = self._generate_diagrams()

        # Combine results
        final_result = {
            "technical_documentation": technical_docs,
            "user_guide": user_guide,
            "diagrams": diagrams,
            "code_structure": self.code_structure
        }

        return final_result

    def _detect_language(self, code_input):
        """Detect the programming language of the provided code."""
        self.messages.append({
            "role": "user",
            "content": "Please identify the programming language of the following code snippet. Just output the language name in lowercase:\n\n" + code_input[
                                                                                                                                                   :1000]
            # Use first 1000 chars for detection
        })

        response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            base_url="http://localhost:8000"
        )

        detected_language = response["response"]["response_message"].strip().lower()

        # Add detection result to messages
        self.messages.append({
            "role": "assistant",
            "content": f"The detected language is {detected_language}."
        })

        return detected_language

    def _analyze_code(self, code_input, language):
        """Analyze the code structure and functionality."""

        analysis_tools = [
            {
                "name": "code_analyzer",
                "description": "Analyzes code to identify key components, functions, classes, and their relationships",
                "input_schema": {"type": "string", "description": "Code to analyze"},
                "output_schema": {"type": "object", "description": "Structured analysis of code components"}
            }
        ]

        self.messages.append({
            "role": "user",
            "content": f"Please analyze this {language} code and identify the main components, functions, classes, and their relationships:\n\n{code_input}"
        })

        response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            tools=analysis_tools,
            base_url="http://localhost:8000"
        )

        code_analysis = response["response"]["response_message"]

        # Add analysis to messages
        self.messages.append({
            "role": "assistant",
            "content": "Code analysis completed."
        })

        return code_analysis

    def _extract_code_structure(self, code_analysis):
        """Extract structured information about the code."""

        extraction_tools = [
            {
                "name": "structure_extractor",
                "description": "Extracts structured information from code analysis",
                "input_schema": {"type": "string", "description": "Code analysis text"},
                "output_schema": {
                    "type": "object",
                    "description": "Structured code information",
                    "properties": {
                        "classes": {"type": "array", "description": "List of classes"},
                        "functions": {"type": "array", "description": "List of functions"},
                        "modules": {"type": "array", "description": "List of modules"},
                        "dependencies": {"type": "array", "description": "List of dependencies"},
                        "main_functionality": {"type": "string", "description": "Summary of main functionality"}
                    }
                }
            }
        ]

        self.messages.append({
            "role": "user",
            "content": "Based on the code analysis, extract structured information about classes, functions, modules, "
                       "dependencies, and main functionality in JSON format."
        })

        response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            tools=extraction_tools,
            base_url="http://localhost:8000"
        )

        # Parse the structured data from response
        import json
        try:
            structured_data = json.loads(response["response"]["response_message"])
            self.code_structure = structured_data
        except:
            # Fallback if JSON parsing fails
            self.code_structure = {
                "classes": [],
                "functions": [],
                "modules": [],
                "dependencies": [],
                "main_functionality": "Could not automatically extract structure"
            }

        # Add structure extraction to messages
        self.messages.append({
            "role": "assistant",
            "content": "Code structure extracted."
        })

        return self.code_structure

    def _generate_technical_docs(self):
        """Generate technical documentation for developers."""

        docs_tools = [
            {
                "name": "api_docs_generator",
                "description": "Generates API documentation for developers",
                "input_schema": {"type": "object", "description": "Code structure information"},
                "output_schema": {"type": "string", "description": "Markdown formatted API documentation"}
            }
        ]

        self.messages.append({
            "role": "user",
            "content": f"""Generate comprehensive technical documentation aimed at developers based on the code structure.
            Include:
            1. Overview of the code's purpose
            2. Architecture explanation
            3. API reference for all classes and functions
            4. Parameter descriptions and return types
            5. Usage examples
            6. Dependencies and requirements

            Here's the code structure to work with: {self.code_structure}
            """
        })

        response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            tools=docs_tools,
            base_url="http://localhost:8000"
        )

        technical_docs = response["response"]["response_message"]

        # Add documentation to messages
        self.messages.append({
            "role": "assistant",
            "content": "Technical documentation generated."
        })

        return technical_docs

    def _generate_user_guide(self):
        """Generate user-friendly guide for non-technical users."""

        guide_tools = [
            {
                "name": "user_guide_generator",
                "description": "Generates user-friendly documentation for non-technical users",
                "input_schema": {"type": "object", "description": "Code structure information"},
                "output_schema": {"type": "string", "description": "Markdown formatted user guide"}
            }
        ]

        self.messages.append({
            "role": "user",
            "content": f"""Generate a user-friendly guide aimed at non-technical end users based on the code structure.
            Include:
            1. Plain language explanation of what this software does
            2. Features and benefits explained in non-technical terms
            3. How-to guides for common tasks
            4. Examples of typical use cases
            5. FAQs in user-friendly language

            Here's the code structure to work with: {self.code_structure}
            """
        })

        response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            tools=guide_tools,
            base_url="http://localhost:8000"
        )

        user_guide = response["response"]["response_message"]

        # Add user guide to messages
        self.messages.append({
            "role": "assistant",
            "content": "User guide generated."
        })

        return user_guide

    def _generate_diagrams(self):
        """Generate visualization diagrams of code structure."""

        diagram_tools = [
            {
                "name": "diagram_generator",
                "description": "Generates mermaid or plantuml diagram code for code visualization",
                "input_schema": {"type": "object", "description": "Code structure information"},
                "output_schema": {"type": "object", "description": "Diagram code objects"}
            }
        ]

        self.messages.append({
            "role": "user",
            "content": f"""Generate diagram code for visualizing the code structure. Please create:
            1. A class diagram showing class relationships
            2. A flowchart showing the main execution flow
            3. A component diagram showing module relationships

            Use mermaid diagram syntax. Base it on this code structure: {self.code_structure}
            """
        })

        response = llm_chat(
            agent_name=self.agent_name,
            messages=self.messages,
            tools=diagram_tools,
            base_url="http://localhost:8000"
        )

        diagrams = response["response"]["response_message"]

        # Add diagrams to messages
        self.messages.append({
            "role": "assistant",
            "content": "Visualization diagrams generated."
        })

        return diagrams