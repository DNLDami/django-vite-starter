import pytest 
from pytest_django.asserts import assertTemplateUsed


class TestHomePage:
          
    def test_template_used(self, client):
        '''Test homepage returns the correct view and template'''
        response = client.get('/')
        
        assertTemplateUsed(response, 'home.html')
        