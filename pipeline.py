from typing import List, Union
from utils import get_examples, make_context, get_response
from tools import LLM, Tools
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

class Pipeline:
    def __init__(
        self,
        llm_agent: LLM,
        model_sampler_name: str,
        model_responder_name: str,
        sample_prompt: str,
        respond_prompt: str,
        search_tool: Tools,
        number_retrieved_pages: int,
        skip_websites: List[str],
        used_number_of_links: int
    ):
        """
        Initializes the Pipeline with the necessary components.

        Parameters:
            llm_agent (LLM): The language model agent to use for generating and responding.
            model_sampler_name (str): The name of the model to use for sampling.
            model_responder_name (str): The name of the model to use for responding.
            sample_prompt (str): The prompt used to generate sample questions.
            respond_prompt (str): The prompt used for generating responses to questions.
            search_tool (Tools): The search tool to use for retrieving context.
            number_retrieved_pages (int): The number of pages to retrieve from the search tool.
            skip_websites (List[str]): List of website domains to skip during content retrieval.
            used_number_of_links (int): Desired number of successfully fetched links.
        """
        self.llm = llm_agent
        self.model_sampler_name = model_sampler_name
        self.model_responder_name = model_responder_name
        self.sample_prompt = sample_prompt
        self.respond_prompt = respond_prompt
        self.search_tool = search_tool
        self.number_retrieved_pages = number_retrieved_pages
        self.skip_websites = skip_websites
        self.used_number_of_links = used_number_of_links

    def __call__(
        self,
        seed_questions: Union[str, List[str]],
        verbose: bool = False,
        seed_as_instructions: bool = False,
        sample_size: int = None,
        iterations: int = 1,
        max_workers_iterations: int = 2,  # Number of threads for iterations
        max_workers_questions: int = 4  # Number of threads for questions
    ):
        """
        Executes the pipeline with the provided seed questions.

        Parameters:
            seed_questions (str or List[str]): The seed question(s) to start with.
            verbose (bool): If True, prints additional information during execution.
            seed_as_instructions (bool): If True, use seed questions as instructions.
            sample_size (int, optional): Number of seed questions to randomly select.
            iterations (int): Number of times to run the pipeline. Defaults to 1.
            max_workers_iterations (int): Maximum number of worker threads for iterations.
            max_workers_questions (int): Maximum number of worker threads for processing questions.

        Returns:
            List[dict]: A list of instructions generated by the pipeline.
        """
        all_instructions = []

        # Define a helper function for processing a single iteration
        def process_iteration(iteration_index):
            iteration_instructions = []

            if verbose:
                print(f"\033[34m\nStarting iteration {iteration_index + 1} of {iterations}\033[0m")

            # Generate sample questions based on the seed questions
            if verbose:
                print("\033[36mGenerating sample questions...\033[0m")
            samples = get_examples(
                seed=seed_questions,
                agent=self.llm,
                model=self.model_sampler_name,
                prompt=self.sample_prompt,
                verbose=verbose,
                seed_as_instructs=seed_as_instructions,
                sample_size=sample_size
            )

            if verbose:
                print("\033[32mGenerated Samples:\033[0m")
                for idx, question in enumerate(samples['questions'], start=1):
                    print(f"  {idx}. {question}")

            questions = samples['questions']

            # Prepare the progress bar for questions
            question_progress = tqdm(total=len(questions), desc=f"Questions (Iteration {iteration_index + 1})", unit="question", leave=False)

            # Use ThreadPoolExecutor for concurrent processing of questions
            with ThreadPoolExecutor(max_workers=max_workers_questions) as executor:
                future_to_question = {
                    executor.submit(self.process_question, question, verbose): question for question in questions
                }

                for future in as_completed(future_to_question):
                    question = future_to_question[future]
                    try:
                        instruction = future.result()
                        if instruction:
                            iteration_instructions.append(instruction)
                    except Exception as err:
                        print(f"\033[31mError processing question '{question}': {err}\033[0m")
                    finally:
                        question_progress.update(1)

            question_progress.close()
            return iteration_instructions

        # Prepare the progress bar for iterations
        iteration_progress = tqdm(total=iterations, desc="Iterations", unit="iteration")

        # Use ThreadPoolExecutor for concurrent processing of iterations
        with ThreadPoolExecutor(max_workers=max_workers_iterations) as executor:
            future_to_iteration = {
                executor.submit(process_iteration, iteration_index): iteration_index for iteration_index in range(iterations)
            }

            for future in as_completed(future_to_iteration):
                iteration_index = future_to_iteration[future]
                try:
                    iteration_instructions = future.result()
                    all_instructions.extend(iteration_instructions)
                except Exception as err:
                    print(f"\033[31mError in iteration {iteration_index + 1}: {err}\033[0m")
                finally:
                    iteration_progress.update(1)

        iteration_progress.close()

        return all_instructions

    def process_question(self, question: str, verbose: bool = False):
        """
        Processes a single question: retrieves context, generates response.

        Parameters:
            question (str): The question to process.
            verbose (bool): If True, prints additional information.

        Returns:
            dict: The instruction generated for the question.
        """
        try:
            if verbose:
                print(f"\033[35m\nProcessing question:\033[0m {question}")

            # Generate context and retrieve links using the search tool
            if verbose:
                print("\033[36mRetrieving context...\033[0m")
            context, links = make_context(
                query=question,
                tool=self.search_tool,
                num_pages=self.number_retrieved_pages,
                verbose=verbose,
                skip_websites=self.skip_websites,
                used_number_of_links=self.used_number_of_links
            )
            # Truncate context if necessary
            max_context_length = 200000
            truncated_context = context[:min(max_context_length, len(context))]

            if verbose:
                print("\033[36mGenerating response...\033[0m")
            # Get the response using the responder model
            instruction = get_response(
                query=question,
                context=truncated_context,
                links=links,
                agent=self.llm,
                model=self.model_responder_name,
                prompt=self.respond_prompt,
                verbose=verbose
            )
            return instruction
        except Exception as err:
            print(f"\033[31mUnexpected error processing question '{question}': {err}\033[0m")
            return None
