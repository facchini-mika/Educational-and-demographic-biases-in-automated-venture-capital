import threading
from result_persistor import save_result
from llm_api_client import call_api
from template_builder import generate_prompt_for_config
from configuration_generator import get_configs

# Experiment configuration
REPETITIONS = 2  # global constant for number of repetitions
CONFIG_VARIANT = "single" # Options: "full", "persons", "unis", "single"
MODEL_IDS = [3] # 0: OpenAI, 1: Google, 2: DeepSeek, 3: Mistral

def run(config: dict) -> None:
    """Generate a prompt, query the model, and save the result."""
    prompt = generate_prompt_for_config(config)

    # Only the first thread (i.e., the one using the first MODEL_ID) logs prompts
    if config["model_id"] == MODEL_IDS[0]:
        with open("generated_prompts.txt", "a", encoding="utf-8") as f:
            f.write(prompt)
            f.write("\n" + "-" * 80 + "\n")
    
    # Example response structure, to test code without actual API calls
    response = {
        "raw_response": "invest: 1, amount: 100000",
        "tokens_input": 0,
        "tokens_output": 0,}
    #response = call_api(config["model_id"], prompt)
    save_result(response, config)

def main():
    """Runs configured experiment."""
    # Clear log and data files at the start of a run
    for fname in ("generated_prompts.txt", "Data/Output/data.jsonl"):
        try:
            open(fname, "w", encoding="utf-8").close()
        except FileNotFoundError:
            # If the file doesn't exist yet, no action is needed
            pass
    def worker(model_id: int):
        for config in get_configs(CONFIG_VARIANT, model_id, repetitions=REPETITIONS):
            run(config)

    threads = []
    for model_id in MODEL_IDS:
        thread = threading.Thread(target=worker, args=(model_id,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
