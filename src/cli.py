"""
Command Line Interface for Learning Intelligence Tool
"""

import click
import sys
from pathlib import Path
from colorama import Fore, Style, init

from src.data.ingestion import load_data, validate_input_format, DataValidationError
from src.inference.engine import InferenceEngine
from src.reporting.insights import InsightGenerator
from src.config import OUTPUTS_DIR

# Initialize colorama
init(autoreset=True)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Learning Intelligence Tool - AI-powered learner analytics
    
    Analyze learner data to predict course completion, detect dropout risk,
    and identify difficult chapters.
    """
    pass


@cli.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='Path to input CSV or JSON file'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default=None,
    help='Output directory for reports (default: outputs/)'
)
@click.option(
    '--format', '-f',
    type=click.Choice(['text', 'json', 'csv', 'all'], case_sensitive=False),
    default='text',
    help='Output format (default: text)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
def predict(input, output, format, verbose):
    """
    Run predictions on learner data
    
    Example:
        learning-intelligence-tool predict -i data/sample_input.csv -f all
    """
    try:
        # Set output directory
        if output is None:
            output_dir = OUTPUTS_DIR
        else:
            output_dir = Path(output)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        click.echo(f"{Fore.CYAN}🚀 Learning Intelligence Tool - Prediction Mode{Style.RESET_ALL}")
        click.echo("=" * 80)
        
        # Validate input
        click.echo(f"\n{Fore.YELLOW}📂 Loading and validating input data...{Style.RESET_ALL}")
        validation_result = validate_input_format(input)
        
        if not validation_result['valid']:
            click.echo(f"{Fore.RED}❌ Validation Error: {validation_result['message']}{Style.RESET_ALL}")
            sys.exit(1)
        
        click.echo(f"{Fore.GREEN}✓ Data validation successful{Style.RESET_ALL}")
        if verbose:
            stats = validation_result['statistics']
            click.echo(f"  Total records: {stats['total_records']}")
            click.echo(f"  Unique students: {stats['unique_students']}")
            click.echo(f"  Unique courses: {stats['unique_courses']}")
        
        # Load data
        df = load_data(input)
        
        # Run inference
        click.echo(f"\n{Fore.YELLOW}🤖 Running AI predictions...{Style.RESET_ALL}")
        engine = InferenceEngine()
        engine.load_models()
        
        results = engine.predict(df)
        click.echo(f"{Fore.GREEN}✓ Predictions complete{Style.RESET_ALL}")
        
        # Generate reports
        click.echo(f"\n{Fore.YELLOW}📊 Generating reports...{Style.RESET_ALL}")
        generator = InsightGenerator()
        
        if format in ['text', 'all']:
            text_report = generator.generate_text_report(results)
            click.echo("\n" + text_report)
            
            # Save text report
            text_path = output_dir / 'analysis_report.txt'
            with open(text_path, 'w') as f:
                # Remove color codes for file output
                import re
                clean_report = re.sub(r'\x1b\[[0-9;]*m', '', text_report)
                f.write(clean_report)
            click.echo(f"{Fore.GREEN}✓ Text report saved: {text_path}{Style.RESET_ALL}")
        
        if format in ['json', 'all']:
            json_path = output_dir / 'predictions.json'
            generator.save_json_report(results, json_path)
            click.echo(f"{Fore.GREEN}✓ JSON report saved: {json_path}{Style.RESET_ALL}")
        
        if format in ['csv', 'all']:
            csv_dir = output_dir / 'csv_reports'
            generator.save_csv_reports(results, csv_dir)
            click.echo(f"{Fore.GREEN}✓ CSV reports saved: {csv_dir}/{Style.RESET_ALL}")
        
        click.echo(f"\n{Fore.CYAN}✨ Analysis complete!{Style.RESET_ALL}")
        
    except DataValidationError as e:
        click.echo(f"{Fore.RED}❌ Data Validation Error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"{Fore.RED}❌ Error: {str(e)}{Style.RESET_ALL}")
        click.echo(f"\n{Fore.YELLOW}💡 Hint: Run model training first if models are not found.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Unexpected Error: {str(e)}{Style.RESET_ALL}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='Path to input CSV or JSON file'
)
def validate(input):
    """
    Validate input data format
    
    Example:
        learning-intelligence-tool validate -i data/sample_input.csv
    """
    click.echo(f"{Fore.CYAN}🔍 Validating input data...{Style.RESET_ALL}")
    
    result = validate_input_format(input)
    
    if result['valid']:
        click.echo(f"{Fore.GREEN}✓ Data validation successful!{Style.RESET_ALL}\n")
        stats = result['statistics']
        click.echo("Data Statistics:")
        click.echo(f"  Total records: {stats['total_records']}")
        click.echo(f"  Unique students: {stats['unique_students']}")
        click.echo(f"  Unique courses: {stats['unique_courses']}")
        click.echo(f"  Average score: {stats['avg_score']}")
        click.echo(f"  Average time spent: {stats['avg_time_spent']} minutes")
    else:
        click.echo(f"{Fore.RED}❌ Validation failed:{Style.RESET_ALL}")
        click.echo(f"  {result['message']}")
        sys.exit(1)


@cli.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='Path to input CSV or JSON file'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    default=None,
    help='Output directory for analysis (default: outputs/)'
)
def analyze(input, output):
    """
    Generate comprehensive analysis and insights
    
    This is equivalent to running predict with --format all
    
    Example:
        learning-intelligence-tool analyze -i data/sample_input.csv
    """
    # Call predict with format='all'
    ctx = click.get_current_context()
    ctx.invoke(predict, input=input, output=output, format='all', verbose=True)


if __name__ == '__main__':
    cli()
