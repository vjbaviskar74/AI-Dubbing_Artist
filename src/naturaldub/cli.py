import argparse
import sys
from .graph.workflow import create_workflow

def run_cli(video_path: str):
    print(f"Starting NaturalDub CLI for: {video_path}")
    import uuid
    state = {
        "run_id": str(uuid.uuid4()),
        "input_video": video_path
    }
    
    workflow = create_workflow()
    
    try:
        final_state = workflow.invoke(state)
        print("\n\n=== PIPELINE SUCCESS ===")
        print(f"Output Video: {final_state.get('output_video')}")
    except Exception as e:
        print(f"\n\n=== PIPELINE FAILED ===")
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NaturalDub AI CLI")
    parser.add_argument("--video", type=str, required=True, help="Path to input video")
    args = parser.parse_args()
    
    run_cli(args.video)
