from CybORG.Emulator.Actions.RestoreAction import RestoreAction
import argparse
import keyring

parser = argparse.ArgumentParser()

parser.add_argument("-u", "--user",type=str,default="dummy", help="user name")

args = parser.parse_args()

#DO it via arg parser
user_name=args.user

password = keyring.get_password("openstack", user_name)


restore_action = RestoreAction(
    hostname='Defender',
    auth_url='https://cloud.isislab.vanderbilt.edu:5000/v3',
    project_name='mvp1a',
    username=user_name,
    password=password,
    user_domain_name='ISIS',
    project_domain_name='ISIS'
)

observation=restore_action.execute(None)
print('observation success:',observation.success)

