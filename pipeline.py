from typing import List, Union
from utils import get_examples, make_context, get_response
from tools import LLM, Tools

class Pipeline:
    def __init__(
        self,
        llm_agent: LLM,
        model_name: str,
        sample_prompt: str,
        respond_prompt: str,
        search_tool: Tools,
        num_retrieved_pages: int
    ):
        """
        Initializes the Pipeline with the necessary components.
        """
        self.llm = llm_agent
        self.model_name = model_name
        self.sample_prompt = sample_prompt
        self.respond_prompt = respond_prompt
        self.search_tool = search_tool
        self.num_retrieved_pages = num_retrieved_pages

    def __call__(
        self,
        seed_questions: Union[str, List[str]],
        verbose: bool = False,
        seed_as_instructions: bool = False,
        sample_size: int = None
    ):
        """
        Executes the pipeline with the provided seed questions.
        """
        # Generate sample questions based on the seed questions
        samples = get_examples(
            seed=seed_questions,
            agent=self.llm,
            model=self.model_name,
            prompt=self.sample_prompt,
            verbose=verbose,
            seed_as_instructs=seed_as_instructions,
            sample_size=sample_size  # Pass the sample_size parameter
        )
        if verbose:
            print(f"Generated Samples: {samples}")

        instructions = []
        for question in samples['questions']:
            try:
                # Generate context and retrieve links using the search tool
                context, links = make_context(
                    question,
                    self.search_tool,
                    self.num_retrieved_pages,
                    verbose
                )
                # Truncate context if necessary
                max_context_length = 200000
                truncated_context = context[:min(max_context_length, len(context))]
                # Get the response using the LLM
                instruction = get_response(
                    question,
                    truncated_context,
                    links,
                    self.llm,
                    self.model_name,
                    self.respond_prompt,
                    verbose
                )
                instructions.append(instruction)
            except Exception as err:
                print(f"Unexpected error: {err}, type: {type(err)}")
        return instructions
