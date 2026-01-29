from isaaclab.app import AppLauncher
import argparse

app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

from pxr import Usd, Sdf
import os

def check_integrity(usd_path):
    if not os.path.exists(usd_path):
        print(f"Error: File not found at {usd_path}")
        return

    print(f"Opening stage: {usd_path}")
    stage = Usd.Stage.Open(usd_path)
    if not stage:
        print("Error: Could not open stage.")
        return

    print("Checking for broken relationships and joints...")
    
    issues_found = False
    
    for prim in stage.Traverse():
        # Check relationships
        for rel in prim.GetRelationships():
            targets = rel.GetTargets()
            for target in targets:
                # Check if target path contains 'astra' or points to non-existent prim
                if "astra" in str(target).lower():
                    print(f"Warning: Prim {prim.GetPath()} has relationship {rel.GetName()} targeting removed path: {target}")
                    issues_found = True
                else:
                    target_prim = stage.GetPrimAtPath(target)
                    if not target_prim.IsValid():
                         print(f"Warning: Prim {prim.GetPath()} has relationship {rel.GetName()} targeting invalid/missing prim: {target}")
                         issues_found = True

        # Check attributes that are relationships (like physics connections)
        # In USD, Physics connections are relationships, detected above.
        
    if not issues_found:
        print("No obvious broken relationships found.")
    else:
        print("Issues found in USD file.")

if __name__ == "__main__":
    usd_file_path = os.path.join(os.path.dirname(__file__), "spot_micro.usd")
    check_integrity(usd_file_path)
    
    simulation_app.close()
