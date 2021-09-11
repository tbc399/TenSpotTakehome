from rest_framework import permissions


class BookPermissions(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if view.action in ('retrieve', 'list'):
            return request.user.has_perm('library.view_book')
        elif view.action in ('create', 'update'):
            return request.user.has_perms((
                'library.add_book',
                'library.change_book'
            ))
        elif view.action == 'destroy':
            return request.user.has_perm('library.delete_book')
        elif view.action in ('checkout_book', 'return_book'):
            return request.user.has_perms((
                'library.add_checkoutbook',
                'library.add_returnbook',
            ))
        else:
            return False


class AuthorPermissions(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if view.action in ('retrieve', 'list'):
            return request.user.has_perm('library.view_author')
        elif view.action in ('create', 'update'):
            return request.user.has_perms(
                ('library.add_author', 'library.change_author')
            )
        elif view.action == 'destroy':
            return request.user.has_perm('library.delete_author')
        else:
            return False


class GenrePermissions(permissions.BasePermission):
    
    def has_permission(self, request, view):
        
        if view.action == 'list':
            return request.user.has_perm('library.view_genre')
        elif view.action == 'create':
            return request.user.has_perm('library.add_genre')
        elif view.action == 'destroy':
            return request.user.has_perm('library.delete_genre')
        else:
            return False


class UserPermissions(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.has_perm('auth.view_user')
