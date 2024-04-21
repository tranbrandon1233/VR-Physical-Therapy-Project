from agents import  PatientData, FFTask, BBTask, PPTask, GameRequest, ItemRequest, EndGame, SetParams
    
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from dotenv import load_dotenv
import os

load_dotenv()
 
AGENT_ADDRESS = os.getenv("AGENT_ADDRESS")
 
user = Agent(
    name="user",
    port=8000,
    seed="user secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"],
)
 
fund_agent_if_low(user.wallet.address())
 
table_query = PatientData(
    name="Brandon",
    issues=["Biceps Brachii"],
    severity=2
)
 
# This on_interval agent function performs a request on a defined period
@user.on_interval(period=3.0)
async def interval(ctx: Context):
         print(ctx.storage)
 
 
@user.on_message(BookTableResponse, replies=set())
async def handle_book_response(ctx: Context, _sender: str, msg: BookTableResponse):
    if msg.success:
        ctx.logger.info("Table reservation was successful")
 
    else:
        ctx.logger.info("Table reservation was UNSUCCESSFUL")
 
    ctx.storage.set("completed", True)
 
if __name__ == "__main__":
    user.run()