from CybORG.Emulator.Actions.RestoreAction import RestoreAction


redeploy_host_action = RestoreAction(
    hostname='testmachine-v',
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name='mvp1',
    username='ninehs',
    password='hdN1n5t1tut3$',
    user_domain_name='ISIS',
    project_domain_name='ISIS'
)

redeploy_host_action.execute(None)
