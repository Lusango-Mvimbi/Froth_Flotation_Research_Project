import pickle
from pathlib import Path

horizons = ['5min', '15min', '30min', '60min']

for horizon in horizons:
    print(f'=== {horizon.upper()} MODEL ===')
    
    # Check rf_model.pkl
    model_path = Path(f'backend/trained_models/{horizon}_efficient/rf_model.pkl')
    if model_path.exists():
        model = pickle.load(open(model_path, 'rb'))
        print(f'rf_model.pkl type: {type(model)}')
        if hasattr(model, 'predict'):
            print('Has predict method: True')
        else:
            print('Has predict method: False')
            if hasattr(model, '__len__'):
                print(f'Length: {len(model)}')
                if len(model) > 0 and isinstance(model[0], str):
                    print('Contains feature names!')
    
    # Check if model is in metadata
    metadata_path = Path(f'backend/trained_models/{horizon}_efficient/metadata.pkl')
    if metadata_path.exists():
        metadata = pickle.load(open(metadata_path, 'rb'))
        if 'results' in metadata:
            print('Model found in metadata results')
            for model_name, model_data in metadata['results'].items():
                if 'model' in model_data:
                    print(f'  {model_name}: {type(model_data["model"])}')
        elif 'model_type' in metadata:
            print('Standard metadata structure')
        else:
            print('Unknown metadata structure')
    print()
