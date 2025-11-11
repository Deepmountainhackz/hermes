ALERT_RULES = {
    'markets': {
        'sp500_daily_change': {'high': 3.0, 'medium': 2.0},
        'vix_level': {'high': 30, 'medium': 25},
    },
    
    'commodities': {
        'oil_daily_change': {'high': 5.0, 'medium': 3.0},
        'wheat_weekly_change': {'high': 10.0, 'medium': 7.0},
    },
    
    'economics': {
        'unemployment_change': {'high': 0.3, 'medium': 0.2},
        'inflation_rate': {'high': 5.0, 'medium': 3.5},
    },
    
    'weather': {
        'extreme_temp_high': 40,
        'extreme_temp_low': -20,
        'storm_count_24h': 3,
    },
    
    'disasters': {
        'earthquake_magnitude': {'high': 6.0, 'medium': 5.0},
        'wildfire_count_weekly': {'high': 10, 'medium': 5},
    },
    
    'agriculture': {
        'yield_change_yoy': {'high': -15, 'medium': -10},
        'production_change_yoy': {'high': -20, 'medium': -15},
    }
}
