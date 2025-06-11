import click
from flask.cli import with_appcontext
from ..utils.jolpica_api import import_historical_data
from ..models import Settings
import os

@click.command('import-f1-data')
@click.option('--start-season', default=2020, help='Start season to import data from')
@click.option('--end-season', default=2025, help='End season to import data to')
@click.option('--cache-dir', help='Directory to store Fast-F1 cache (defaults to ~/.fastf1)')
@with_appcontext
def import_f1_data(start_season: int, end_season: int, cache_dir: str = None):
    """Import F1 data using Fast-F1."""
    if not cache_dir:
        cache_dir = os.path.expanduser('~/.fastf1')
    
    click.echo(f'Importing F1 data from {start_season} to {end_season}...')
    click.echo(f'Using cache directory: {cache_dir}')
    
    stats = import_historical_data(cache_dir, start_season, end_season)
    
    # Print results
    click.echo('\nImport Results:')
    click.echo('-' * 50)
    for season, season_stats in stats.items():
        if 'error' in season_stats:
            click.echo(f'Season {season}: Error - {season_stats["error"]}')
        else:
            click.echo(f'Season {season}:')
            click.echo(f'  Races imported: {season_stats["races"]}')
            click.echo(f'  Drivers imported: {season_stats["drivers"]}')
    click.echo('-' * 50)

def init_app(app):
    """Register the command with the Flask application."""
    app.cli.add_command(import_f1_data) 