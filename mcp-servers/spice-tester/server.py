# /// script
# dependencies = [
#   "mcp",
#   "numpy",
# ]
# ///

from mcp.server.fastmcp import FastMCP
import numpy as np

mcp = FastMCP("SPICE-Physics-Verifier")

@mcp.tool()
def simulate_buck_step(vin: float, duty_cycle: float, f_sw: float, L: float, C: float, R: float, steps: int = 500) -> dict:
    """
    Simula numericamente el transitorio de arranque de un convertidor Buck ideal
    para validar que el motor de la app produce las curvas correctas de i_L(t) y v_C(t).
    """
    dt = (1.0 / f_sw) / 50.0  # 50 pasos por periodo de conmutacion
    i_L = 0.0
    v_C = 0.0
    t = 0.0
    
    historial_v = []
    historial_i = []
    
    for _ in range(steps):
        # Estado del interruptor PWM (1 = ON, 0 = OFF)
        periodo_actual = (t * f_sw) % 1.0
        sw_on = 1.0 if periodo_actual < duty_cycle else 0.0
        
        # Tension en el nodo de conmutacion (con diodo libre ideal: no baja de 0V si i_L > 0)
        v_sw = vin if sw_on else (0.0 if i_L > 0 else v_C)
        
        # Ecuaciones diferenciales (Euler hacia adelante / Backward aproximado)
        di_L = ((v_sw - v_C) / L) * dt
        i_L = max(0.0, i_L + di_L)  # Modo de conduccion discontinua (DCM) soportado por el diodo
        
        dv_C = ((i_L - (v_C / R)) / C) * dt
        v_C += dv_C
        
        t += dt
        historial_v.append(round(v_C, 4))
        historial_i.append(round(i_L, 4))
        
    return {
        "v_out_teorico_ccm": round(vin * duty_cycle, 3),
        "v_out_final_simulado": historial_v[-1],
        "i_L_max_pico": max(historial_i),
        "muestra_curva_vC": historial_v[::25],
        "muestra_curva_iL": historial_i[::25]
    }

if __name__ == "__main__":
    mcp.run()