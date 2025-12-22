#!/usr/bin/env python3
# modules/Collecte.py

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Import shared UI system from Collecte.py
from Collecte import UI, Icons, Theme
from llm_backend import LLMBackend


class Analysis:
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / "prompts"
        self.results_dir = Path(__file__).parent.parent / "results"
        self.backend = None
        self.available_models = []
        self.ui = UI()  # ← Shared UI system
    
    def get_available_models(self):
        """Liste les modèles Ollama installés sur la machine"""
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                self.ui.warning("Ollama command failed")
                return []
            
            models = []
            lines = result.stdout.strip().split('\n')
            
            # Skip header line
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        models.append(model_name)
            
            return sorted(models)
            
        except FileNotFoundError:
            self.ui.error("Ollama CLI not found in PATH")
            with self.ui.indent():
                self.ui.muted("Check installation: which ollama")
            return []
        except subprocess.TimeoutExpired:
            self.ui.warning("Ollama command timeout")
            return []
        except Exception as e:
            self.ui.warning(f"Error listing models: {e}")
            return []
    
    def _categorize_models(self, models):
        """Organise les modèles par catégorie (PoC vs Production)"""
        categories = {
            "🚀 PoC / Debug (fast)": [],
            "🎯 Production (quality)": [],
            "🔬 Other": []
        }
        
        for model in models:
            model_lower = model.lower()
            if any(x in model_lower for x in ['qwen:0.5b', 'qwen2:0.5b', 'tinyllama']):
                categories["🚀 PoC / Debug (fast)"].append(model)
            elif any(x in model_lower for x in ['mistral', 'llama3', 'qwen:7b', 'qwen2:7b']):
                categories["🎯 Production (quality)"].append(model)
            else:
                categories["🔬 Other"].append(model)
        
        return categories
    
    def _get_size_hint(self, model):
        """Hint sur la vitesse/qualité selon le modèle"""
        model_lower = model.lower()
        
        if 'qwen:0.5b' in model_lower or 'qwen2:0.5b' in model_lower:
            return "⚡ 2-5s"
        elif 'mistral' in model_lower or 'llama3' in model_lower:
            return "🐢 30-60s"
        elif any(x in model_lower for x in [':1b', ':3b', ':7b']):
            return "⏱️ 10-45s"
        else:
            return ""
    
    def select_backend(self):
        """Menu sélection backend avec modèles disponibles"""
        self.ui.space()
        self.ui.step("Scanning installed Ollama models...")
        
        models = self.get_available_models()
        
        if not models:
            self.ui.space()
            self.ui.error("No Ollama models found!")
            self.ui.space()
            
            with self.ui.indent():
                self.ui.subsection("Quick setup:")
                with self.ui.indent():
                    self.ui.list_item("Start Ollama: ollama serve")
                    self.ui.list_item("Install models:")
                    with self.ui.indent():
                        self.ui.muted("ollama pull qwen:0.5b            # Fast PoC")
                        self.ui.muted("ollama pull mistral:7b-instruct  # Production")
                
                self.ui.space()
                self.ui.muted("Then restart this script.")
            
            self.ui.space()
            use_default = input("\n   Use default (qwen:0.5b) anyway? (y/n): ")
            if use_default.lower() == 'y':
                return ("local", "qwen:0.5b")
            
            return None
        
        self.ui.success(f"Found {len(models)} model(s)")
        self.ui.space()
        
        # Catégorise les modèles
        categorized = self._categorize_models(models)
        
        self.ui.separator()
        self.ui.header("SELECT LLM MODEL")
        self.ui.separator()
        
        all_models = []
        idx = 1
        
        for category, category_models in categorized.items():
            if category_models:
                self.ui.space()
                self.ui.subsection(category)
                with self.ui.indent():
                    for model in category_models:
                        size_hint = self._get_size_hint(model)
                        print(f"    {idx}. {model:<30} {size_hint}")
                        all_models.append(model)
                        idx += 1
        
        self.ui.space()
        self.ui.muted("0. Exit")
        self.ui.separator()
        
        while True:
            try:
                choice = int(input("\nYour choice: ").strip())
                if choice == 0:
                    return None
                if 1 <= choice <= len(all_models):
                    model = all_models[choice - 1]
                    return ("local", model)
                self.ui.error(f"Invalid choice. Please enter 0-{len(all_models)}")
            except ValueError:
                self.ui.error("Please enter a number")
            except KeyboardInterrupt:
                print("\n")
                self.ui.warning("Cancelled")
                return None
    
    def list_prompts(self):
        """List available analysis prompts"""
        prompts = []
        if self.prompts_dir.exists():
            for file in sorted(self.prompts_dir.glob("*.md")):
                prompts.append(file.stem)
        return prompts
    
    def list_data_files(self):
        """List available data files in results/"""
        data_files = []
        if self.results_dir.exists():
            for file in sorted(self.results_dir.glob("*.json")):
                data_files.append(file.name)
        return data_files
    
    def read_prompt(self, prompt_name):
        """Read prompt template from file"""
        prompt_file = self.prompts_dir / f"{prompt_name}.md"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def read_data(self, data_filename):
        """Read JSON data from results/"""
        data_file = self.results_dir / data_filename
        if not data_file.exists():
            raise FileNotFoundError(f"Data file not found: {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def display_menu(self, title, options):
        """Display interactive menu using shared UI"""
        self.ui.separator()
        self.ui.header(title)
        self.ui.separator()
        self.ui.space()
        
        with self.ui.indent():
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
        
        self.ui.space()
        self.ui.muted("0. Exit")
        self.ui.separator()
        
        while True:
            try:
                choice = input("\nYour choice: ").strip()
                choice_num = int(choice)
                
                if choice_num == 0:
                    return None
                if 1 <= choice_num <= len(options):
                    return options[choice_num - 1]
                else:
                    self.ui.error(f"Invalid choice. Please enter 0-{len(options)}")
            except ValueError:
                self.ui.error("Please enter a number")
            except KeyboardInterrupt:
                print("\n")
                self.ui.warning("Exiting...")
                return None
    
    def save_result(self, result, prompt_name, data_filename):
        """Sauvegarde TXT avec timestamp et metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{prompt_name}_{timestamp}.txt"
        output_path = self.results_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header informatif
            f.write(f"{'=' * 60}\n")
            f.write(f"MOSAIC Analysis Report\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(f"Prompt:    {prompt_name}\n")
            f.write(f"Data:      {data_filename}\n")
            f.write(f"Model:     {self.backend.model}\n")
            f.write(f"Date:      {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n{'=' * 60}\n\n")
            f.write(result)
        
        self.ui.success(f"Analysis saved: {output_path.name}")
        return output_path
    
    def run_analysis(self, prompt_name, data_filename):
        """Run LLM analysis with selected prompt and data"""
        self.ui.space()
        self.ui.separator()
        self.ui.header("RUNNING ANALYSIS", Icons.PROCESSING)
        self.ui.separator()
        
        # 1. Select backend
        backend_config = self.select_backend()
        if backend_config is None:
            self.ui.space()
            self.ui.warning("Cancelled")
            return
        
        backend_type, model = backend_config
        
        # 2. Read prompt template
        self.ui.space()
        self.ui.step(f"Loading prompt: {prompt_name}.md")
        prompt = self.read_prompt(prompt_name)
        
        with self.ui.indent():
            self.ui.success(f"Prompt loaded ({len(prompt)} characters)")
        
        # 3. Read data
        self.ui.space()
        self.ui.step(f"Loading data: {data_filename}")
        data = self.read_data(data_filename)
        data_str = json.dumps(data, indent=2)
        
        with self.ui.indent():
            self.ui.success(f"Data loaded ({len(data_str)} characters)")
        
        # Preview tronquée
        preview = data_str[:300] + "..." if len(data_str) > 300 else data_str
        self.ui.space()
        with self.ui.indent():
            self.ui.muted("Data preview:")
            with self.ui.indent():
                for line in preview.split('\n')[:10]:
                    self.ui.muted(line)
        
        # 4. Initialize backend
        self.ui.space()
        self.ui.step("Initializing LLM backend...")
        self.backend = LLMBackend(backend_type=backend_type, model=model)
        
        with self.ui.indent():
            self.ui.keyvalue("Backend", self.backend.backend_type)
            self.ui.keyvalue("Model", self.backend.model)
        
        # Check availability
        if not self.backend.check_availability():
            self.ui.space()
            self.ui.error("Ollama server not available")
            with self.ui.indent():
                self.ui.muted("Start it with: ollama serve")
            return
        
        with self.ui.indent():
            self.ui.success("Ollama server: Running")
        
        # 5. Prepare full prompt
        full_prompt = f"{prompt}\n\n{data_str}"
        
        # 6. Call LLM
        estimated_time = "2-5s" if "qwen:0.5b" in model else "30-60s"
        self.ui.space()
        self.ui.step("Calling LLM...")
        
        with self.ui.indent():
            self.ui.keyvalue("Model", self.backend.model)
            self.ui.keyvalue("Estimated time", estimated_time)
            self.ui.muted("Please wait...")
        
        self.ui.space()
        
        result = self.backend.analyze(full_prompt, "")
        
        # 7. Display result
        self.ui.space()
        self.ui.separator()
        self.ui.header("ANALYSIS RESULT", Icons.STATS)
        self.ui.separator()
        
        if result.startswith("ERROR"):
            self.ui.space()
            self.ui.error(result)
        else:
            self.ui.space()
            print(result)
        
        self.ui.space()
        self.ui.separator()
        
        # 8. Save result
        self.save_result(result, prompt_name, data_filename)
    
    def run(self):
        """Main interactive loop"""
        self.ui.space()
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + "  🔬 MOSAIC - Behavioral Analysis with Local LLM".center(58) + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "═" * 58 + "╝")
        
        # Select prompt
        prompts = self.list_prompts()
        if not prompts:
            self.ui.space()
            self.ui.error("No prompts found in modules/prompts/")
            return
        
        prompt_choice = self.display_menu("Select Analysis Prompt", prompts)
        if prompt_choice is None:
            self.ui.space()
            self.ui.muted("Goodbye!")
            return
        
        # Select data file
        data_files = self.list_data_files()
        if not data_files:
            self.ui.space()
            self.ui.error("No data files found in results/")
            return
        
        data_choice = self.display_menu("Select Data File", data_files)
        if data_choice is None:
            self.ui.space()
            self.ui.muted("Goodbye!")
            return
        
        # Run analysis
        try:
            self.run_analysis(prompt_choice, data_choice)
        except FileNotFoundError as e:
            self.ui.space()
            self.ui.error(f"Error: {e}")
        except KeyboardInterrupt:
            self.ui.space()
            self.ui.warning("Analysis interrupted by user")
        except Exception as e:
            self.ui.space()
            self.ui.error(f"Unexpected error: {e}")
        
        self.ui.space()
        self.ui.success("Analysis complete!")
        self.ui.space()


if __name__ == "__main__":
    analyzer = Analysis()
    analyzer.run()
