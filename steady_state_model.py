import numpy as np

def building_heat_loss(T_internal_F, T_external_F, R_wall, area, ACH, volume):
    """
    Calculates total heat loss rate from building per second
    in Watts, given internal and external temperature

    T_internal_F: Temperature inside the room in Fahrenheit
    T_external_F: Temperature outside the building in Fahrenheit
    R_wall: insulation R value of wall
    ACH: Air Changes per Hour by infiltration
    volume:
    area: total surface area through which heat can escape (walls, ceiling, floor, windows)
    """
    T_internal_K = (T_internal_F - 32) * 5/9 + 273.15
    T_external_K = (T_external_F - 32) * 5/9 + 273.15

    delta_T = T_internal_K - T_external_K
    # conductive heat loss through building
    Q_conductive = (delta_T / R_wall) * area

    # infiltration loss - air leaking in and out
    rho_air = 1.2 # unit - kg/m3
    cp_air = 1005 # unit J/kg.K
    Q_infiltration = (ACH / 3600) * volume * rho_air * cp_air * delta_T

    Q_total = Q_conductive + Q_infiltration

    return Q_total

def sat_pressure(T_F):
    """
    Calculates saturation pressure, the maximum pressure 
    water vapor can exert at a given temperature
    
    T_F: Temperature in Fahrenheit
    """
    # Convert to Celsius for ASHRAE Eq. 5 (IAPWS-IF97)
    # ASHRAE Fundamentals 2025, Chapter 1, Equation 5
    T_C = (T_F - 32) * 5/9
    T_K = T_C + 273.15
    theta = T_K + (-0.238555575678e0) / (T_K - 0.650175348448e3)
    A = theta**2 + 0.116705214528e4 * theta - 0.724213167032e6
    B = -0.170738469401e2 * theta**2 + 0.120208247025e5 * theta - 0.323255503223e7
    C = 0.149151086135e2 * theta**2 - 0.482326573616e4 * theta + 0.405113405421e6
    p_ws = 1000 * (2*C / (-B + (B**2 - 4*A*C)**0.5))**4  # kPa
    return p_ws

def indoor_humidity(T_internal_F, T_external_F, RH_external):
    """
    Calculates indoor relative humidity by assuming indoor air 
    carries the same absolute moisture content as outdoor air, 
    then recalculates what that moisture level feels like at 
    the warmer indoor temperature

    T_internal_F: Indoor temperature in Fahrenheit
    T_external_F: External Temperature in Fahrenheit
    RH_external: External Relative Humidity
    """
    """
    ASHRAE Fundamentals 2025 Chapter 1
    Humidity ratio W: Equation 21
    Saturation pressure: Equation 5
    """
    P_atm = 101.325  # kPa

    # Outdoor absolute humidity (humidity ratio W)
    P_sat_ext = sat_pressure(T_external_F)
    p_w = RH_external * P_sat_ext
    W = 0.621945 * p_w / (P_atm - p_w)  # Eq. 21 ASHRAE Ch.1

    # Indoor RH at indoor temp, same W (infiltration assumption)
    P_sat_int = sat_pressure(T_internal_F)
    p_w_int = W * P_atm / (0.621945 + W)
    RH_internal = p_w_int / P_sat_int
    RH_internal = min(RH_internal, 1.0)

    return RH_internal

def comfort_model(T_internal_F, RH_internal, T_wall_F):
    """
    Calculates total heat loss from the human body via radiation to walls, 
    convection to air, and evaporation. Compares against metabolic rate to 
    give a Hot/Cold/Good verdict.

    T_internal_F: Indoor Temperature in Fahrenheit
    RH_internal: Indoor Relative Humidity
    T_wall_F: Wall Temperature in Fahrenheit
    """
    
    """
    Radiation + convection heat loss from human body
    Taken from Dr. Gray's matlab code
    ASHRAE Fundamentals 2025 Chapter 9
    """
    epsilon = 0.98
    sigma = 5.6703e-8
    H = 5
    T_skin_K = 310.15  # 37C in Kelvin

    T_wall_K = (T_wall_F - 32) * 5/9 + 273.15
    T_air_K  = (T_internal_F - 32) * 5/9 + 273.15

    q_rad  = epsilon * sigma * (T_skin_K**4 - T_wall_K**4)
    q_conv = H * (T_skin_K - T_air_K)
    # Evaporative heat loss — ASHRAE Fundamentals Ch.9
    # q_evap decreases as RH increases (less evaporation possible)
    # At rest: ~10 W/m2 at low RH, approaches 0 at high RH
    q_evap = 10 * (1 - RH_internal)  # simplified linear approximation
    q_total = q_rad + q_conv + q_evap

    METABOLIC_RATE = 60  # W/m2, seated quiet, ASHRAE Fundamentals Ch.9 Table 4

    tolerance = 15  # W/m2 either side — needs calibration from your survey data

    if q_total < METABOLIC_RATE - tolerance:
        verdict = "Hot"
    elif q_total > METABOLIC_RATE + tolerance:
        verdict = "Cold"
    else:
        verdict = "Good"

    return q_total, verdict


def steady_state_model(T_external_F, RH_external, T_setpoint_F, R_wall, A_envelope, ACH, volume):
    """
    Takes all 3 steps together
    """

# Sweep outdoor conditions to build database
