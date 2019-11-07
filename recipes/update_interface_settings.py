import getpass
from tqdm import tqdm
import json

from kili.authentication import authenticate
from kili.mutations.tool import update_tool
from kili.queries.tool import get_tools


email = input('Enter email: ')
password = getpass.getpass()
project_id = input('Enter project id: ')


with open('./conf/new_interface_settings.json', 'r') as f:
    interface_settings = json.load(f)


client, user_id = authenticate(email, password)

tools = get_tools(client, project_id)

assert len(tools) == 1
tool_id = tools[0]['id']
name = tools[0]['name']
tool_type = tools[0]['toolType']

update_tool(client,
            tool_id, project_id, name, tool_type,
            json_settings=interface_settings)
