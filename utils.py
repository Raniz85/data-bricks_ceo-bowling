import os.path

# Define a helper to load the input for a series
def load_input(part: int) -> [str]:
    """Loads the input for a part of the kata from the volume"""
    input_path = os.path.join(VOLUME_PATH, f"./series{part:02d}.txt")
    with open(input_path) as f:
        return f.readlines()