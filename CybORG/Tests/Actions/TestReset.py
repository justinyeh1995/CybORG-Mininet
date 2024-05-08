from CybORG.Emulator.Actions.RestoreAction import RestoreAction


restore_action = RestoreAction(
    hostname='testmachine',
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name='castle',
    username='vardhah',
    password='*****',
    user_domain_name='ISIS',
    project_domain_name='ISIS'
)

restore_action.execute(None)
