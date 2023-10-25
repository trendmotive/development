# -*- coding: utf-8 -*-

{
    'name' : 'Bulk sms integrations',
    'author': "Trend Motive Solutions (TREMO)",
    'version' : '16.0.1.1',
    'summary' : 'This is a module to allow an api gateway with Ujumbe sms',
    'website':'https://instagram.com/_tremos__?igshid=OGQ5ZDc2ODk2ZA==',
    'description' : """This is a module to allow an api gateway with Ujumbe sms""",
    "license" : "OPL-1",
    'depends' : ['base','phone_validation','mail','sms'],
    'data': ["security/ir.model.access.xml","views/sms_gateway.xml"],
    'qweb' : [],
    'demo': [],
    'installable' : True,
    'auto_install' : False,
    'price': 58,
    'category' : 'Tool',
    'currency': "EUR",
}
