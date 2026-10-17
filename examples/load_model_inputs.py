"""Load one Arrow batch ready for model-specific tokenization."""

from steam_insights.pipeline.loader import iter_model_batches, latest_dataset
from steam_insights.pipeline.settings import load_pipeline_config

config = load_pipeline_config()
directory = latest_dataset(config)
for batch in iter_model_batches(directory, kind="pairs", split="train", batch_size=32):
    print("Dataset:", directory.name)
    print("Batch rows:", batch.num_rows)
    print("Input fields:", batch.schema.names)
    break
else:
    print("No eligible input pairs in this split; inspect the readiness report.")
