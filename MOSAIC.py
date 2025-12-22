#!/usr/bin/env python3
"""
MOSAIC - Orchestrator Script
Runs extraction → optional AI analysis pipeline
"""

import sys
import os
import subprocess
from pathlib import Path

# Import UI from Collecte.py
sys.path.insert(0, str(Path(__file__).parent / 'modules'))
from Collecte import UI, Icons, Theme


def main():
    if '-h' in sys.argv or '--help' in sys.argv:
        modules_dir = Path(__file__).parent / 'modules'
        mosaic_script = modules_dir / 'Collecte.py'
        mosaic_cmd = [sys.executable, str(mosaic_script), '--help']
        
        subprocess.run(mosaic_cmd, cwd=str(modules_dir))
        sys.exit(0)
    
    ui = UI()
    
    # Header
    ui.space()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🎯 MOSAIC - Behavioral Signal Structuring".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    ui.space()
    
    # Phase 1: Extraction
    ui.header("PHASE 1: DATA EXTRACTION", Icons.PROCESSING)
    ui.space()
    
    with ui.indent():
        ui.info("Launching Collecte.py extractor...")
    
    ui.space()
    ui.separator()
    ui.space()
    
    # Paths
    project_root = Path(__file__).parent
    modules_dir = project_root / 'modules'
    mosaic_script = modules_dir / 'Collecte.py'
    
    # Build command
    mosaic_cmd = [sys.executable, str(mosaic_script)] + sys.argv[1:]
    
    try:
        result = subprocess.run(
            mosaic_cmd,
            cwd=str(modules_dir),
            check=False
        )
        
        extraction_success = result.returncode == 0
        
    except KeyboardInterrupt:
        ui.space()
        ui.warning("Extraction cancelled by user")
        sys.exit(0)
    
    # Phase 2: AI Analysis (optional)
    ui.space()
    ui.separator()
    ui.space()
    
    ui.header("PHASE 2: AI ANALYSIS (Optional)", Icons.STATS)
    ui.space()
    
    with ui.indent():
        if extraction_success:
            ui.success("Data extraction completed")
        else:
            ui.warning("Extraction had some errors")
        
        ui.muted(f"Location: ./results/*.json")
        ui.space()
        
        # Prompt user
        choice = _prompt_ai_analysis(ui)
        
        if choice == 'yes':
            ui.space()
            ui.info("Launching AI analyzer...")
            ui.space()
            ui.separator()
            ui.space()
            
            analyzer_script = modules_dir / 'Analysis.py'
            analyzer_cmd = [sys.executable, str(analyzer_script)]
            
            try:
                subprocess.run(
                    analyzer_cmd,
                    cwd=str(modules_dir),
                    check=False
                )
            except KeyboardInterrupt:
                ui.warning("Analysis cancelled by user")
        
        elif choice == 'no':
            ui.space()
            ui.success("Extraction complete!")
            ui.space()
            
            with ui.indent():
                ui.subsection("Next Steps:")
                ui.space()
                ui.list_item("Extracted data: ./results/*.json")
                ui.list_item("Analysis prompts: ./modules/prompts/*.md")
                ui.space()
                ui.muted("You can run manual analysis anytime with:")
                ui.muted("  cd modules && python3 Analysis.py")
            
            ui.space()
    
    ui.space()
    ui.separator()
    ui.space()
    
    with ui.indent():
        ui.muted("Thank you for using MOSAIC!")
    
    ui.space()


def _prompt_ai_analysis(ui):
    """
    Prompt user for AI analysis choice
    Returns: 'yes' or 'no'
    """
    ui.subsection("Would you like to analyze data with local LLM?")
    ui.space()
    
    with ui.indent():
        ui.muted("Options:")
        ui.list_item("Yes - Launch interactive AI analyzer (requires Ollama)")
        ui.list_item("No  - Manual analysis (data ready in ./results/)")
    
    ui.space()
    
    while True:
        try:
            choice = input("  Your choice (y/n): ").strip().lower()
            
            if choice in ['y', 'yes']:
                return 'yes'
            elif choice in ['n', 'no']:
                return 'no'
            else:
                ui.warning("Please enter 'y' or 'n'")
        
        except KeyboardInterrupt:
            print()
            return 'no'


if __name__ == "__main__":
    main()
