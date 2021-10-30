from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount, CardAction, ActionTypes, SuggestedActions
import re
import time
from datetime import datetime

from botbuilder.core import ActivityHandler, ConversationState, TurnContext, UserState
from botbuilder.schema import ChannelAccount
from conversation_data import ConversationData
from user_profile import UserProfile


class MyBot(ActivityHandler):
 """
 This bot will respond to the user's input with suggested actions.
 Suggested actions enable your bot to present buttons that the user
 can tap to provide input.
 """

 def __init__(self, conversation_state: ConversationState, user_state: UserState):
 if conversation_state is None:
 raise TypeError(
 "[MyBot]: Missing parameter. conversation_state is required but None was given"
 )
 if user_state is None:
 raise TypeError(
 "[MyBot]: Missing parameter. user_state is required but None was given"
 )

 self.conversation_state = conversation_state
 self.user_state = user_state
 self.conversation_data_accessor = self.conversation_state.create_property(
 "ConversationData"
 )
 self.user_profile_accessor = self.user_state.create_property("UserProfile")

 async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
 """
 Send a welcome message to the user and tell them what actions they may perform to use this bot
 """
 for member in turn_context.activity.members_added:
 if member.id != turn_context.activity.recipient.id:
 await turn_context.send_activity(
 MessageFactory.text(
 f"Hi, I am Defectron. What can I help you with?"
 )
 )
 await self._send_suggested_actions(turn_context)
 # Get the state properties from the turn context.

 async def on_turn(self, turn_context: TurnContext):
 await super().on_turn(turn_context)

 await self.conversation_state.save_changes(turn_context)
 await self.user_state.save_changes(turn_context)

 async def on_message_activity(self, turn_context: TurnContext):
 """
 Respond to the users choice and display the suggested actions again.
 """

 if (turn_context.activity.text == ('1.Authorisation_Issue')):
 user_profile = await self.user_profile_accessor.get(turn_context, UserProfile)
 conversation_data = await self.conversation_data_accessor.get(
 turn_context, ConversationData
 )

 if user_profile.name is None:
 # First time around this is undefined, so we will prompt user for name.
 if conversation_data.prompted_for_user_name:
 # Set the name to what the user provided.
 user_profile.name = turn_context.activity.text

 # Acknowledge that we got their name.
 await turn_context.send_activity(
 f"Thanks USER ID {user_profile.name}. To see conversation data, type anything."
 )

 # Reset the flag to allow the bot to go though the cycle again.
 conversation_data.prompted_for_user_name = False
 else:
 # Prompt the user for their name.
 await turn_context.send_activity("What is your USER ID?")

 # Set the flag to true, so we don't prompt in the next turn.
 conversation_data.prompted_for_user_name = True
 else:
 # Add message details to the conversation data.
 conversation_data.timestamp = self.__datetime_from_utc_to_local(
 turn_context.activity.timestamp
 )
 conversation_data.channel_id = turn_context.activity.channel_id

 # Display state data.
 await turn_context.send_activity(
 f"{user_profile.name} sent: {turn_context.activity.text}"
 )
 await turn_context.send_activity(
 f"Message received at: {conversation_data.timestamp}"
 )
 await turn_context.send_activity(
 f"Message received from: {conversation_data.channel_id}"
 )

 async def _send_suggested_actions(self, turn_context: TurnContext):
 """
 Creates and sends an activity with suggested actions to the user. When the user
 clicks one of the buttons the text value from the "CardAction" will be displayed
 in the channel just as if the user entered the text. There are multiple
 "ActionTypes" that may be used for different situations.
 """

 reply = MessageFactory.text("What can I help you with?")

 reply.suggested_actions = SuggestedActions(
 actions=[
 CardAction(
 title="1.Authorisation_Issue",
 type=ActionTypes.im_back,
 value="1.Authorisation_Issue",
 ),
 CardAction(
 title="2.Data_Missing",
 type=ActionTypes.im_back,
 value="2.Data_Missing",
 ),
 CardAction(
 title="3.SOP_Documentation",
 type=ActionTypes.im_back,
 value="3.SOP_Documentation",
 ),
 CardAction(
 title="4.Others",
 type=ActionTypes.im_back,
 value="4.Others",
 ),
 ]
 )
 await turn_context.send_activity(reply)

 def __datetime_from_utc_to_local(self, utc_datetime):
 now_timestamp = time.time()
 offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
 now_timestamp
 )
 result = utc_datetime + offset
 return result.strftime("%I:%M:%S %p, %A, %B %d of %Y")