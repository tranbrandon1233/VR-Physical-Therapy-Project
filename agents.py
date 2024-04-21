from uagents import Agent, Context, Model, Protocol, Bureau
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os
import random as rand
from IPython.display import Markdown
import google.generativeai as genai
import textwrap

from IPython.display import display
from IPython.display import Markdown
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

load_dotenv()

data_to_unity = dict()

FIREBASE_URL = os.getenv("FIREBASE_URL")

GEMINI_API_KEY= os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred, {
  'databaseURL': FIREBASE_URL
})


genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-pro')
 
class PatientData(Model):
    name: str
    issues: list[str]
    severity: int

class FFTask(Model):
    difficulty: int
    num_plants:int
    distance: tuple[list[int],int,list[int]]
    size:int
    handedness: str
    time: int

class BBTask(Model):
    difficulty: int
    timer_per_revolution: int
    revs_remaining:int
    time: int
    

class PPTask(Model):
    difficulty: int
    arrangement: list[list[str]] # Use "in{x}" for inserting book number x and "out{x}" for removing book number x or "N" for neither
    grid_size:int

class GameRequest(Model):
    type: str
    game: FFTask|BBTask|PPTask

class EndGame(Model):
    win_or_lose: str
    score: int

class SetParams(Model):
    game_type: str
    difficulty: int

placeholder = Agent(name="placeholder", seed="task_man recovery phrase")
game_master = Agent(name="game_master")
#print(placeholder.address)

protocol = Protocol(name="proto")
game_protocol = Protocol(name="game_proto")

class PDF(FPDF):
    def __init__(self, font_path_en):
        super().__init__()
        self.font_path_en = font_path_en
    def header(self):
        if self.page_no() == 1: # Create the header only on the first page with the title, space to write a name,the date, and a line break
            self.set_font('Noto Sans TC', 'B', 15)
            self.cell(0, 10, 'FINAL REPORT', 0, align='C', new_x="LMARGIN", new_y="NEXT") # Since the ln parameter is deprecated, we must use the new_x and new_y parameters instead and explicitly assign the align parameter to avoid confusion
            self.set_font('Noto Sans TC', '', 12)
            self.cell(0, 10, 'Date: 2024-04-08', 0, align='R', new_x="LMARGIN", new_y="NEXT")
            self.ln(10)

    def footer(self):
        if self.page_no() > 1: # Create the footer with the page number on every page except the first
            self.set_y(-15)
            self.set_font('Noto Sans TC', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, align='C',new_x="RIGHT", new_y="TOP",)
            
    def add_text(self, text,image_path=None):
        self.set_font('Noto Sans TC', '', 10)
        self.multi_cell(text=text,new_x="RIGHT", new_y="TOP",h=10,w=0)
        self.ln(9)  # Adjust for spacing
        
        if image_path:
            # Add image to the right side of the question text
            self.image(image_path, x=85, y=self.get_y() - 50, h=10)  # Adjust x, y, h as needed

# Define an async function to get 'last_score' from Firebase every second
@placeholder.on_interval(period=1)
async def get_score(ctx:Context):
    
        ctx.storage.set("time_remaining", ctx.storage.get("time_remaining") - 1)
        ctx.storage.set("secsSinceLastScore", ctx.storage.get("secsSinceLastScore") + 1)
        # Get a database reference to our posts
        # Read the data at the posts reference (this is a blocking operation)
        ref = db.reference('/score')
        last_score = ref.get()["score"]
        if ctx.storage.get("event_log") is None:
            ctx.storage.set("event_log", "")
        if last_score > ctx.storage.get("last_score"):
            ctx.storage.set("secsSinceLastScore", 0)
            if last_score >= ctx.storage.get("winning_score"):
               
                ctx.storage.set("time_remaining",0)
                if ctx.storage.get("difficulty") < 2:
                    ctx.storage.set("difficulty", ctx.storage.get("difficulty") + 1)  
                    ctx.storage.set("event_log", ctx.storage.get("event_log") + "\n\nPlayer has won a round of " + str(ctx.storage.get("game_type")) + ". The difficulty level of "+str(ctx.storage.get("game_type"))+" has been increased to "+str(ctx.storage.get("difficulty"))+".")
                    ctx.logger.info("\n\nPlayer has won a round of " + str(ctx.storage.get("game_type")) + ". The difficulty level of "+str(ctx.storage.get("game_type"))+" has been increased to "+str(ctx.storage.get("difficulty"))+".")
                    if ctx.storage.get("time_remaining") == 0:
                        ratio = 0
                    else:
                        ratio = (ctx.storage.get("winning_score")-ctx.storage.get("last_score"))/ctx.storage.get("time_remaining")
                    #giveInstructions(ctx.storage.get("game_type"),"Good",ctx.storage.get("last_score"),ctx.storage.get("time_remaining"),ratio,ctx.storage.get("winning_score")-ctx.storage.get("last_score")) 
                    await ctx.send(game_master.address,SetParams(game_type=ctx.storage.get("game_type"),difficulty=ctx.storage.get("difficulty")))
                else:
                    ctx.storage.set("event_log", ctx.storage.get("event_log") + "\n\nPlayer has beaten " + str(ctx.storage.get("game_type")) + "!")
                    if ctx.storage.get("time_remaining") == 0:
                        ratio = 0
                    else:
                        ratio = (ctx.storage.get("winning_score")-ctx.storage.get("last_score"))/ctx.storage.get("time_remaining")
                    #giveInstructions(ctx.storage.get("game_type"),"Win",ctx.storage.get("last_score"),ctx.storage.get("time_remaining"),ratio,ctx.storage.get("winning_score")-ctx.storage.get("last_score")) 
            else:
                ctx.storage.set("last_score", last_score)
                
        elif (ctx.storage.get("secsSinceLastScore") > 30 or ctx.storage.get("time_remaining") <= 0):
            
            if ctx.storage.get("difficulty") > 0:
                ctx.storage.set("difficulty", ctx.storage.get("difficulty") - 1)
                if ctx.storage.get("time_remaining") == 0:
                        ratio = 0
                else:
                    ratio = (ctx.storage.get("winning_score")-ctx.storage.get("last_score"))/ctx.storage.get("time_remaining")
                #giveInstructions(ctx.storage.get("game_type"),"Bad",ctx.storage.get("last_score"),ctx.storage.get("time_remaining"),ratio,ctx.storage.get("winning_score")-ctx.storage.get("last_score")) 
                
                if(ctx.storage.get("secsSinceLastScore") > 20):
                    ctx.storage.set("event_log", ctx.storage.get("event_log") + "\n\nIt's been 20 seconds since the player scored a point, so the difficulty level of "+str(ctx.storage.get("game_type"))+" has been decreased to "+str(ctx.storage.get("difficulty"))+".")
                else:
                    ctx.storage.set("event_log", ctx.storage.get("event_log") + "\n\nThe time remaining for "+str(ctx.storage.get("game_type")) + " is now 0. The difficulty level of "+str(ctx.storage.get("game_type"))+" has been decreased to "+str(ctx.storage.get("difficulty"))+".")
                await ctx.send(game_master.address,SetParams(game_type=ctx.storage.get("game_type"),difficulty=ctx.storage.get("difficulty")))
                ctx.storage.set("secsSinceLastScore", 0)
                ctx.storage.set("time_remaining",0)
            else:
                ctx.storage.set("event_log", ctx.storage.get("event_log") + "\n\nPlayer has lost " + str(ctx.storage.get("game_type")) + ".")
                if ctx.storage.get("time_remaining") == 0:
                        ratio = 0
                else:
                    ratio = (ctx.storage.get("winning_score")-ctx.storage.get("last_score"))/ctx.storage.get("time_remaining")
                #giveInstructions(ctx.storage.get("game_type"),"Lose",ctx.storage.get("last_score"),ctx.storage.get("time_remaining"),ratio,ctx.storage.get("winning_score")-ctx.storage.get("last_score")) 
                
@placeholder.on_event("startup")
async def start(ctx:Context):
    ctx.logger.info("Hello, I will be your personal physical therapist today. Let's get started!")
    ctx.storage.set("event_log", "Beginning of the session.")
    ctx.storage.set("playedAlready",None)
    ctx.storage.set("highlighted_muscles", [])
    ctx.storage.set("game_type", "Forearm Flexors")
    ctx.storage.set("secsSinceLastScore", 0)
    ctx.storage.set("last_score",0)
    ctx.storage.set("handedness","R")
    ctx.storage.set("time_remaining", 0)
    ctx.storage.set("winning_score", 0)
    ctx.storage.set("num_plants", 0)
    ctx.storage.set("distance", ([0,0],0,[0,0]))
    ctx.storage.set("size", 0)
    ctx.storage.set("time", 30)
    ctx.storage.set("prev_text_output", "")
    ctx.storage.set("text_output", "")
    
    

@game_master.on_message(model=SetParams,replies=GameRequest)
async def generate_challenge(ctx:Context,data,msg:SetParams):
    ctx.logger.info(f'Creating {msg.game_type} game with difficulty level {msg.difficulty}.')
    match msg.game_type:
        case "Forearm Flexors":
            ctx.storage.set("game_type","Forearm Flexors")
            ctx.storage.set("time_remaining", 30)
            if(ctx.storage.get("handedness") is None):
                ctx.storage.set("handedness","R")
            match msg.difficulty:
                case 0:
                    await ctx.send(game_master.address,GameRequest(type="FF",game=FFTask(difficulty=0,num_plants=10,distance=([1,3],1,[1,3]),size=7,handedness=ctx.storage.get("handedness"), time=10*6)))
                    ctx.storage.set("winning_score", 10)
                    ctx.storage.set("difficulty", 2)
                    ctx.storage.set("num_plants", 10)
                    ctx.storage.set("distance", ([1,3],1,[1,3]))
                    ctx.storage.set("size", 7)
                    ctx.storage.set("time", 30)
                    ctx.storage.set("difficulty", 0)
                case 1:
                    await ctx.send(game_master.address,GameRequest(type="FF",game=FFTask(difficulty=1,num_plants=15,distance=([2,4],1,[2,4]),size=5,handedness=ctx.storage.get("handedness"),time=15*4)))
                    ctx.storage.set("winning_score", 15)
                    ctx.storage.set("num_plants", 15)
                    ctx.storage.set("difficulty", 1)
                    ctx.storage.set("distance", ([2,4],1,[2,4]))
                    ctx.storage.set("size", 5)
                    ctx.storage.set("time", 30)
                    
                case 2:
                    await ctx.send(game_master.address,GameRequest(type="FF",game=FFTask(difficulty=2,num_plants=20,distance=([3,5],1,[3,5]),size=3,handedness=ctx.storage.get("handedness"),time=20*3)))
                    ctx.storage.set("winning_score", 20)
                    ctx.storage.set("num_plants", 20)
                    ctx.storage.set("difficulty", 0)
                    ctx.storage.set("distance", ([3,5],1,[3,5]))
                    ctx.storage.set("size", 3)
                    ctx.storage.set("handedness", ctx.storage.get("handedness"))
                    ctx.storage.set("time", 30)
        case "Bicep Builder":
            match msg.difficulty:
                case 0:
                    await ctx.send(game_master.address,GameRequest(type="BB",game=BBTask(difficulty=0,timer_per_revolution=10,revs_remaining=3,time=20*3)))
                    ctx.storage.set("winning_score", 3)
                    ctx.storage.set("time_remaining", 30)
                    data_to_unity["winning_score"] = 3
                    data_to_unity["difficulty"] = 2
                    data_to_unity["Bicep Builder"] = {"timer_per_revolution":10,"revs_remaining":3,"time":20*3}
                    
                case 1:
                    await ctx.send(game_master.address,GameRequest(type="BB",game=BBTask(difficulty=1,timer_per_revolution=8,revs_remaining=6,time=50)))
                    ctx.storage.set("winning_score",6)
                    ctx.storage.set("time_remaining", 50)
                    data_to_unity["winning_score"] = 6
                    data_to_unity["difficulty"] = 1
                    data_to_unity["Bicep Builder"] = {"timer_per_revolution":8,"revs_remaining":6,"time":50}
                case 2:
                    await ctx.send(game_master.address,GameRequest(type="BB",game=BBTask(difficulty=2,timer_per_revolution=6,revs_remaining=9,time=45)))
                    ctx.storage.set("winning_score", 9)
                    ctx.storage.set("time_remaining", 45)
                    data_to_unity["winning_score"] = 9
                    data_to_unity["difficulty"] = 0
                    data_to_unity["Bicep Builder"] = {"timer_per_revolution":6,"revs_remaining":9,"time":45}
                    
        case "Push and Place":
            ctx.storage.set("time_remaining", None)
            data_to_unity["Forearm Flexors"] = None
            data_to_unity["Bicep Builder"] = None
            match msg.difficulty:
                case 0:
                    books = getBooks(3,4)
                    await ctx.send(game_master.address,GameRequest(type="PP",game=PPTask(difficulty=0,arrangement=books,grid_size=3)))
                    ctx.storage.set("winning_score", 3)
                    ctx.storage.set("difficulty", 0)
                    data_to_unity["winning_score"] = 3
                    data_to_unity["difficulty"] = 0
                    data_to_unity["Push and Place"] = {"arrangement":books,"grid_size":3}
                    
                case 1:
                    books=getBooks(5,7)
                    await ctx.send(game_master.address,GameRequest(type="PP",game=PPTask(difficulty=1,arrangement=books,grid_size=5)))
                    ctx.storage.set("winning_score", 5)
                    ctx.storage.set("difficulty", 1)
                    data_to_unity["winning_score"] = 5
                    data_to_unity["difficulty"] = 1
                    data_to_unity["Push and Place"] = {"arrangement":books,"grid_size":5}
                case 2:
                    books=getBooks(7,10)
                    await ctx.send(game_master.address,GameRequest(type="PP",game=PPTask(difficulty=2,arrangement=books,grid_size=7)))
                    ctx.storage.set("winning_score", 7)
                    ctx.storage.set("difficulty", 2)
                    data_to_unity["winning_score"] = 7
                    data_to_unity["difficulty"] = 2
                    data_to_unity["Push and Place"] = {"arrangement":books,"grid_size":7}
                    
    ctx.logger.info(str(ctx.storage.get("game_type"))+" game started with difficulty level "+str(ctx.storage.get("difficulty"))+".")
    if ctx.storage.get("event_log") is None:
        ctx.storage.set("event_log", "")
    ctx.logger.info(str(ctx.storage.get("game_type"))+" game started with difficulty level "+str(ctx.storage.get("difficulty"))+".")
    ctx.storage.set("event_log", ctx.storage.get("event_log") + "\n\n"+str(ctx.storage.get("game_type"))+" game started with difficulty level "+str(ctx.storage.get("difficulty"))+".")
def getBooks(n,total_count):
    books = [["N" for _ in range(n)] for _ in range(n)]
    bookBools = [[False for _ in range(n)] for _ in range(n)]
    inFlag = True
    outFlag = False
    count = 1
    flattened = [item for sublist in bookBools for item in sublist]
    while False in flattened and count <= total_count:
        i = rand.randint(0,n-1)
        j = rand.randint(0,n-1)
        if bookBools[i][j] == False:
            bookBools[i][j] = True
            if inFlag == True:
                books[i][j] = "in" + str(count)
                inFlag = False
                outFlag = True
            elif outFlag == True:
                books[i][j] = "out" + str(count)
                inFlag = True
                outFlag = False
                count +=1
            flattened =  [item for sublist in bookBools for item in sublist]
    return books



@protocol.on_query(model=PatientData,replies=SetParams)
async def create_game(ctx: Context, data: PatientData,msg:PatientData):
    ctx.logger.info(f'Creating game for {msg.name}')
    ctx.storage.set("secsSinceLastScore", 0)
    ctx.storage.set("last_score",0)
    ctx.storage.set("handedness","R")
    ctx.storage.set("difficulty", 2-msg.severity)
    if any(issue in msg.issues for issue in ["Flexor carpi radialis"," Flexor carpi ulnaris", "Flexor digitorum superficialis"]):
        ctx.storage.set("highlighted_muscles",["Flexor carpi radialis"," Flexor carpi ulnaris", "Flexor digitorum superficialis"])
        ctx.storage.set("game_type", "Forearm Flexors")
        if ctx.storage.get("playedAlready") is None:
            ctx.storage.set("handedness","R")
            ctx.storage.set("playedAlready",True)
        else:
            ctx.storage.set("handedness","L")
            ctx.storage.set("playedAlready",None)
        setDifficulty(msg,ctx)
        giveInstructions("Forearm Flexors")
    elif "Biceps Brachii" in msg.issues:
        ctx.storage.set("game_type", "Bicep Builder")
        setDifficulty(msg,ctx)
        giveInstructions(2)
    elif "Triceps Brachii" in msg.issues:
        ctx.storage.set("game_type", "Push and Place")
        setDifficulty(msg,ctx)
        giveInstructions("Push and Place",ctx.storage.get("difficulty"))
    await ctx.send(game_master.address,SetParams(game_type=ctx.storage.get("game_type"), difficulty=ctx.storage.get("difficulty")))
    
def setDifficulty(data,ctx):
    match data.severity:
        case 0:
            ctx.storage.set("difficulty", 2)
            data_to_unity["difficulty"] = 2
        case 1:
            ctx.storage.set("difficulty", 1)
            data_to_unity["difficulty"] = 1
        case 2:
            ctx.storage.set("difficulty", 0)
            data_to_unity["difficulty"] = 0
'''
@protocol.on_message(model=EndGame)

async def generate_report(results: FinalResults):
    # Initialize PDF with the needed fonts, margins, and automatic page breaks
    pdf = PDF('NotoSans-VariableFont_wdth,wght.ttf', 'NotoSansTC-VariableFont_wght.ttf') # Set any font file

    pdf.add_font('Noto Sans TC', '', 'NotoSansTC-VariableFont_wght.ttf')
    pdf.add_font('Noto Sans TC', 'B', 'NotoSansTC-VariableFont_wght.ttf')
    pdf.add_font('Noto Sans TC', 'I', 'NotoSansTC-VariableFont_wght.ttf')
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_auto_page_break(auto=True, margin=15)
    lines_per_page = 20
    current_line = 0
    for i, res in enumerate(results): # Loop over the questions and answers
        # Create a new page if needed and reset the question count
        if current_line >= lines_per_page or i == 0:
            pdf.add_page()
            current_line = 0
        match i:
            case 0:
                plt.plot(results.game1Results)
                plt.savefig(f"game1_results.png")
                pdf.add_text("Average results for game 1: "+str(sum(results.game1Results)/len(results.game1Results)),"game1_results.png")  
      
            case 1:
                plt.plot(results.game2Results)
                plt.savefig(f"game2_results.png")
                pdf.add_text("Average results for game 2: "+str(sum(results.game2Results)/len(results.game2Results)),"game2_results.png")  
            
            case 2:
                plt.plot(results.game3Results)
                plt.savefig(f"game3_results.png")
                pdf.add_text("Average results for game 3: "+str(sum(results.game3Results)/len(results.game3Results)),"game3_results.png")  
        current_line += 1  # Increment the number of questions on the page

    # Save the PDF to a file
    pdf_file_path= 'FinalReport.pdf'  # Set the output file path and name of the generated PDF

    pdf.output(pdf_file_path)  # Output the file to the specified filepath
    print("Final report saved at:", pdf_file_path) # Let the user know where the file was saved

'''

@placeholder.on_interval(5)
async def speak(ctx:Context):
    Purpose = """
    Let the user know how they are doing and respond to anything they've said. 
    Be very, very careful with your words, users may have trauma, PTSD, etc since they have all expericned a stroke.

    If the user is doing very good give encouraging words like "way to go," "amazing," etc. Say we will now try a harder level.

    If the user is doing very badly, give encouraging words like "this is ok" let's try something else, I know you can do it, etc. 
    """
    
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
    if ctx.storage.get("time_remaining") != 0:
        ratio = (ctx.storage.get("winning_score")-ctx.storage.get("last_score")/ctx.storage.get("time_remaining"))
    else:
        ratio = 0
    soap = '''What is a SOAP note?
    A SOAP note is a form of written documentation many healthcare professions use to record a patient or client interaction. Because SOAP notes are employed by a broad range of fields with different patient/client care objectives, their ideal format can differ substantially between fields, workplaces, and even within departments. However, all SOAP notes should include Subjective, Objective, Assessment, and Plan sections, hence the acronym SOAP. A SOAP note should convey information from a session that the writer feels is relevant for other healthcare professionals to provide appropriate treatment. The audience of SOAP notes generally consists of other healthcare providers both within the writer’s own field as well in related fields but can also include readers such as those associated with insurance companies and litigation. A good SOAP note should result in improved quality of patient care by helping healthcare professionals better document and therefore recall and apply details about a specific case.

    How long is a SOAP note and how do I style one?
    The length and style of a SOAP note will vary depending on one’s field, individual workplace, and job requirements. SOAP notes can be written in full sentence paragraph form or as an organized list of sentences fragments. Note the difference in style and format in the following two examples. The first come from within a hospital context. The second is an example from a mental health counseling setting.
    '''
    current_info = """
    The user's current score is {0}, and the time remaining is {1} seconds.
    The user must score at least {2} points, or an average of {3} points per second, to win.
    """.format(ctx.storage.get("last_score"), ctx.storage.get("time_remaining"), ctx.storage.get("winning_score")-ctx.storage.get("last_score"), ratio)        
    user_input = "The user just said the following: " + ctx.storage.get("text_output") 
    try:
        if(ctx.storage.get("text_output") == ctx.storage.get("prev_text_output") ):
            return
    except:
        pass
        # Combine the user input with the game context and purpose
    if ctx.storage.get("game_type")=="Forearm Flexors":
        full_prompt = Purpose + '\n\n'+ Game1 + '\n\n'+ current_info +'\n\n' + user_input + '\n\n' + "Try to keep it around two sentences."
    else:
        full_prompt = Purpose +'\n\n'+ Game2 +'\n\n'+ current_info + '\n\n'+user_input + '\n\n' + "Try to keep it around two sentences."
    # user_input comes from unity
    ctx.storage.set("prev_text_output",full_prompt)
    response = model.generate_content(full_prompt)
    ref = db.reference('/llm')
    def analyze_user_input(user_input):
        return "\n"+ model.generate_content("Did the patient talk how the patient is feeling, their description of pain or discomfort, their level of daily activities, and their perception of progress. It often includes patient's personal opinions and feelings about their condition. If yes for any of them. ONLY OUTPUT THESE IN A LIST. Write it in third person like start with 'the patient.'" + user_input).text
    
    ref.update({"text":response.text})
    ctx.storage.set("text_output",response.text)
    subjective =  analyze_user_input(user_input)
    subjective = model.generate_content("Use the SOAP model to write the subjective part of the evaluation.\n\n" + soap + "\n\n"+subjective ).text
    objective = model.generate_content("Use the SOAP model to write the Objective part of the evaluation: " + soap +'\n\n' + Game1+"\n\n"+Game2 + "\n\nEvent log:\n\n"+ctx.storage.get("event_log") + "\n\nUSE DATA FROM THE LOG AND YOUR UNDERSTADING OF THE GAME TO WRITE ONLY Objective. Only talk about metrics that are mentioned in the log. Say how many games were played. how much time was used. what level the game was played at") .text
   
    ctx.logger.info("Notes on subjective behavior:\n\n" + subjective)
    ctx.logger.info("\n\nNotes on objective behavior:\n\n" + objective)



def giveInstructions(game,task="Intro",current_score=0,time_remaining=0,seconds_per_score=0, remaining_points=0,ctx=None): # Tell Gemini 

    model = genai.GenerativeModel('gemini-pro')

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



    if time_remaining > 0:
                score_remaining_per_sec = remaining_points/time_remaining
    else:
        score_remaining_per_sec = 0
    current_info = """
    The user's current score is {0}, and the time remaining is {1} seconds.
    It has taken the user an average of {2} seconds to score each point, and the user must score at least {3} points, or an average of {4} points per second, to win.
    """.format(current_score, time_remaining, seconds_per_score, remaining_points, score_remaining_per_sec)

    if task == "Bad":
        if time_remaining == 0:
            Purpose =''' 
            The user is doing badly, and the time remaining for this game has run out. 
            Let the user know that the difficulty has been decreased for the next round. 
            Give encouraging words like "this is ok," "let's try something else," "I know you can do it," etc. 
            Be very, very careful with your words, users may have trauma, PTSD, etc since they have all experienced a stroke.
            '''
        else:
            Purpose =''' 
            The user is doing badly, and the time remaining for this game has run out. 
            Let the user know that the difficulty has been decreased for the next round. 
            Give encouraging words like "this is ok," "let's try something else," "I know you can do it," etc. 
            Be very, very careful with your words, users may have trauma, PTSD, etc since they have all experienced a stroke.
            '''
    elif task == "Good":
            Purpose =''' 
            The user is doing well, so the difficulty has been increased for the next round. Let the user know, and give congratulating words like "Good job!," "Great work!," "Keep it up!," etc. 
            '''
    elif task == "Win":
        Purpose =''' 
            The user is doing great! Give congratulating words like "Good job!," "Great work!," "Keep it up!," etc. 
            '''
        current_info = """
        The user's final score is {0}.
        It has taken the user an average of {1} seconds to score each point.
        """.format(current_score, seconds_per_score )

    elif task == "Lose":
        Purpose = ''' 
            The user is stuck on level 0 (the lowest one). Give encouraging words like "this is ok," "let's try something else," "I know you can do it," etc. Be very, very careful with your words, users may have trauma, PTSD, etc since they have all experienced a stroke.
        '''
        current_info = """
        The user's final score is {0}, and it has taken the user an average of {1} seconds to score each point.
        The user had to score at least {2} points, or an average of {3} points per second, to win.
        """.format(current_score, seconds_per_score, remaining_points, score_remaining_per_sec)
        

    else:
        current_info =""
        Purpose =''' 
        You are a bot that speaks in a VR for a post-stroke therapy game. Be very encouraging and kind. The philospophy of our training is to use Repetitive Task Training (RTT) which helps Relearning Lost Skills, Progressively improving on the same tasks , and Neuromuscular Rehabilitation (NMRE) - reinforcing new neural connections and promoting muscle memory. 
        Be very very careful with your words, users may have trauma, PTSD, etc since they have all experienced a stroke.

        If the user is doing very good give encouraging words like "way to go," "amazing," etc. Say we will now try a harder level.

        If the user is doing very badly, give encouraging words like "this is ok" let's try something else, I know you can do it, etc. 
        '''
  
    # Combine the user input with the game context and purpose
    if game=="Forearm Flexors":
        full_prompt = Purpose + '\n\n'+ Game1 + '\n\n'+ current_info
    elif game ==2:
        full_prompt = Purpose +'\n\n'+ Game2 +'\n\n'+ current_info
    # user_input comes from unity
    response = model.generate_content(full_prompt)
    ref = db.reference('/llm')
    ref.update({"text":response.text})

@placeholder.on_interval(period=1)
async def get_unity_data(ctx:Context):
    ref = db.reference('/output')
    print(ref.get())
    ctx.storage.set("text_output",str(ref.get()["speech_text"]))
    ref = db.reference('/api')
    sendDict = {
        "game_type": "Forearm Flexors",
        "difficulty": ctx.storage.get("difficulty"),
        "time_remaining": ctx.storage.get("time_remaining"),
        "secsSinceLastScore": ctx.storage.get("secsSinceLastScore"),
        "last_score": ctx.storage.get("last_score"),
        "winning_score": ctx.storage.get("winning_score"),
        "highlighted_muscles": ctx.storage.get("highlighted_muscles"),
        "num_plants": ctx.storage.get("num_plants"),
        "distance": ctx.storage.get("distance"),
        "size": ctx.storage.get("size"),
        "handedness": ctx.storage.get("handedness"),
        "max_time": ctx.storage.get("time")
}
    ctx.storage.set("game_type", "Forearm Flexors")
    ref.update(sendDict)
   



def setMuscles(ctx,highlighted_muscles):
    new_muscles = {}
    for muscle in list(ctx.storage.get(highlighted_muscles).keys()):
        if muscle in highlighted_muscles:
            new_muscles[muscle] = True
        else:
            new_muscles[muscle] = False
    return highlighted_muscles

placeholder.include(protocol)
game_master.include(game_protocol)

from uagents.setup import fund_agent_if_low
 
user = Agent(
    name="user",
    port=8000,
    seed="user secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"],
)


game_query = PatientData(
    name="Brandon",
    issues=["Flexor carpi radialis"," Flexor carpi ulnaris", "Flexor digitorum superficialis"],
    severity=1
)
 
# This on_interval agent function performs a request on a defined period
@user.on_interval(period=3.0)
async def interval(ctx: Context):
         await ctx.send(placeholder.address, game_query)
 
 
 
if __name__ == '__main__':
    bureau = Bureau()
    bureau.add(user)
    bureau.add(placeholder)
    bureau.add(game_master)
    bureau.run()
   