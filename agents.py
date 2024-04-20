from uagents import Agent, Context, Model
from matplotlib import pyplot as plt
from fpdf import FPDF
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from dotenv import load_dotenv
import os
import random as rand
load_dotenv() 

DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

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


class FinalResults(Model):
    game1Results: list[int]
    game2Results: list[int]
    game3Results: list[int]
    
class PatientData(Model):
    name: str
    issues: list[str]
    severity: int

class FFTask(Model):
    difficulty: int
    num_plants:int
    distance: list[list[int],int,list[int]]
    size:int
    handedness: str

class BBTask(Model):
    difficulty: int
    timer_per_revolution: int
    revs_remaining:int

class PPTask(Model):
    difficulty: int
    arrangement: list[list[str]] # Use "in{x}" for inserting book number x and "out{x}" for removing book number x or "N" for neither
    grid_size:int
    
    
placeholder = Agent(name="placeholder", seed="task_man recovery phrase")
 
# Fetch the service account key JSON file contents
cred = credentials.Certificate('serviceAccountKey.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': DATABASE_URL
})


# Define an async function to get 'last_score' from Firebase every second
@placeholder.on_interval(seconds=1)
async def get_score(ctx:Context):
        # Get a database reference to our posts
        ref = db.reference('last_score')
        # Read the data at the posts reference (this is a blocking operation)
        last_score = ref.get()
        if last_score > ctx.storage.get("last_score"):
            ctx.storage.set("last_score", last_score)
            ctx.storage.set("secsSinceLastScore", 0)
            generate_challenge(ctx)
        elif ctx.storage.get("secsSinceLastScore") > 20 and ctx.storage.get("difficulty") > 1:
            ctx.storage.set("difficulty", ctx.storage.get("difficulty") - 1)  
            
            ctx.storage.set("secsSinceLastScore", 0)
            
@placeholder.on_message()
async def generate_challenge(ctx,sender):
    match ctx.storage.get("game_type"):
        case "Forearm Flexors":
            match ctx.storage.get("difficulty"):
                case 1:
                    ctx.send(sender,FFTask(difficulty=1,num_plants=10,distance=[[1,3],1,[1,3]],size=7,handedness=ctx.storage.get("handedness")))
                case 2:
                    ctx.send(sender,FFTask(difficulty=2,num_plants=15,distance=[[2,4],1,[2,4]],size=5,handedness=ctx.storage.get("handedness")))
                case 3:
                    ctx.send(sender,FFTask(difficulty=3,num_plants=20,distance=[[3,5],1,[3,5]],size=3,handedness=ctx.storage.get("handedness")))
        case "Bicep Builder":
            match ctx.storage.get("difficulty"):
                case 1:
                    ctx.send(sender,BBTask(difficulty=1,timer_per_revolution=10,revs_remaining=3))
                case 2:
                    ctx.send(sender,BBTask(difficulty=2,timer_per_revolution=8,revs_remaining=6))
                case 3:
                    ctx.send(sender,BBTask(difficulty=3,timer_per_revolution=6,revs_remaining=9))
        case "Push and Place":
            match ctx.storage.get("difficulty"):
                case 1:
                    books = getBooks(3,4)
                    ctx.send(sender,PPTask(difficulty=1,arrangement=books,grid_size=3))
                case 2:
                    books=getBooks(5,7)
                    ctx.send(sender,PPTask(difficulty=2,arrangement=books,grid_size=5))
                case 3:
                    books=getBooks(7,10)
                    ctx.send(sender,PPTask(difficulty=3,arrangement=books,grid_size=7))
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
@placeholder.on_message()
async def start(ctx: Context):
    ctx.logger.info(f'Hello, my name is {ctx.name}, and I will be your guide through physical therapy today')
    
@placeholder.on_interval(seconds=10)
async def setDifficulty(ctx: Context):
    ctx.storage.set("difficulty", ctx.storage.get("secsSinceLastScore")//10)

@placeholder.on_message(model=PatientData)
async def create_game(ctx: Context, sender: str, data: PatientData):
    ctx.logger.info(f'creating game for {data.name}')
    ctx.storage.set("secsSinceLastScore", 0)
    ctx.storage.set("handedness","R")
    if any(issue in data.issues for issue in ["Flexor carpi radialis"," Flexor carpi ulnaris", "Flexor digitorum superficialis"]):
        ctx.storage.set("highlighted_muscles", setMuscles(ctx,["Flexor carpi radialis"," Flexor carpi ulnaris", "Flexor digitorum superficialis"]))
        ctx.storage.set("game_type", "Forearm Flexors")
        if ctx.storage.get("playedAlready") is None:
            ctx.storage.set("handedness","R")
            ctx.storage.set("playedAlready",True)
        else:
            ctx.storage.set("handedness","L")
            ctx.storage.get("playedAlready",None)
        match data.severity:
            case 1:
                ctx.storage.set("difficulty", 3)
            case 2:
                ctx.storage.set("difficulty", 2)
            case 3:
                ctx.storage.set("difficulty", 1)
        giveInstructions("Forearm Flexors",ctx.storage.get("difficulty"),ctx.storage.get("handedness"))
    elif "Biceps Brachii" in data.issues:
        ctx.storage.set("highlighted_muscles", setMuscles(ctx,["Biceps Brachii"]))
        ctx.storage.set("game_type", "Bicep Builder")
        match data.severity:
            case 1:
                ctx.storage.set("difficulty", 3)
            case 2:
                ctx.storage.set("difficulty", 2)
            case 3:
                ctx.storage.set("difficulty", 1)
        giveInstructions("Bicep Builder",ctx.storage.get("difficulty"))
    elif "Triceps Brachii" in data.issues:
        ctx.storage.set("highlighted_muscles", setMuscles(ctx,["Triceps Brachii"]))
        ctx.storage.set("game_type", "Push and Place")
        match data.severity:
            case 1:
                ctx.storage.set("difficulty", 3)
            case 2:
                ctx.storage.set("difficulty", 2)
            case 3:
                ctx.storage.set("difficulty", 1)
        giveInstructions("Push and Place",ctx.storage.get("difficulty"))
    generate_challenge(ctx,sender)
        
@placeholder.on_message(model=FinalResults)
async def generate_report(ctx: Context, results: FinalResults):
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

def giveInstructions(task,difficulty,handedness=None): # Tell Gemini 
    match task:
        case "Extensor Escape":
            pass
        case "Precision Pinch":
            pass
    #instructions = AudioSegment.from_wav("sound.wav")
    #play(...)
    
def setMuscles(ctx,highlighted_muscles):
    new_muscles = {}
    for muscle in list(ctx.storage.get(highlighted_muscles).keys()):
        if muscle in highlighted_muscles:
            new_muscles[muscle] = True
        else:
            new_muscles[muscle] = False
    return highlighted_muscles
if __name__ == "__main__":
    placeholder.run()