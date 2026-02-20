# --- config/schematics.py ---
# Schematics configuration for 3D models - handles model-specific settings

# Model-specific configuration for initial orientations and behavior
# Models listed here but not in SCHEMATICS_VISIBLE_KEYS are not shown in the Ship menu (e.g. worf, apollo_1570, apollo_1701_refit).
SCHEMATICS_CONFIG = {
    'ncc_1701': {
        'name': 'NCC-1701 Enterprise',
        'initial_pitch': 0.0,
        'initial_roll': 0.0,
        'initial_yaw': 90.0,
        'description': 'Constitution-class starship',
        'type': 'spaceship'
    },
    'worf': {
        'name': 'Worf',
        'initial_pitch': -90.0,  # Face camera (front view)
        'initial_roll': 0.0,
        'initial_yaw': 0.0,
        'description': 'Character - front view for facial examination',
        'type': 'character'
    },
    'apollo_1570': {
        'name': 'Apollo NCC-1570',
        'initial_pitch': 0.0,    # Keep horizontal
        'initial_roll': 0.0,
        'initial_yaw': 90.0,     # Rotate to side view like arrow
        'description': 'Spaceship - side profile view',
        'type': 'spaceship'
    },
    'apollo_1701_refit': {
        'name': 'Apollo NCC-1701 Refit',
        'initial_pitch': 0.0,    # Keep horizontal
        'initial_roll': 0.0,
        'initial_yaw': 90.0,     # Rotate to side view like arrow
        'description': 'Spaceship - side profile view',
        'type': 'spaceship'
    }
}

# Model keys shown in the Ship submenu (others remain in config but are not rendered in the UI).
SCHEMATICS_VISIBLE_KEYS = ('ncc_1701', 'apollo_1570')

# Sensor configuration for 3D viewer (separate from other app sensor usage)
SENSOR_3D_CONFIG = {
    # Balanced noise filtering - responsive but stable
    'primary_deadzone': 2.0,     # Smaller deadzone for responsiveness
    'secondary_deadzone': 3.0,   # Slightly larger for secondary axes
    'diagonal_threshold': 8.0,   # Allow diagonal movements more easily
    'noise_ratio_threshold': 0.3, # More lenient filtering
    
    # Increased sensitivity for better responsiveness
    'primary_sensitivity': 0.8,   # More responsive
    'secondary_sensitivity': 0.6, # More responsive for secondary axis
    'tertiary_sensitivity': 0.4,  # More responsive for tertiary axis
    
    # Lighter smoothing for responsiveness
    'smoothing_factor': 0.3,     # Less aggressive smoothing (30% of new reading)
}

def get_model_config(model_key):
    """Get configuration for a specific model."""
    return SCHEMATICS_CONFIG.get(model_key, {
        'name': 'Unknown Model',
        'initial_pitch': 0.0,
        'initial_roll': 0.0,
        'initial_yaw': 0.0,
        'description': 'Default configuration',
        'type': 'unknown'
    })

def get_initial_rotations(model_key):
    """Get initial rotation values for a model."""
    config = get_model_config(model_key)
    return {
        'pitch': config['initial_pitch'],
        'roll': config['initial_roll'], 
        'yaw': config['initial_yaw']
    } 