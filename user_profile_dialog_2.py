import requests
from requests.auth import HTTPBasicAuth
import json
import pymsteams
from botbuilder.core import MessageFactory, UserState
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
from botbuilder.dialogs.choices import Choice, FoundChoice

from dialogs.BoxConnect import box_upload


class UserProfileDialog2(ComponentDialog):
 def __init__(self, user_state: UserState):
 super(UserProfileDialog2, self).__init__(UserProfileDialog2.__name__)

 self.add_dialog(
 WaterfallDialog(
 WaterfallDialog.__name__,
 [
 self.user_id_step,
 self.user_id_confirm_step,
 self.sys_det_step,
 self.tran_code_step,
 self.tran_code_confirm_step,
 ],
 )
 )
 self.add_dialog(TextPrompt(TextPrompt.__name__))
 self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
 self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
 self.initial_dialog_id = WaterfallDialog.__name__

 async def user_id_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

 return await step_context.prompt(
 TextPrompt.__name__,
 PromptOptions(prompt=MessageFactory.text("Please enter your User ID.")),
 )

 async def user_id_confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 step_context.values["user_id"] = step_context.result

 # We can send messages to the user at any point in the WaterfallStep.

 def validate_name(user_input: str):
 return 1

 val = validate_name(str(step_context.result))
 if val == 1:
 await step_context.context.send_activity(MessageFactory.text(f"ID entered {step_context.result}"))
 # WaterfallStep always finishes with the end of the Waterfall or
 # with another dialog; here it is a Prompt Dialog.
 return await step_context.prompt(
 TextPrompt.__name__,
 PromptOptions(prompt=MessageFactory.text("Please enter the SAP Instance")),
 )

 async def sys_det_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 step_context.values["sys_det"] = step_context.result

 def validate_name(user_input: str):
 return 1

 val = validate_name(str(step_context.result))
 if val == 1:
 await step_context.context.send_activity(
 MessageFactory.text(f"Instance entered {step_context.result}")
 )
 else:
 await step_context.context.send_activity(
 MessageFactory.text(f"Invalid User ID or Instance. Please re-enter your details.")
 )
 return await step_context.replace_dialog(
 UserProfileDialog2.__name__
 )
 return await step_context.prompt(
 TextPrompt.__name__,
 PromptOptions(prompt=MessageFactory.text("Please enter the Transaction Code.")),
 )

 async def tran_code_step(
 self, step_context: WaterfallStepContext
 ) -> DialogTurnResult:
 step_context.values["tran_code"] = step_context.result

 # We can send messages to the user at any point in the WaterfallStep.

 def validate_name(user_input: str):
 return 1

 val = validate_name(str(step_context.result))
 if val == 1:
 await step_context.context.send_activity(
 MessageFactory.text(f"Transaction code: {step_context.result}")
 )

 # Get the current profile object from user state. Changes to it
 # will saved during Bot.on_turn.
 user_id = step_context.values["user_id"]
 sys_det = step_context.values["sys_det"]
 tran_code = step_context.values["tran_code"]

 async def _auth_func1(self, user_id: str, sys_det: str, tran_code: str):
 cred = open('instance.json', )
 read_config = cred.read()
 config_det = json.loads(read_config)
 flag = 0
 list1 = [(k, v) for k, v in config_det.items()]
 for i in range(0, len(list1)):

 if sys_det.lower() == str(list1[i][0]).lower():
 flag = 1
 uname = list1[i][1]['Username']
 passw = list1[i][1]['Password']
 uri = list1[i][1]['GET']
 params = list1[i][1]['Params']
 params2 = str(params['$filter']).replace('user_id', user_id)
 params['$filter'] = params2
 # Trigger the GET operation, passing the URI from the file
 myresponse = requests.get(uri, headers=list1[i][1]['Header'], params=params,
 auth=HTTPBasicAuth(uname, passw))
 # For successful API call, response code will be 200 (OK)
 if myresponse.ok:
 payload = myresponse.content
 jsonf = json.loads(payload)
 if not jsonf['d']['results']:
 await step_context.context.send_activity(MessageFactory.text
 (
 f"No errors found in the SAP buffer for the user " + user_id))
 return '111'
 else:
 if (tran_code) in str(jsonf['d']['results']):
 await step_context.context.send_activity(MessageFactory.text
 (
 f"Errors found in the SAP buffer for the transaction " + tran_code))
 return '222'
 elif (tran_code) not in str(jsonf['d']['results']):
 await step_context.context.send_activity(MessageFactory.text
 (
 f"No errors found in the SAP buffer for the transaction " + tran_code))
 return '111'
 else:
 await step_context.context.send_activity(MessageFactory.text
 (
 f"Auth data could not be fetched. Please check the User ID: " + user_id))
 return '111'

 if flag == 0:
 await step_context.context.send_activity(
 MessageFactory.text(f"SAP Instance not maintained! Please check")
 )
 return '444'

 m = await _auth_func1(self, user_id, sys_det, tran_code)
 if m == '111':
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get the initial selection"))
 return await step_context.end_dialog()
 elif m == '222':
 return await step_context.prompt(
 ConfirmPrompt.__name__,
 PromptOptions(
 prompt=MessageFactory.text("Would you like me to send details to the Auth team? Yes/No")
 ),
 )
 elif m == '333':
 return await step_context.replace_dialog(
 UserProfileDialog2.__name__
 )
 elif m == '444':
 return await step_context.replace_dialog(
 UserProfileDialog2.__name__
 )
 else:
 await step_context.context.send_activity(
 MessageFactory.text(f"ERROR")
 )
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get the initial selection"))
 return await step_context.end_dialog()

 async def tran_code_confirm_step(
 self, step_context: WaterfallStepContext
 ) -> DialogTurnResult:

 def _auth_func2():
 user_id = str(step_context.values["user_id"])
 sys_det = str(step_context.values["sys_det"])
 tran_code = str(step_context.values["tran_code"])
 myTeamsMessage = pymsteams.connectorcard(
 "")
 myTeamsMessage.text("Auth request for user " + user_id + " Transaction: "+ tran_code + " System: " + sys_det)
 myTeamsMessage.send()
 return step_context.context.send_activity(
 MessageFactory.text(f"Auth request details have been sent!"))

 if step_context.result:
 await _auth_func2()
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get the initial selection"))
 return await step_context.end_dialog()

 else:
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get the initial selection"))
 return await step_context.end_dialog()


class UserProfileDialog3(ComponentDialog):
 def __init__(self, user_state: UserState):
 super(UserProfileDialog3, self).__init__(UserProfileDialog3.__name__)

 self.add_dialog(
 WaterfallDialog(
 WaterfallDialog.__name__,
 [
 self.system_name_step,
 self.test_name_step,
 self.trigger_test_step,
 ],
 )
 )
 self.add_dialog(TextPrompt(TextPrompt.__name__))
 self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
 self.initial_dialog_id = WaterfallDialog.__name__

 async def system_name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 return await step_context.prompt(
 ChoicePrompt.__name__,
 PromptOptions(
 prompt=MessageFactory.text("Please select the system name for regression test run"),
 choices=[Choice("CUS"), Choice("DEV"), Choice("QAS"), Choice("TRA")],
 ),
 )

 async def test_name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 step_context.values["system_name_step"] = step_context.result.value
 return await step_context.prompt(
 ChoicePrompt.__name__,
 PromptOptions(
 prompt=MessageFactory.text("Please select the regression test run"),
 choices=[Choice("Test1"), Choice("Test2")],
 ),
 )

 async def trigger_test_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 step_context.values["test_name_step"] = step_context.result.value
 test_sys_id = step_context.values["system_name_step"]
 test_name = step_context.values["test_name_step"]
 await step_context.context.send_activity(
 MessageFactory.text(str(test_name)+ " will be triggered in system " + str(test_sys_id)
 + ". The box link with the results will be sent to the teams channel.")
 )

 import os
 os.system('robot -d results Tests\CF\Test1.robot')
 box_upload(test_name)
 await step_context.context.send_activity(
 MessageFactory.text(f'Your session has ended. Type something to get the initial selection.')
 )
 return await step_context.end_dialog()


class UserProfileDialog4(ComponentDialog):
 def __init__(self, user_state: UserState):
 super(UserProfileDialog4, self).__init__(UserProfileDialog4.__name__)

 self.add_dialog(
 WaterfallDialog(
 WaterfallDialog.__name__,
 [
 self.user_api_step,
 self.link_api_step,
 ],
 )
 )

 self.add_dialog(TextPrompt(TextPrompt.__name__))
 self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
 self.initial_dialog_id = WaterfallDialog.__name__

 async def user_api_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 return await step_context.prompt(
 ChoicePrompt.__name__,
 PromptOptions(
 prompt=MessageFactory.text("Please enter the project name"),
 choices=[Choice("PET"), Choice("LIMS")],
 ),
 )

 async def link_api_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
 step_context.values["user_api_step"] = step_context.result.value
 project_api = step_context.result.value
 print(project_api)
 if project_api == 'PET':
 api_payload = "https://box.com"
 else:
 api_payload = "https://box.com"

 await step_context.context.send_activity(
 MessageFactory.text(f"Payload logs for {project_api} can be found at {api_payload}")
 )
 await step_context.context.send_activity(
 MessageFactory.text(f"Your session has ended. Type something to get the initial selection")
 )
 return await step_context.end_dialog()