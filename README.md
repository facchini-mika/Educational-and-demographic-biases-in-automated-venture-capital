# Educational and Demographic Biases in Automated Venture Capital

This project provides an **automated data generation tool** developed for a bachelor thesis on bias in venture capital decisions. It offers a user-friendly GUI to configure and run experiments that examine how educational background and demographic cues (such as gender and ethnicity) of startup founders might influence AI-driven investment recommendations. The tool queries multiple large language model (LLM) APIs (e.g. OpenAI GPT-4, Google Gemini, etc.) with standardized startup pitch prompts and collects their decisions on whether to invest and how much to invest. The resulting dataset can be used to analyze potential biases in the models’ venture capital recommendations.

## Features

- **GUI-Based Experiment Launcher:** Provides a graphical interface to set up and run experiments without coding.
- **Multi-Model Support:** Supports querying multiple LLM providers in one go (e.g. OpenAI, Google, DeepSeek, Mistral).
- **Configurable Scenarios:** Choose full factorial experiments or simplified variants (vary all attributes or just a subset) for flexibility in testing.
- **Automated Data Logging:** Collects all model responses and saves them to a structured JSON Lines (`.jsonl`) file with relevant metadata for analysis.
- **Parallel Execution:** Runs queries across selected models in parallel to speed up experiment completion.
- **Graceful Stopping:** Includes an option to force-stop an ongoing experiment if needed.

## Getting Started

Follow these steps to set up the project and run the tool:

1. **Clone the Repository**  
   Clone the project repository and navigate into it:
   ```bash
   git clone https://github.com/<your-user>/Educational-and-Demographic-Biases-in-Automated-Venture-Capital.git
   cd Educational-and-Demographic-Biases-in-Automated-Venture-Capital
   ```

2. **Set Up a Python Environment**  
   Ensure you have **Python 3.10+** installed. It’s recommended to use a virtual environment:
   ```bash
   python3 -m venv .venv          # Create virtual environment (optional)
   source .venv/bin/activate      # Activate the virtual env (use .venv\Scripts\activate on Windows)
   ```

3. **Install Dependencies**  
   Install the required Python libraries. If a `requirements.txt` is provided, use:
   ```bash
   pip install -r requirements.txt
   ```  
   *Note:* The tool uses Python’s Tkinter (for the GUI) and a few external libraries for API access (e.g. OpenAI SDK, Google GenAI SDK, Together API, Mistral client, `python-dotenv`, `filelock`). Make sure these are installed in your environment.

4. **Configure API Keys (optional)**  

   If no API keys are given, the system simulates the calls with a result of `invest: 1, amount: 100000`

   The experiment uses external LLM APIs, so you need to provide your API credentials:
   - Create an **`.env`** file
   - Open the `.env` file in a text editor and enter your API keys for the relevant services (e.g. `OPENAI_API_KEY`, `GOOGLE_API_KEY` (for Gemini), `TOGETHER_API_KEY`, `MISTRAL_API_KEY`, etc.).  
   Alternatively, you can set these environment variables directly in your system.

6. **Launch the GUI**  
   Start the graphical interface by running:
   ```bash
   python gui_launcher.py
   ```  
   This will open a window titled "Experiment Launcher", where you can configure and run the experiment.

## Usage

Once the GUI is open, you can set up an experiment to generate data. For example:

1. **Configure the Experiment:** In the GUI, enter the number of **Repetitions** (how many times each scenario should be run, e.g. `1` or more for averaging effects). Then select a **Config Variant** from the drop-down:
   - *full* – run the full experiment (all combinations of gender × ethnicity × education for each selected model).
   - *persons* – vary only the person-related attributes (gender, ethnicity) while keeping education constant.
   - *unis* – vary only the university education attribute while keeping the person constant.
   - *single* – run a single test scenario (one specific founder profile and one university).
2. **Select Models:** Choose one or multiple models from the list (e.g. OpenAI, Gemini, DeepSeek, Mistral) to include in the run.
3. **Start the Experiment:** Click the **Start Experiment** button. The status label at the bottom will update to "Running…" and the experiment will begin. Each selected model will be queried with the generated pitch prompts according to the chosen variant.
4. **Monitoring:** The experiment runs in parallel threads for each model. You can monitor progress via the status text. If needed, you can click **Force Quit** to stop the experiment early.
5. **Results:** When the run finishes, a pop-up will confirm completion and the status will show "Finished successfully ✓". All results are saved to the output file (e.g. `Data/Output/data.jsonl`). Each line in this JSONL file represents one model’s response to a pitch, including the input details and the model’s yes/no decision and proposed amount. All generated prompts are saved in `generated_prompts.txt` for traceability file for traceability. This also includes the repetitions.

You can then use the collected data in `Data/Output/data.jsonl` for further analysis (e.g. to compute statistics on bias or train evaluation models as part of the thesis).

## Repository Structure

- **`gui_launcher.py`** – Launches the Tkinter-based GUI application for configuring and starting experiments.
- **`llm_api_client.py`** – Contains a unified client to query different large language model APIs (OpenAI, Google Gemini, DeepSeek via Together API, Mistral, etc.).
- **`configuration_generator.py`** – Defines how to generate experiment configurations. Depending on the variant (full, persons, unis, single), it produces the appropriate combinations of founder attributes and repeats.
- **`template_builder.py`** – Builds the startup pitch prompt for a given configuration by filling in a template with the founder’s details (name, pronouns, university, etc.).
- **`result_persistor.py`** – Handles saving model responses to disk in a thread-safe way. It appends results to a JSON Lines file (`data.jsonl`) and includes fields like the model’s decision, amount, and metadata (timestamps, tokens used).
- **`run_manager.py`** – Orchestrates the experiment run. It sets up threads for each selected model, generates prompts for each scenario, calls the LLM API client, and uses the result persistor to log outputs.
- **`Data/Input/`** – Directory containing input data assets for the experiment:
  - `gender_ethnicity.json`, `universities.json`, `pitch_templates.json` (lists of sample founder identities, university options, and base pitch text templates used by the tool).
- **`Data/Output/`** – Directory where experiment outputs are saved. After running an experiment, the main results file `data.jsonl` will appear here (along with any other processed output files).

