import pathlib
import textwrap
from dotenv import load_dotenv
import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
load_dotenv()
import os


# GOOGLE_API_KEY = os.getenv(GOOGLE_API_KEY)
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key='AIzaSyA8e0v4a-0IVE2QGgpTTblVvlP0Va0honE')

# for m in genai.list_models():
#   if 'generateContent' in m.supported_generation_methods:
#     print(m.name)

model = genai.GenerativeModel('gemini-pro')

Purpose =''' 
You are a bot that speaks in a VR for post-stroke therapy game. Be very encouraging and kind. The philospophy of our training is to use Repetitive Task Training (RTT) which helps Relearning Lost Skills, Progressively improving on the same tasks , and Neuromuscular Rehabilitation (NMRE) - reinforcing new neural connections and promoting muscle memory. 
Be very very careful with your words, users may have trauma, PTSD, etc since they have all expericned a stroke.

We will tell you if the user is doing = very good, good, ok, bad, very badly in a game. 
If the user is doing very good give encouraging words like "way to go," "amazing," etc. Say we will now try a harder level.

If the user is doing very bdaly, give encouraging words like "this is ok" let's try something else, I know you can do it, etc. 
'''

Game1='''
VR Game for Forearm Flexors - virtual gardening

Targeted Muscles: Flexor carpi radialis, Flexor carpi ulnaris, Flexor digitorum superficialis (muscles along the inner side of the forearm responsible for wrist and finger flexion).
Game Concept: Players engage in virtual gardening tasks like pulling weeds (grass), which require gripping and wrist flexion.
Adjustability:
Easier: Objects are larger and closer to the user.
Harder: Objects are smaller and positioned further away, requiring more precise and extended movements.

Gameflow and scene: 
The user can see grass in front of them. They use either their right or left hand to pick up grass. 
The user is sitting down. 
There are a number of weed grass placed on the mud in the VR world. 

The data you get: Number of plants, distance from global origin (x,y,z) of every plant, Size of grass, and time left passed/elapsed.
'''

Game2='''
Bicep Builder - VR Game for Biceps Brachii - rowing 
Targeted Muscle: Biceps Brachii (front of the upper arm, crucial for bending the elbow).
Game Concept: Players simulate rowing activities, which involve repeated elbow flexion. 
Adjustability:
Easier: More time to complete a revolution as compared to the previous round
Harder: Less time to complete a revolution as compared to the previous round

Gameflow and scene: 
Shows count-down timer for each rowing revolution 
Shows number of revolutions completed (rowing actions)
Shows the person in a boat (the user is sitting in the boat) 

The data you get: Time left for the rowing
'''

# user_input comes from unity

def create_prompt(user_input, game):
    # Combine the user input with the game context and purpose
    if game==1:
        full_prompt = Purpose + ' '+ Game1 + ' '+ user_input
    elif game ==2:
       full_prompt = Purpose +' '+ Game2 +' '+ user_input
    return full_prompt



response = model.generate_content(create_prompt)
print(response.text)
# response = model.generate_content("What is the meaning of life?", stream=True)

