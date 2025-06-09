from src.slicer.core.resin import Resin, ResinProperties, ExposureSettings, MovementSettings, SpecialSettings, ResinRegistry, CalibrationResin


properties = ResinProperties(
    viscosity=230,
    density=1.13,
    currency="EUR",
    price=25.00
)

exposure_settings = ExposureSettings(
    light_off_delay=2,
    bottom_layers=1,
    bottom_exp_time=30,
    transition_layers=3,
    h_a=84,
    T_c=0.8,
    overlap=0.010 # 10um
)

movement_settings = MovementSettings(
    bottom_lift_height=8,
    bottom_lift_speed=1.5,
    bottom_retract_speed=1.5,
    normal_lift_height=6,
    normal_lift_speed=2,
    normal_retract_speed=2,
    max_acceleration=20,
    use_TSMC=True
)

special_settings = SpecialSettings(
    light_pwm=255,
    anti_aliasing=4,
    min_aa=255,
    print_time_compensation=0.0,
    shrinkage_compensation=0.0,
    intelli_mode=True
)

anycubic_standard_clear = Resin(
    name="Anycubic Standard Clear",
    properties=properties,
    exposure_settings=exposure_settings,
    movement_settings=movement_settings,
    special_settings=special_settings,
)


ResinRegistry.register(anycubic_standard_clear)