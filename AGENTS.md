# SketchSPICE - Simulador Interactivo de Circuitos a Mano Alzada

## Vision y Arquitectura
Aplicacion para tablets donde el usuario dibuja esquemas electronicos con un stylus, un motor de vision los convierte en un grafo topologico, un motor numerico resuelve el estado transitorio (paso a paso en el tiempo $\Delta t$) y el lienzo anima la carga/descarga de condensadores, flujo de corriente en bobinas y niveles de tension.

## Contrato de Datos (Pipeline Estricto)
Las tres capas del proyecto estan desacopladas y solo se comunican mediante estructuras tipadas:
1. `StrokeData`: Array de puntos `(x, y, pressure, timestamp)` capturados en `src/canvas/`.
2. `CircuitGraph`: Nodos electricos y ramas reconocidos por `src/vision/` -> Genera un JSON y un `Netlist` estandar SPICE.
3. `SimulationFrame`: Estado instantaneo en $t$: vector de voltajes nodales $V_n(t)$ y corrientes de rama $I_b(t)$ calculado en `src/simulation/`.

## Reglas de Oro del Codigo
- **Hilo de UI sagrado:** Jamas ejecutes algebra matricial ni simulaciones transitorias en el hilo principal de renderizado. El motor de simulacion debe correr en un Web Worker / Isolate independiente.
- **Fisica real, no animaciones falsas:** La velocidad de las particulas (electrones) en una rama debe ser estrictamente proporcional a la corriente instantanea $I(t)$ calculada. El color de cada nodo debe interpolarse segun su voltaje real $V(t)$.
- **Delegacion de Subagentes:**
  - Para geometria, suavizado de lapiz y shaders/animacion: delega a `@canvas-ui`.
  - Para segmentacion de trazos, ML y conexion de nodos: delega a `@vision-ml`.
  - Para matrices MNA, metodos numericos ( Trapecios / Backward Euler ) y modelos de componentes (MOSFETs, diodos, RLC): delega a `@spice-physics`.