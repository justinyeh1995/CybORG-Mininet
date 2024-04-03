from CybORG.Emulator.Actions.SshAction import SshAction


if __name__ == "__main__":
    
    sshAction = SshAction("172.17.0.2", "velociraptor", "velociraptor", 22)
    #sshAction = SshAction("172.17.0.3", "sftp_user", "art54")
    
    observation = sshAction.execute(None)

    print(observation)
    
    print("foo")