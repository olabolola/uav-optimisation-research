import gym
import UAV_RL_env
import numpy as np
import UAV_RL_env.envs.celes as celes
import numpy as np
import helper_functions
no_trucks = 2
no_drones = 1
env = gym.make('HDS-v0', no_customers = 100, no_trucks = no_trucks, no_drones = no_drones)

env.reset()

truck_actions = []
drone_actions = []


for _ in range(no_trucks):
    x_target_truck = np.random.randint(0, 4999)
    y_target_truck = np.random.randint(0, 4999)
    position = celes.Position(x_target_truck, y_target_truck)
    truck_actions.append(("move_towards_position", (position)))

for _ in range(no_drones*no_trucks):
    drone_actions.append("nothing")

action = (truck_actions, drone_actions)
for _ in range(100):
    env.step(action)
# env.render()

for i in range(len(drone_actions)):
    drone_actions[i] = ("go_to_closest_truck", celes.Position(2500, 2500))
for i in range(len(truck_actions)):
    truck_actions[i] = (("nothing"), None)
action = (truck_actions, drone_actions)
for _ in range(20):
    a, b, c, info = env.step(action)
    env.render()

helper_functions.make_video()


# def make_video():
#     # windows:
#     fourcc = cv2.VideoWriter_fourcc(*'XVID')
#     # Linux:
#     #fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#     out = cv2.VideoWriter('qlearn.avi', fourcc, 60.0, (1200, 900))

#     for i in range(20):
#         img_path = f"hind{i}.png"
#         print(img_path)
#         frame = cv2.imread(img_path)
#         out.write(frame)

#     out.release()


# make_video()

# import subprocess, os
# os.chdir(r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code')
# for i in range(20):
#     subprocess.call([
#             'ffmpeg', '-framerate', '8', '-i', f'hind{i}.png', '-r', '30', '-pix_fmt', 'yuv420p',
#             'video_name.mp4'
#         ])

#MAKE THE VIDEO!!!



# for item in info:
#     print(item)
# for _ in range(10):
#     env.step(action)
# env.step(action)
# env.step(action)
# env.render()





