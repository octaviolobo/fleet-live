from dataclasses import dataclass
import asyncio
from math import sqrt
@dataclass
class Truck:
    id: int
    x: float
    y: float
    
    status: str 
    payload_tons: float 
    target_index: int


    ##if truck target_index = route5 entao ele se move 5 casas no eixo x e 2 no eixo y, quando ele chega la ele vai estar ou loading ou hauling ou dumping ou stoped
    # ele precisa ter todos esses estados em status
    # e a cada 1 segundo ele se move em direçao a um target_index, loop de increase ?
    #calcular a direçao que o truck precisa se mover no eixo x e y, a cada 1 segundo a "velocidade" vai ser 5 pontos
    #para calcular a direçao que ele precisa se mover direçao_x = delta_x /ditancia total, delta_x = target_x - current_x, distancia total = sqrt(delta_x^2 + delta_y^2)
    # para atualizar as cordenadas truck.x = truck.x + (direction_x * speed * time) e truck.y = truck.y + (direction_y * speed * time)
    #direction_x: proporção do movimento no eixo X.

async def simulate_truck_movement(truck):
         # 1. Set the movement speed and update interval
    speed = 5 
    time = 1  # seconds 
    route = [
            (50, 20),
            (55, 22),
            (70, 40),
        ]
    max_capacity = 10
    loading_rate = 2

    while True:
        target_index = truck.target_index
        # Acesse a coordenada correspondente na rota
        target = route[target_index]

        # Separe a coordenada X da coordenada Y
        target_x, target_y = target
        # 3. Calculate delta_x and delta_y
        delta_x = target_x - truck.x
        delta_y = target_y - truck.y
        # 4. Calculate the remaining distance 
        distance_remaining = sqrt(delta_x**2 + delta_y**2)

                   
        

        if distance_remaining < 0.5:
            if truck.target_index == 0:
                print(f"o truck chegou ao  1 destino, carregando payload em:{truck.payload_tons} tons")
                truck.status = "loading"
                if truck.status == "loading":
                #logica de carregamento
                    truck.payload_tons += loading_rate * time
                    await asyncio.sleep(1)
                if truck.payload_tons > max_capacity:
                    truck.payload_tons = max_capacity
    
                if truck.payload_tons >=  max_capacity:
                    print(f"caminhao carregado payload em:{truck.payload_tons} tons")
                    truck.status = "hauling"
                    truck.target_index += 1
            elif truck.target_index == 1:
                print("truck chegou ao ponto 2, dumping...")
                truck.status = "dumping"
                truck.payload_tons -= loading_rate * time
                await asyncio.sleep(1)
                if truck.payload_tons == 0:
                    print("carga zerada indo para o proximo destino")
                    truck.target_index += 1
            elif truck.target_index == 2:
                print("truck chegou ao destino 3, Finalizando..")
                truck.status = "stoped"
                if truck.status == "stoped":
                    break
                    



            if truck.target_index < len(route):
                continue
            else:
                print("rota concluida")
                break
        


        # 5. Check #if the truck has arrived
        '''if truck.x and truck.y == target_x and target_y:
            print("truck arrived at target location") 
        if truck.x and truck.y != target_x and target_y:
            if final_truck.x - target_x > 0.5:
                print("truck arrived at target location")
            else:
                print(f"truck falta{delta_x} para chegar")
            if final_truck.y - target_y > 0.5:
                print("truck arrived at target location")
            else:
                print(f"truck falta{delta_y} para chegar")'''
        # 6. Calculate the normalized direction
        direction_x = delta_x / distance_remaining
        direction_y = delta_y / distance_remaining

        # 7. Calculate movement based on speed and elapsed time
        movement = speed * time
        # 8. Prevent overshooting the target
        if movement > distance_remaining:
            movement = distance_remaining
        # 9. Update truck.x and truck.y
        if truck.status == "hauling" or truck.status == "dumping" or truck.status == "traveling"  :
            truck.x += direction_x * movement
            truck.y += direction_y * movement
        if distance_remaining > 0.5:
            print(f"truck hauling, truck position x:{truck.x} y {truck.y}")
        
        # 10. Wait before the next update using asyncio.sleep()
        await asyncio.sleep(1)

async def main():
    truck = Truck(
        id=1,
        x=10,
        y=80,
       
        payload_tons=0,
        status="traveling",
        target_index=0

    )
    
    await simulate_truck_movement(truck)

asyncio.run(main())


        
    