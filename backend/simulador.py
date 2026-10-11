from dataclasses import dataclass, asdict
import asyncio
from math import sqrt


# A dataclass keeps the truck state as plain, typed data: easy to serialize
# to JSON / Redis and to send to the frontend later.

ROUTE = [
        (50, 20),
        (55, 22),
        (70, 40),
    ]


@dataclass
class Truck:
    id: int
    x: float
    y: float

    status: str
    payload_tons: float
    target_index: int

TRUCKS = [Truck(
        id=1,
        x=10,
        y=80,

        payload_tons=0,
        status="traveling",
        target_index=0
    ),
    Truck(
        id=2,
        x=5,
        y=30,
    
        payload_tons=0,
        status="traveling",
        target_index=0
    ),
    Truck(
        id=3,
        x=12,
        y=90,
    
        payload_tons=0,
        status="traveling",
        target_index=0
    ),
    ]  
def fleet_snapshot():
    return [asdict(truck) for truck in TRUCKS] 
    # if truck target_index = ROUTE5 entao ele se move 5 casas no eixo x e 2 no eixo y, quando ele chega la ele vai estar ou loading ou hauling ou dumping ou stoped
    # ele precisa ter todos esses estados em status
    # e a cada 1 segundo ele se move em direçao a um target_index, loop de increase ?
    # calcular a direçao que o truck precisa se mover no eixo x e y, a cada 1 segundo a "velocidade" vai ser 5 pontos
    # para calcular a direçao que ele precisa se mover direçao_x = delta_x /ditancia total, delta_x = target_x - current_x, distancia total = sqrt(delta_x^2 + delta_y^2)
    # para atualizar as cordenadas truck.x = truck.x + (direction_x * speed * time) e truck.y = truck.y + (direction_y * speed * time)
    # direction_x: proporção do movimento no eixo X.

async def simulate_truck_movement(truck):
    """
    Runs the truck's state machine forever, one tick per second.

    States: traveling -> loading -> hauling -> dumping -> traveling ...
    Each loop iteration either:
      - performs the action at the current waypoint (load / dump / turn around), or
      - moves the truck one step towards the current waypoint.
    """
    # 1. Set the movement speed and update interval
    speed = 5   # distance units per second
    time = 1    # tick duration in seconds (dt)
    # Waypoints: index 0 = load point, 1 = dump point, 2 = return point
    
    max_capacity = 10  # tons
    loading_rate = 2   # tons per second (also used as the dumping rate)

    while True:
        target_index = truck.target_index
        # Access the coordinates of the current target waypoint
        target = ROUTE[target_index]

        # Split the target into its X and Y coordinates
        target_x, target_y = target
        # Calculate delta_x and delta_y (vector from the truck to the target)
        delta_x = target_x - truck.x
        delta_y = target_y - truck.y
        # 4. Calculate the remaining distance (Euclidean norm of the delta vector)
        distance_remaining = sqrt(delta_x**2 + delta_y**2)



        # Arrival check uses a tolerance instead of exact equality, because
        # float coordinates rarely match the target exactly.
        if distance_remaining < 0.5:
            if truck.target_index == 0:
                # Load point: add payload each tick until the truck is full
                print(f"o truck: {truck.id} chegou ao  1 destino, {truck.status} payload em:{truck.payload_tons} tons")
                truck.status = "loading"               
                # loading logic
                truck.payload_tons += loading_rate * time
                await asyncio.sleep(1)
                # Clamp so the payload never exceeds the truck's capacity
                if truck.payload_tons > max_capacity:
                    truck.payload_tons = max_capacity

                # Full: switch to hauling and head to the dump point
                if truck.payload_tons >=  max_capacity:
                    print(f"truck: {truck.id} carregado payload em:{truck.payload_tons} tons")
                    truck.status = "hauling"
                    truck.target_index += 1
            elif truck.target_index == 1:
                # Dump point: unload payload each tick until empty
                truck.status = "dumping"
                print(f"truck: {truck.id} chegou ao destino 2, {truck.status} Payload:{truck.payload_tons}")

                truck.payload_tons -= loading_rate * time
                await asyncio.sleep(1)
                # Empty: travel (unloaded) to the next waypoint
                if truck.payload_tons == 0:
                    print(f"carga de {truck.id} zerada indo para o proximo destino")
                    truck.status = "traveling"
                    truck.target_index += 1
            elif truck.target_index ==2:
                # Return point: wrap the index back to 0 to restart the haul cycle
                print(f"truck: {truck.id} chegou ao destino 3, voltando para rota incial")
                truck.status = "traveling"

                # Modulo makes the ROUTE circular, so the truck loops forever
                truck.target_index = (truck.target_index + 1) % len(ROUTE)
            # Skip the movement step: the truck is stationary while at a waypoint
            continue
        # Calculate the normalized direction (unit vector): only the
        #    direction matters here, the step size comes from speed * time
        direction_x = delta_x / distance_remaining
        direction_y = delta_y / distance_remaining

        #  Calculate movement based on speed and elapsed time (d = v * t)
        movement = speed * time
        #  Prevent overshooting the target: on the last step, move only
        #    the remaining distance so the truck lands exactly on the waypoint
        if movement > distance_remaining:
            movement = distance_remaining
        #  Update truck.x and truck.y (only moving states change position)
        if truck.status == "hauling" or  truck.status == "traveling"  :
            truck.x += direction_x * movement
            truck.y += direction_y * movement
        
        print(f" truck:{truck.id},{truck.status}, truck position x:{truck.x} y {truck.y}")
    
        #  Wait before the next update using asyncio.sleep()
        #     (non-blocking: other trucks/tasks can run during this pause)
        await asyncio.sleep(1)

async def main():
    # Truck starts empty, away from the ROUTE, heading to load point
    
    print(fleet_snapshot())

    await asyncio.gather (simulate_truck_movement(TRUCKS[0]),
                          simulate_truck_movement(TRUCKS[1]),
                          simulate_truck_movement(TRUCKS[2])
                          )


if __name__ == "__main__":
    asyncio.run(main())


