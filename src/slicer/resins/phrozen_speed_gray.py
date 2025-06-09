from src.slicer.core.resin import Resin, ResinProperties, ExposureSettings, MovementSettings, SpecialSettings, ResinRegistry


properties = ResinProperties(
    viscosity=200,
    density=1.13,
    currency="EUR",
    price=44.63
)

exposure_settings = ExposureSettings(
    light_off_delay=2,
    bottom_layers=5,
    bottom_exp_time=30,
    transition_layers=5,
    h_a=150,
    T_c=0.5,
    overlap=0.2
)

movement_settings = MovementSettings(
    bottom_lift_height=8,
    bottom_lift_speed=2,
    bottom_retract_speed=2,
    normal_lift_height=6,
    normal_lift_speed=2.5,
    normal_retract_speed=2.5,
    max_acceleration=20,
    use_TSMC=True
)

special_settings = SpecialSettings(
    light_pwm=255,
    anti_aliasing=4,
    min_aa=230,
    print_time_compensation=0.0,
    shrinkage_compensation=0.0,
    intelli_mode=True
)


phrozen_speed_gray = Resin(
    name="Phrozen Speed Gray",
    properties=properties,
    exposure_settings=exposure_settings,
    movement_settings=movement_settings,
    special_settings=special_settings,
)


ResinRegistry.register(phrozen_speed_gray)