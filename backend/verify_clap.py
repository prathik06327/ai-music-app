import laion_clap
import torch

def verify():
    # Attempt to load the model
    # According to docs, the standard initialization is:
    # model = laion_clap.CLAP_Module(enable_fusion=False)
    # model.load_ckpt()
    print("Initializing CLAP module...")
    
    try:
        # Initializing without specifying amodel ensures it matches the default loaded checkpoint ('HTSAT-tiny' or 'HTSAT-base' depending on laion-clap defaults)
        model = laion_clap.CLAP_Module(enable_fusion=False, amodel='HTSAT-tiny')
        model.load_ckpt() # Automatically downloads the default checkpoint
        print("CLAP model correctly loaded.")
    except Exception as e:
        print(f"Failed to load CLAP: {e}")

if __name__ == '__main__':
    verify()