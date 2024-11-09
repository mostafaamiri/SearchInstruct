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

        Parameters:
            llm_agent (LLM): The language model agent to use for generating and responding.
            model_name (str): The name of the model to use.
            sample_prompt (str): The prompt used to generate sample questions.
            respond_prompt (str): The prompt used for generating responses to questions.
            search_tool (Tools): The search tool to use for retrieving context.
            num_retrieved_pages (int): The number of pages to retrieve for context.
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
        sample_size: int = None,
        iterations: int = 1
    ):
        """
        Executes the pipeline with the provided seed questions.

        Parameters:
            seed_questions (str or List[str]): The seed question(s) to start with.
            verbose (bool): If True, prints additional information during execution.
            seed_as_instructions (bool): If True, use seed questions as instructions.
            sample_size (int, optional): Number of seed questions to randomly select.
            iterations (int): Number of times to run the pipeline. Defaults to 1.

        Returns:
            List[dict]: A list of instructions generated by the pipeline.
        """
        all_instructions = []

        for iteration in range(iterations):
            if verbose:
                print(f"\nStarting iteration {iteration + 1} of {iterations}")

            # Generate sample questions based on the seed questions
            samples = get_examples(
                seed=seed_questions,
                agent=self.llm,
                model=self.model_name,
                prompt=self.sample_prompt,
                verbose=verbose,
                seed_as_instructs=seed_as_instructions,
                sample_size=sample_size
            )

            if verbose:
                print(f"Generated Samples: {samples}")

            for question in samples['questions']:
                try:
                    # Generate context and retrieve links using the search tool
                    context, links = make_context(
                        query=question,
                        tool=self.search_tool,
                        num=self.num_retrieved_pages,
                        verbose=verbose
                    )
                    # Truncate context if necessary
                    max_context_length = 200000
                    truncated_context = context[:min(max_context_length, len(context))]
                    # Get the response using the LLM
                    instruction = get_response(
                        query=question,
                        context=truncated_context,
                        links=links,
                        agent=self.llm,
                        model=self.model_name,
                        prompt=self.respond_prompt,
                        verbose=verbose
                    )
                    all_instructions.append(instruction)
                except Exception as err:
                    print(f"Unexpected error: {err}, type: {type(err)}")

        return all_instructions
