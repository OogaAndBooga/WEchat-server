import asyncio
import json
import websockets, websockets.exceptions as excuses

###  The current names are usernames

people = {'teofil' : 'teofil', 'luca' : 'luca'}
current_users = {}
groups = {
    'grupa-lui-teo' : {'members' : ['teofil', 'luca'], 'messages' : []}, 
    'grupa-lui-luca' : {'members' : ['teofil', 'luca'], 'messages' : []}
}

async def do_stuff(websocket, path):
    print('som body connecttttttttttttttt')
    msg = await websocket.recv()
    print(json.loads(msg))
    username = json.loads(msg)['username']
    password = json.loads(msg)['password']
    while not(username in people and password == people[username]):
        await websocket.send(json.dumps({'password_correct' : False}))
        msg = await websocket.recv()
        print(json.loads(msg))
        username = json.loads(msg)['username']
        password = json.loads(msg)['password']

    mygroups = []
    for group in groups:
        if username in groups[group]['members']:
            mygroups.append({'group_name': group, 'members' : groups[group]['members']})

    try:
        msg = {'password_correct': True, 'groups' : mygroups}
        await websocket.send(json.dumps(msg))

        mygroups = []
        for group in groups:
            if username in groups[group]['members']:
                mygroups.append({group : []}) #the empty list is for messages
        current_users[username] = {'websocket' : websocket, 'requested_groups' : [], 'messages_already_sent' : mygroups}

        print('{} connected yaaaaaaaaaaaaaaaaaaaaaaaaaaay'.format(username))
        print('fisst message :') #;libqaelji   EV;OHI  WEFIO;HOIJQWER['OIJ'    E   WGV['OIJ    WGEGV3O;NWDVpoihnvW;ON'WVD'nkWV/LKN]]
        print(msg)
        while True:
            msg = await websocket.recv()
            msg = json.loads(msg)
            action = msg['action']
            if action == 'message':
                print('received {} from {}'.format(msg, username))
                msg['sender'] = username
                recipient = msg['recipient']
                del msg['recipient']
            
                if recipient in groups:
                    groups[recipient]['messages'].append(msg)
                    print('added message {} to group {}'.format(msg, recipient))
                    print(groups[recipient]['messages'])
                    msg = json.dumps(msg)

                    for user in groups[recipient]['members']:
                        if user in current_users and user != username:
                            if recipient not in current_users[user]['requested_groups']:
                                current_users[user]['messages_already_sent'][recipient].append(msg) #add messages not to send when requesting messages
                                print('{} has not requested {}'.format(username, recipient))
                            await current_users[user]['websocket'].send(msg)
                            print('sent {} {}'.format(user, msg))
            elif action == 'request_messages':
                requested_group = msg['group']
                print('{} requested messages from {}, {}'.format(username, requested_group, groups[requested_group]))
                print('{} has requested groups : {}'.format(username, current_users[username]['requested_groups']))
                if requested_group not in current_users[username]['requested_groups']:
                    if username in groups[requested_group]['members']:
                        msg = {'messages' : list(groups[requested_group]['messages'])}
                        for i in range(len(msg['messages'])):
                            if msg['messages'][i]['sender'] == username:
                                msg['messages'][i]['sender'] = 'me' #pt luca
                        if msg['messages'] != []:
                            await websocket.send(json.dumps(msg))
                            print('sent {} : {}'.format(username, msg))
                            current_users[username]['requested_groups'].append(requested_group)
            elif action == 'create_group':
                print('{} created group {}'.format(username, msg['group']))
                if msg['group'] not in groups:
                    groups[msg['group']] = {'members' : [list(people.keys())], 'messages' : []}
                else:
                    print('group {} already exists'.format(msg['group']))
    except (excuses.ConnectionClosed, excuses.ConnectionClosedError, excuses.ConnectionClosedOK):
        del current_users[username]
        print('deleted {}'.format(username))#remove user from current users

def serve(port):
    start_server = websockets.serve(do_stuff, '0.0.0.0', port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    [{'time': '1616415017', 'message': 'salut primul mesaj', 'message_type': 'message', 'sender': 'luca'}, {'time': '1616415023', 'message': 'salut al doilea mesaj', 'message_type': 'message', 'sender': 'luca'}]