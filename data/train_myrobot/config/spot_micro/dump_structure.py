from isaaclab.app import AppLauncher
import argparse

# Explicitly launch the app first
app_launcher = AppLauncher(headless=True)
simulation_app = app_launcher.app

from pxr import Usd, Sdf
import os

def dump_structure(usd_path, output_file):
    if not os.path.exists(usd_path):
        with open(output_file, "w") as f:
            f.write(f"Error: File not found at {usd_path}")
        return

    stage = Usd.Stage.Open(usd_path)
    if not stage:
        with open(output_file, "w") as f:
            f.write("Error: Could not open stage.")
        return

    with open(output_file, "w") as f:
        f.write(f"Dumping structure for {usd_path}\n")
        f.write("-" * 50 + "\n")
        
        for prim in stage.Traverse():
            f.write(f"Prim: {prim.GetPath()} ({prim.GetTypeName()})\n")
            
            # If it's a joint, verify its targets
            if "Joint" in prim.GetTypeName():
                f.write(f"  Type: {prim.GetTypeName()}\n")
                for rel in prim.GetRelationships():
                    f.write(f"    Rel: {rel.GetName()}\n")
                    targets = rel.GetTargets()
                    for target in targets:
                        f.write(f"      Target: {target}\n")
                        target_prim = stage.GetPrimAtPath(target)
                        if not target_prim.IsValid():
                            f.write(f"      -> INVALID TARGET! (Prim does not exist)\n")
            
            # Check for any relationships that might be suspicious
            for rel in prim.GetRelationships():
                targets = rel.GetTargets()
                for target in targets:
                    if "astra" in str(target).lower():
                        f.write(f"    -> WARNING: Relationship {rel.GetName()} points to 'astra' path: {target}\n")

    print(f"Dump completed to {output_file}")

if __name__ == "__main__":
    usd_file_path = os.path.join(os.path.dirname(__file__), "spot_micro.usd")
    output_path = os.path.join(os.path.dirname(__file__), "structure_dump.txt")
    dump_structure(usd_file_path, output_path)
    
    simulation_app.close()
