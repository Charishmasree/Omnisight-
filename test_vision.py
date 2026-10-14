import os
import json
from vision_analyzer import analyze_screenshot

def main():
    sample_dir = "sample_images"
    
    if not os.path.exists(sample_dir):
        print(f"Directory '{sample_dir}' not found. Please run generate_test_images.py first.")
        return
        
    image_files = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print(f"No images found in {sample_dir}/. Please add some test screenshots or run generate_test_images.py.")
        return
        
    print(f"Found {len(image_files)} test images in {sample_dir}/. Starting analysis...\n")
    
    results = {}
    
    for filename in sorted(image_files):
        print(f"{'='*40}")
        print(f"Analyzing: {filename}")
        print(f"{'='*40}")
        
        image_path = os.path.join(sample_dir, filename)
        
        try:
            # Call the main analyze function
            result = analyze_screenshot(image_path)
            
            # Print formatted JSON output to terminal
            print(json.dumps(result, indent=2))
            
            # Store result
            results[filename] = result
        except Exception as e:
            print(f"Failed to analyze {filename}: {e}")
            
        print("\n")
        
    # Save all results to a file for team review
    results_file = "analysis_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Analysis complete! All results saved to {results_file}.")

if __name__ == "__main__":
    main()
