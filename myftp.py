from ftplibrary import FTP
        
ftp = FTP()
while True:
    line = input('ftp> ').strip()
    args = line.split()
    if line:
        command = args[0]
    else:
        continue
        
    if command == 'quit' or command == 'bye':
        ftp.quit()
        break
    
    elif command == 'pwd':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        ftp.pwd()
        
    elif command == 'ascii':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        ftp.ascii()
        
    elif command == 'binary':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        ftp.binary()
    
    elif command == 'open':
        if len(args) == 1:
            open_site = input('To ')
            if open_site == '':
                print('Usage: open host name [port]')
                continue
        elif len(args) == 2:
            ftp.open(args[1])
        elif len(args) == 3:
            ftp.open(args[1],args[2])
        
    elif command == 'disconnect' or command == 'close':
        ftp.disconnect()
        
    elif command == 'ls':
        if not ftp.isConnect:
            print('Not connected.')
            continue 
        elif len(args) == 1:
            ftp.ls()
        else:
            ftp.ls(args[1])
            
    elif command == 'get':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        elif len(args) == 1:
            remote_file = input('Remote file ')
            if remote_file == '':
                print('Remote file get [ local-file ].')
                continue
            local_file = input('Local file ')
            ftp.get(remote_file,local_file)
        elif len(args) == 2:
            ftp.get(args[1],args[1])
        elif len(args) == 3:
            ftp.get(args[1],args[2])
            
    elif command == 'put':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        elif len(args) == 1:
            local_file = input('Local file ')
            if local_file == '':
                print('Local file put: remote file.')
                continue
            remote_file = input('Remote file ')
            ftp.put(local_file,remote_file)
        elif len(args) == 2:
            ftp.put(args[1],args[1])
        elif len(args) == 3:
            ftp.put(args[1],args[2])
            
    elif command == 'delete':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        elif len(args) == 1:
            remote_file = input('Remote file ')
            if local_file == '':
                print('delete remote file.')
                continue
            ftp.delete(remote_file)
        elif len(args) == 2:
            ftp.delete(args[1])
    
    elif command == 'rename':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        elif len(args) == 1:
            old_name = input('From name ')
            if old_name == '':
                print('rename from-name to-name.')
                continue
            new_name = input('To name ')
            if new_name == '':
                print('rename from-name to-name.')
                continue
            ftp.rename(old_name,new_name)
        elif len(args) == 2:
            new_name = input('To name ')
            if new_name == '':
                print('rename from-name to-name.')
                continue
            ftp.rename(args[1],new_name)
        elif len(args) == 3:
            ftp.rename(args[1],args[2])
            
    elif command == 'user':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        elif len(args) == 1:
            ftp.user()
        elif len(args) == 2:
            ftp.user(args[1])
        elif len(args) == 3:
            ftp.user(args[1],args[2])
    
    elif command == 'cd':
        if not ftp.isConnect:
            print('Not connected.')
            continue
        elif len(args) == 1:
            ftp.cd()
        elif len(args) == 2:
            ftp.cd(args[1])
            
    else:
        print("Invalid command.")