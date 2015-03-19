import sys
from pprint import pprint
from collections import defaultdict

from pyral import Rally, rallyWorkset
options = [arg for arg in sys.argv[1:] if arg.startswith('--')]
args    = [arg for arg in sys.argv[1:] if arg not in options] 
server, user, password, apikey, workspace, project = rallyWorkset(options)
print 'user=',user,'password=',password
rally = Rally(server, user, password, workspace='Big Data CoE', project=project)
rally.enableLogging('mypyral.log')
ownerDict = defaultdict(list)

def debugObject(obj, thenExit=False):
   l=dir(obj)
   d=obj.__dict__
   pprint (d, indent=2)
   if thenExit:
      sys.exit(0) 

def printStory(story):
  try:
    ownerName='--No Owner--'
    parentID='NoParent'
    featureID='NoFeature'
    if hasattr(story,'Parent') and story.Parent is not None:
      parentID=story.Parent.FormattedID
    if story.Owner is not None:
      ownerName=story.Owner.UserName
    if hasattr(story,'Feature') and story.Feature is not None:
      featureID=story.Feature.FormattedID
    print "{: <36} | {: <10}|".format(story.Project.Name, story.FormattedID),
    print "{: <10}| {: <10}| {: <20}".format(parentID,featureID,ownerName)
#    print story.Parent._type
#    print story._type       
  except:
    print "Caught Exception"
    print story.details()
    raise



# 
# Notes:
#   - There are cases where a US has attribute HasParent=True, but the Parent attribute does not exist.
#     In such cases, the query will return the US in the results
#   - Even though the .details() method will show friendly None if an attribute does not exist, 
#     the query should check for null
def showStoriesInProjectHierarchy(proj,myQuery,level=0):
  if level == 0:
    print "%-36s | %-10s| %-10s| %-10s| %-20s" % ('Project Name', 'Story', 'Parent','Feature','Owner')
    print "-" * 100 
  else: 
    print "--" * level,
  print proj.Name
  response = rally.get('UserStory', fetch=True, project=proj.Name, query=myQuery,projectScopeUp=False,projectScopeDown=False)

  for story in response:
    if story.Owner is not None:
      ownerDict[story.Owner.UserName].append(story)
    printStory(story)      
  for child in proj.Children: 
    showStoriesInProjectHierarchy(rally.getProject(name=child.Name), myQuery, level=level+1)

     

def nofeature():
  proj = rally.getProject(name='Data Platform Theme')
#  print proj.details()
#  myQuery = 'Parent != null'
  myQuery = 'Feature != null'
#  myQuery = 'Feature = null'
#  myQuery = "(Feature.c_BDProductOwner='Shyam Ramamoorthy')"

  print 'Rally Query: %s' % (myQuery)
  showStoriesInProjectHierarchy(proj,myQuery)
  for key in ownerDict:
    print "-" * 100
    for story in ownerDict[key]:
       printStory(story)

if __name__ == '__main__':
    nofeature()

