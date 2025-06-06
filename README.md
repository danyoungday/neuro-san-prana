# Project Resilience Autonomous News Agents (PRANA)

The goal of this project is: to replicate the Oxford COVID-19 dataset on other decision-making domains by replacing the large number of volunteers with a multi-agent system. The full system would autonomously scrape news articles, reason about and score levels of intervention, and record them. A first major goal in evaluating the system is to recreate the original COVID-19 dataset intervention scores using the saved articles.

## Data Creation
Data is first preprocessed in `data/edav.ipynb`. It's extremely messy right now. The data is turned into a pandas dataframe, then uploaded to wandb as an artifact.
The artifact is then used in `experiment.py` to run the experiment.

## Running

### Web Interface
The historical database is stored in `data/persistence.csv`. All the rows besides the header should be cleared before running.

To run using the web interface, first set your environment variable to enable gpt-4.1:
```bash
export AGENT_LLM_INFO_FILE="./llm_info.hocon"
```

Then run with:
```bash
python -m run
```

### Experiment

In order to run the experiment, you will need to set other environment variables:
```bash
export PYTHONPATH=$PWD
export AGENT_MANIFEST_FILE="./registries/manifest.hocon"
export AGENT_MANIFEST_UPDATE_PERIOD_SECONDS=5
export AGENT_TOOL_PATH="./coded_tools
```

Then run with:
```bash
python -m experiment
```