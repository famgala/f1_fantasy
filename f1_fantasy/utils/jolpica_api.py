import fastf1
from datetime import datetime
from typing import List, Dict, Optional
from ..models import db, Race, Driver

class F1DataManager:
    """Utility class for managing F1 data using Fast-F1."""
    
    def __init__(self, cache_dir: str = None):
        """Initialize Fast-F1 with optional cache directory."""
        if cache_dir:
            fastf1.set_cache(cache_dir)
        # Enable caching by default
        fastf1.set_log_level('WARNING')  # Reduce noise in logs
    
    def import_season_data(self, season: int) -> Dict[str, int]:
        """Import all race and driver data for a given season."""
        stats = {'races': 0, 'drivers': 0}
        
        try:
            # Get schedule for the season
            schedule = fastf1.get_event_schedule(season)
            
            # Import races
            for _, event in schedule.iterrows():
                race = Race(
                    season=season,
                    round=event['RoundNumber'],
                    name=event['EventName'],
                    circuit_name=event['CircuitName'],
                    country=event['Country'],
                    city=event.get('City'),  # Some circuits might not have city data
                    date=event['EventDate'].date(),
                    time=event['EventTime'].time() if 'EventTime' in event else None,
                    status='scheduled'
                )
                db.session.merge(race)
                stats['races'] += 1
            
            # Get drivers for the season
            drivers = fastf1.get_drivers(season)
            for _, driver in drivers.iterrows():
                driver_obj = Driver(
                    driver_number=driver['DriverNumber'],
                    code=driver.get('Abbreviation'),  # Some drivers might not have a code
                    first_name=driver['FirstName'],
                    last_name=driver['LastName'],
                    nationality=driver['CountryCode'],
                    date_of_birth=driver['DateOfBirth'].date() if 'DateOfBirth' in driver else None,
                    constructor=driver['TeamName'],
                    status='active'
                )
                db.session.merge(driver_obj)
                stats['drivers'] += 1
            
            db.session.commit()
            return stats
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error importing season {season}: {str(e)}")
    
    def get_race_details(self, season: int, round: int) -> Dict:
        """Get detailed information about a specific race."""
        try:
            session = fastf1.get_session(season, round, 'R')  # 'R' for race
            session.load()
            
            return {
                'race_name': session.event['EventName'],
                'circuit': session.event['CircuitName'],
                'date': session.event['EventDate'],
                'weather': session.weather_data.to_dict() if hasattr(session, 'weather_data') else None,
                'track_temperature': session.track_status.to_dict() if hasattr(session, 'track_status') else None
            }
        except Exception as e:
            raise Exception(f"Error getting race details: {str(e)}")
    
    def get_driver_details(self, season: int, driver_code: str) -> Dict:
        """Get detailed information about a specific driver."""
        try:
            driver = fastf1.get_driver(driver_code, season)
            return {
                'name': f"{driver['FirstName']} {driver['LastName']}",
                'number': driver['DriverNumber'],
                'team': driver['TeamName'],
                'nationality': driver['CountryCode'],
                'date_of_birth': driver['DateOfBirth'] if 'DateOfBirth' in driver else None
            }
        except Exception as e:
            raise Exception(f"Error getting driver details: {str(e)}")

def import_historical_data(cache_dir: str = None, start_season: int = 2020, end_season: int = 2025) -> Dict[str, Dict[str, int]]:
    """Import historical F1 data for a range of seasons."""
    manager = F1DataManager(cache_dir)
    stats = {}
    
    for season in range(start_season, end_season + 1):
        try:
            season_stats = manager.import_season_data(season)
            stats[str(season)] = season_stats
        except Exception as e:
            print(f"Error importing data for season {season}: {str(e)}")
            stats[str(season)] = {'error': str(e)}
    
    return stats 