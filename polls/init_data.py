from solutioner.users.models import Source
from solutioner.users.models import License
from solutioner.categories.models import Category
from solutioner.rbac.models import RBACRole, RBACOperation

def init_data():
  if not License.objects.all():
    License.objects.create(license='cc-wiki', license_url='http://creativecommons.org/licenses/by-sa/3.0/')
  
  if not Source.objects.all():
    licenses_list = License.objects.get(id=1)
    Source.objects.create(source='solutioner.net', url='http://solutioner.net', image='/media/images/logo.png', description='A sharing system for final solution / search engin...', viewed=0, is_deleted=0)
    source = Source.objects.create(source='stackoverflow.com', url='http://stackoverflow.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
    source = Source.objects.create(source='askubuntu.com', url='http://askubuntu.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
    source = Source.objects.create(source='serverfault.com', url='http://serverfault.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
    source = Source.objects.create(source='superuser.com', url='http://superuser.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
    source = Source.objects.create(source='programmers.stackexchange.com', url='http://programmers.stackexchange.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
    source = Source.objects.create(source='math.stackexchange.com', url='http://math.stackexchange.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
    source = Source.objects.create(source='gaming.stackexchange.com', url='http://gaming.stackexchange.com', image='http://cdn.sstatic.net/stackoverflow/img/apple-touch-icon.png', description='A Q&A system', viewed=0, is_deleted=0)
    source.licenses.add(licenses_list)
    
  if not Category.objects.all():
    Category.objects.create(name= 'Uncategorized' , related_to='0')
    Category.objects.create(name=	'Art/Entertainment'	, related_to='0')
    Category.objects.create(name=	'Business'	, related_to='0')
    Category.objects.create(name=	'Computer'	, related_to='0')
    Category.objects.create(name=	'Culture'	, related_to='0')
    Category.objects.create(name=	'Dance'	, related_to='0')
    Category.objects.create(name=	'Economics'	, related_to='0')
    Category.objects.create(name=	'Education'	, related_to='0')
    Category.objects.create(name=	'Engineering'	, related_to='0')
    Category.objects.create(name=	'Farming/Agriculture'	, related_to='0')
    Category.objects.create(name=	'Food/Cooking'	, related_to='0')
    Category.objects.create(name=	'Games'	, related_to='0')
    Category.objects.create(name=	'Health/Beauty'	, related_to='0')
    Category.objects.create(name=	'Health/Medical'	, related_to='0')
    Category.objects.create(name=	'Language'	, related_to='0')
    Category.objects.create(name=	'Law/Legal'	, related_to='0')
    Category.objects.create(name=	'Life'	, related_to='0')
    Category.objects.create(name=	'Management'	, related_to='0')
    Category.objects.create(name=	'Media'	, related_to='0')
    Category.objects.create(name=	'Music'	, related_to='0')
    Category.objects.create(name=	'Pets'	, related_to='0')
    Category.objects.create(name=	'Politics'	, related_to='0')
    Category.objects.create(name=	'Religion'	, related_to='0')
    Category.objects.create(name=	'Science'	, related_to='0')
    Category.objects.create(name=	'Shopping'	, related_to='0')
    Category.objects.create(name=	'Sports'	, related_to='0')
    Category.objects.create(name=	'Technology'	, related_to='0')
    
  if not RBACRole.objects.all():
    RBACRole.objects.create(name='public')
    RBACRole.objects.create(name='followers')
    RBACRole.objects.create(name='myself')

    
  if not RBACOperation.objects.all():
    RBACOperation.objects.create(name='display_emailaddress')
    RBACOperation.objects.create(name='display_birthdate')
    RBACOperation.objects.create(name='display_profilepicture')
    RBACOperation.objects.create(name='display_location')
    RBACOperation.objects.create(name='display_website')
    RBACOperation.objects.create(name='display_gender')
    RBACOperation.objects.create(name='add_solution')
    RBACOperation.objects.create(name='add_comment')
    RBACOperation.objects.create(name='register')
    RBACOperation.objects.create(name='view_desk')
    RBACOperation.objects.create(name='post_desk')
    RBACOperation.objects.create(name='view_comment')
    RBACOperation.objects.create(name='edit_solution')
    RBACOperation.objects.create(name='edit_profile')
    RBACOperation.objects.create(name='vote_solution')
    RBACOperation.objects.create(name='follow')

  return 'Done'

