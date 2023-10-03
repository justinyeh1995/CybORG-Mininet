@author: Harsh Vardhan ( Vanderbilt University) 


How to add a new action in CybORG environment: 
 1. Create a desired action by defining a action class similar to other actions ( it must inherots from base 'Action' class and should have execute method that returns observation) 
 2. Register it to main intilaization file (__init__.py) of action folder and environment file (env.py)
 3. Also register to local initialization file.   