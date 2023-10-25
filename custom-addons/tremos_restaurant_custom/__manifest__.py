# -*- coding: utf-8 -*-

{
    'name': 'Restaurant Extension',
    'category': 'Generic Modules/Human Resources',
    'version': '16.0.1.0.0',
    'author': 'Odoo SA,Cybrosys Techno Solutions',
    'company': 'Trend Motive Solutions',
    'maintainer': 'Trend Motive Solutions',
    'website': 'https://instagram.com/_tremos__?igshid=OGQ5ZDc2ODk2ZA==',
    'summary': 'Extend the resturant functionalities',
    'description': "",
    'depends': [
        'base',
        'pos_restaurant',
        'hr'
    ],
    'data': ["data/ir_sequence.xml","views/menu_items.xml","views/views.xml"],
    'demo': [],
    'assets': {

        'point_of_sale.assets': [
            'tremos_restaurant_custom/static/src/js/save_order.js',
            'tremos_restaurant_custom/static/src/xml/button.xml',
        ],
    },
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
