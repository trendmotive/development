# -*- coding: utf-8 -*-

{
    'name' : 'Invoice Payment Schedule',
    'author': "Trend Motive Solutions (TREMO)",
    'version' : '16.0.1.1',
    'summary' : 'This is a module to allow extension of the payment amount into installments',
    'website':'https://instagram.com/_tremos__?igshid=OGQ5ZDc2ODk2ZA==',
    'description' : """This is a module to allow an api gateway with Ujumbe sms""",
    "license" : "OPL-1",
    'depends' : ['base','account'],
    'data': ["security/ir.model.access.xml","views/invoice_view.xml"],
    'qweb' : [],
    'demo': [],
    'installable' : True,
    'auto_install' : False,
    'price': 58,
    'category' : 'Tool',
    'currency': "EUR",
}
