# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import List

from botbuilder.dialogs import (
 WaterfallDialog,
 WaterfallStepContext,
 DialogTurnResult,
 ComponentDialog,
)
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions
from botbuilder.dialogs.choices import Choice, FoundChoice
from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
 ComponentDialog,
 WaterfallDialog,
 WaterfallStepContext,
 DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
 TextPrompt,
 ConfirmPrompt,
 ChoicePrompt,
 PromptOptions,
)
from dialogs.user_profile_dialog_2 import UserProfileDialog2
from dialogs.user_profile_dialog_2 import UserProfileDialog4
from dialogs.user_profile_dialog_2 import UserProfileDialog3

from botbuilder.schema import CardAction, ActionTypes, SuggestedActions
from botbuilder.core import (
 UserState,
 MessageFactory,
 ActivityHandler,
 TurnContext)

class UserProfileDialog(ComponentDialog):
 def __init__(self, user_state: UserState):
 super(UserProfileDialog, self).__init__(UserProfileDialog.__name__)

 self.user_profile_accessor = user_state.create_property("UserProfile")

 self.add_dialog(
 WaterfallDialog(
 WaterfallDialog.__name__,
 [
 self.user_name_step,
 self.user_choice_step,
 self.user_choice_confirm_step
 ],
 )
 )
 self.EXIT_OPTION = "exit"
 self.add_dialog(UserProfileDialog2(UserProfileDialog2.__name__))
 self.add_dialog(UserProfileDialog3(UserProfileDialog3.__name__))
 self.add_dialog(UserProfileDialog4(UserProfileDialog4.__name__))
 self.add_dialog(TextPrompt(TextPrompt.__name__))
 self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
 self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
 self.initial_dialog_id = WaterfallDialog.__name__

 async def user_name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 return await step_context.prompt(
 TextPrompt.__name__,
 PromptOptions(prompt=MessageFactory.text("What is your name?")),
 )
 async def user_choice_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 step_context.values["user_name"] = step_context.result
 return await step_context.prompt(
 ChoicePrompt.__name__,
 PromptOptions(
 prompt=MessageFactory.text("Hi "+str(step_context.result)+ "! What would you like me to help you with?"),
 choices=[Choice("Authorisation Issue"), Choice("Regression Test"), Choice("API Logs"), Choice("Others"), Choice("Exit")],
 ),
 )

 async def user_choice_confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

 step_context.values["user_choice"] = step_context.result.value
 if step_context.result.value == 'Authorisation Issue':
 return await step_context.begin_dialog(UserProfileDialog2.__name__)
 if step_context.result.value == 'Regression Test':
 return await step_context.begin_dialog(UserProfileDialog3.__name__)
 if step_context.result.value == 'API Logs':
 return await step_context.begin_dialog(UserProfileDialog4.__name__)
 if step_context.result.value == 'Others':
 await step_context.context.send_activity(
 MessageFactory.text(f"For any other queries/assistance, please contact ")
 )
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get to the initial selection")
 )
 return await step_context.end_dialog()
 if step_context.result.value == 'Exit':
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get to the initial selection"))
 return await step_context.end_dialog()
 else:
 await step_context.context.send_activity(
 MessageFactory.text(
 f"Sorry I don't know that yet. Please choose from the listed options.")
 )
 return await step_context.replace_dialog(UserProfileDialog.__name__)