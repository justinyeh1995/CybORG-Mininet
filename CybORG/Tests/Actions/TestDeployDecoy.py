from CybORG.Emulator.Actions.DeployDecoyAction import DeployDecoy

deploy_decoy = DeployDecoy('172.17.0.2', 'ubuntu', 'ubuntu', 'Tomcat', 443)

observation = deploy_decoy.execute(None)

print(observation)
print("foo")